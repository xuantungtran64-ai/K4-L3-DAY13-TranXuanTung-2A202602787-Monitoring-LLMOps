import pandas as pd
import matplotlib.pyplot as plt
import json
import os

def load_logs(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    if not data:
        return pd.DataFrame()
        
    df = pd.json_normalize(data)
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.set_index('ts')
    return df

def draw_dashboard(filepath="data/logs.jsonl", output_img="submission/evidence/11-dashboard-overview.png"):
    df = load_logs(filepath)
    if df.empty:
        print("Log file is empty! Please run load_test.py first.")
        return
        
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('K4-L3B Day 13 Monitoring & LLMOps Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Latency percentiles and TTFT (ms) -> p95 <= 3000
    ax = axes[0, 0]
    df_resp = df[df['event'] == 'response_sent'].copy()
    if not df_resp.empty and 'latency_ms' in df_resp.columns:
        latency_p50 = df_resp['latency_ms'].resample('1min').median()
        latency_p95 = df_resp['latency_ms'].resample('1min').quantile(0.95)
        latency_p99 = df_resp['latency_ms'].resample('1min').quantile(0.99)
        ttft_p95 = df_resp['ttft_ms'].resample('1min').quantile(0.95)
        
        ax.plot(latency_p50.index, latency_p50, label='P50 Latency', marker='.')
        ax.plot(latency_p95.index, latency_p95, label='P95 Latency', marker='.')
        ax.plot(latency_p99.index, latency_p99, label='P99 Latency', marker='.')
        ax.plot(ttft_p95.index, ttft_p95, label='P95 TTFT', linestyle='--')
        ax.axhline(y=3000, color='r', linestyle=':', label='Threshold (3000ms)')
    ax.set_title('Latency percentiles and TTFT')
    ax.set_ylabel('ms')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Request traffic (requests_per_minute) -> rate >= 1
    ax = axes[0, 1]
    df_req = df[df['event'] == 'request_received'].copy()
    if not df_req.empty:
        traffic = df_req.resample('1min').size()
        ax.plot(traffic.index, traffic, label='Request Count', marker='o', color='purple')
        ax.axhline(y=1, color='r', linestyle=':', label='Threshold (>=1)')
    ax.set_title('Request traffic')
    ax.set_ylabel('requests/min')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Error rate and retrieval success (%) -> error <= 2
    ax = axes[1, 0]
    df_req_all = df[df['event'].isin(['request_received', 'request_failed'])].copy()
    if not df_req_all.empty:
        total_reqs = df_req_all[df_req_all['event'] == 'request_received'].resample('1min').size()
        failed_reqs = df_req_all[df_req_all['event'] == 'request_failed'].resample('1min').size()
        
        # Align index
        total_reqs, failed_reqs = total_reqs.align(failed_reqs, fill_value=0)
        error_rate = (failed_reqs / total_reqs.replace(0, 1)) * 100
        
        ax.plot(error_rate.index, error_rate, label='Error Rate %', marker='o', color='red')
        ax.axhline(y=2, color='r', linestyle=':', label='Error Threshold (<=2%)')
        
    df_retrieval = df[df['tool_success'].notnull()].copy()
    if not df_retrieval.empty:
        retrieval_success = df_retrieval['tool_success'] == True
        success_rate = retrieval_success.resample('1min').mean() * 100
        ax.plot(success_rate.index, success_rate, label='Retrieval Success %', linestyle='--', color='green', marker='x')
        
    ax.set_title('Error rate and retrieval success')
    ax.set_ylabel('%')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Cost over time (usd) -> total <= 2.5
    ax = axes[1, 1]
    if not df_resp.empty and 'cost_usd' in df_resp.columns:
        cost_sum = df_resp['cost_usd'].resample('1min').sum()
        ax.plot(cost_sum.index, cost_sum, label='Cost per min', color='green', marker='o')
        total_cost = df_resp['cost_usd'].sum()
        ax.text(0.05, 0.9, f"Total Cost: ${total_cost:.4f}", transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    ax.set_title('Cost over time')
    ax.set_ylabel('USD')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 5. Tokens (tokens_in, tokens_out) -> sum <= 50000
    ax = axes[2, 0]
    if not df_resp.empty and 'tokens_in' in df_resp.columns:
        tokens_in = df_resp['tokens_in'].resample('1min').sum()
        tokens_out = df_resp['tokens_out'].resample('1min').sum()
        ax.plot(tokens_in.index, tokens_in, label='Tokens In', marker='.')
        ax.plot(tokens_out.index, tokens_out, label='Tokens Out', marker='.')
        total_tokens = df_resp['tokens_in'].sum() + df_resp['tokens_out'].sum()
        ax.text(0.05, 0.9, f"Total Tokens: {total_tokens}", transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    ax.set_title('Input and output tokens')
    ax.set_ylabel('Tokens')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 6. Quality proxy -> mean >= 0.75
    ax = axes[2, 1]
    if not df_resp.empty and 'quality_score' in df_resp.columns:
        quality_mean = df_resp['quality_score'].resample('1min').mean()
        ax.plot(quality_mean.index, quality_mean, label='Quality Score (Mean)', marker='o', color='orange')
        ax.axhline(y=0.75, color='r', linestyle=':', label='Threshold (>=0.75)')
    ax.set_title('Quality Proxy')
    ax.set_ylabel('Score (0-1)')
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save the figure automatically to evidence folder
    os.makedirs(os.path.dirname(output_img), exist_ok=True)
    plt.savefig(output_img)
    print(f"✅ Dashboard image successfully generated and saved to {output_img}")

if __name__ == "__main__":
    draw_dashboard()


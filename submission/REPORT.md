# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Trần Xuân Tùng
- **MSSV:** 2A202601787
- **Lớp:** K4-L3B
- **Repository URL:**
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-<MSSV>`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | [01-pytest.png](evidence/01-pytest.png) |
| Log validator | [02-log-validator.png](evidence/02-log-validator.png) |
| Dashboard validator | [03-dashboard-validator.png](evidence/03-dashboard-validator.png) |
| Structured log | [04-structured-log.png](evidence/04-structured-log.png) |
| PII redaction | [05-pii-redaction.png](evidence/05-pii-redaction.png) |
| Trace list | [06-trace-list.png](evidence/06-trace-list.png) |
| Trace waterfall | [07-trace-waterfall.png](evidence/07-trace-waterfall.png) |
| Trace metadata | [08-trace-metadata.png](evidence/08-trace-metadata.png) |
| Prompt versions | [09-prompt-versions.png](evidence/09-prompt-versions.png) |
| Prompt rollback | [10-prompt-rollback.png](evidence/10-prompt-rollback.png) |
| Dashboard runtime | [11-dashboard-overview.png](evidence/11-dashboard-overview.png) |
| Incident metric | [12-incident-metric.png](evidence/12-incident-metric.png) |
| Incident log | [13-incident-log.png](evidence/13-incident-log.png) |
| Incident trace | [14-incident-trace.png](evidence/14-incident-trace.png) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 (3 FAILED, 1 PASSED) | | |
| `validate_dashboard.py` | Hợp lệ 6/6 panel | | |
| `pytest` | [200] OK nhưng thiếu correlation ID (MISSING) | | |
| Số traces hợp lệ | 0 unique correlation IDs | | |
| Số PII leak | 0 | | |
| Latency P95 / TTFT P95 | Chưa có số liệu chuẩn | | |
| Retrieval success rate | Chưa có số liệu | | |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
- **Các metadata được ghi vào structured log:**
- **Cách bảo đảm PII được scrub trước khi ghi:**
- **Cách kiểm chứng kết quả:**

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Trace được tạo trong project có chứa tên prj (day13-k4-l3b-2A202601787), có thể đối chiếu qua ảnh chụp evidence 06-trace-list.png.
- **Cấu trúc root/retrieval/generation observations:** Trace có root là day13-agent-request bao bọc bên ngoài. Bên trong là span agent lab-agent-run, chứa 2 span con tuần tự là retrieval (cho RAG) và generation (gọi mô hình)
- **Cách nối trace với log:** Thông qua correlation_id được sinh ra ở log request. ID này được truyền vào metadata của trace qua propagate_attributes
- **Prompt name:** day13-chat
- **Version/label baseline:** V 1, label: baseline, production
- **Version/label candidate:** V 2, label: candidate
- **Trace ID của mỗi version:** v1: a50176495f76f43ad76b9adba5fec935 , v2:8d8234d5db630302d01692bbc09d359a
- **Cách promote và rollback production:** Để Promote, đổi label production sang V2 trên Langfuse UI. Để rollback, xóa ở V2 và đổi nhãn production quay ngược về V1. App sẽ tự động fetch prompt mới vì luôn lấy theo LANGFUSE_PROMPT_LABEL=production

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Gồm 6 panel phân tích data/logs.jsonl (latency, traffic, errors, cost, tokens, quality). Mỗi panel có đường threshold giám sát trực quan các chỉ số SLI
- **SLO và lý do chọn:** Chọn SLO 99.5% cho mục tiêu "fast successful requests" (latency <= 3000ms và không gặp lỗi). Lý do: mức 99.5% là hợp lý cho một trợ lý AI nội bộ, cho phép hệ thống có một lượng error budget nhỏ để cập nhật prompt mới mà không ảnh hưởng nghiêm trọng tới trải nghiệm
- **Cách tính error budget:** SLO 99.5% trong 28 ngày nghĩa là error budget là 0.5%. Giả sử workload có 14.000 request/28 ngày thì tối đa 70 request được phép lỗi hoặc trả về quá chậm (>3000ms)
- **Ba alert và runbook tương ứng:**
  1. HighLatencyP95: báo động khi P95 latency > 3000ms liên tục 5 phút
  2. HighErrorRate: báo động khi Error Rate > 2% liên tục 3 phút
  3. LowRetrievalSuccess: báo động khi Retrieval Success < 90% liên tục 10 phút
  (runbook chi tiết các bước xử lý nằm tại docs/alerts.md)


## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.

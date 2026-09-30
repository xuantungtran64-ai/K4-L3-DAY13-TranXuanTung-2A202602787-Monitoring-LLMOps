# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `high`
- Duration: `5m`
- Kênh thông báo: Slack `#alerts-llm`
- SLI/SLO liên quan: `p95(latency_ms)`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ quá lâu để nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Xem Dashboard Latency để biết thời điểm bắt đầu chậm.
  2. Lọc log `data/logs.jsonl` tìm các request có `latency_ms` > 3000ms để lấy `correlation_id`.
  3. Dùng `correlation_id` tra trên Langfuse để xem span nào (retrieval hay generation) bị chậm.
- Mitigation tạm thời: Rollback version prompt nếu do prompt mới dài hơn. Khởi động lại service nếu do tài nguyên.
- Owner: `oncall-team`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `3m`
- Kênh thông báo: Slack `#alerts-llm`
- SLI/SLO liên quan: Tỉ lệ lỗi tổng (Error Rate)
- Điều kiện và thời gian duy trì: `error_rate > 2%` trong 3 phút
- Ảnh hưởng tới người dùng: Người dùng nhận được thông báo lỗi thay vì câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Xem Dashboard Errors để xác nhận loại lỗi (`error_type`).
  2. Tìm các dòng log `request_failed` trong `logs.jsonl` để lấy `correlation_id`.
  3. Kiểm tra Trace trên Langfuse để xem lỗi phát sinh từ bước nào (gọi RAG hay LLM).
- Mitigation tạm thời: Rollback cấu hình hoặc restart ứng dụng nếu bị kẹt (deadlock). Tắt tính năng mới nếu gây lỗi diện rộng.
- Owner: `oncall-team`

## Alert 3

- Tên: `LowRetrievalSuccess`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#alerts-search`
- SLI/SLO liên quan: Tỉ lệ `tool_success` của retrieval
- Điều kiện và thời gian duy trì: `retrieval_success < 90%` trong 10 phút
- Ảnh hưởng tới người dùng: Câu trả lời bị giảm chất lượng hoặc LLM trả lời hallucinate do không có ngữ cảnh từ tài liệu.
- Ba bước kiểm tra đầu tiên:
  1. Mở Dashboard Errors xem biểu đồ Retrieval Success Rate.
  2. Lọc log có `tool_success=false` để lấy `correlation_id`.
  3. Tra cứu trên Langfuse xem input query là gì và tại sao hệ thống vector store lại fail.
- Mitigation tạm thời: Khởi động lại dịch vụ vector search (Mock RAG) hoặc tạm thời chuyển về cấu hình fallback.
- Owner: `search-team`

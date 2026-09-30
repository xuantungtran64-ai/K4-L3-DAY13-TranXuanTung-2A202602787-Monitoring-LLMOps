# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Chỉ cần 3 output text và 5 ảnh runtime; dùng đường dẫn tương đối, ví dụ `evidence/03-incident-trace.png`.

## 1. Thông tin học viên

- **Họ và tên:** Trần Xuân Tùng
- **MSSV:** 2A202601787
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/xuantungtran64-ai/K4-L3-DAY13-TranXuanTung-2A202602787-Monitoring-LLMOps/tree/main
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A2026-2787`

## 2. Evidence index

Giữ đúng ba output text và năm ảnh dưới đây. Không tách thêm ảnh; nếu cần giải thích, ghi bằng chữ trong các mục sau.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/pytest.txt` |
| Log validator | `evidence/log-validator.txt` |
| Dashboard validator | `evidence/dashboard-validator.txt` |
| Structured log + incident log | `evidence/01-incident-log.png` |
| Trace list | `evidence/02-trace-list.png` |
| Trace waterfall + metadata + incident trace | `evidence/03-incident-trace.png` |
| Prompt versions + promote/rollback | `evidence/04-prompt-versioning.png` |
| Dashboard + incident metric | `evidence/05-dashboard-incident.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 (3 FAILED, 1 PASSED) | 100/100 (4 PASSED) | pass toàn bộ tiêu chí |
| `validate_dashboard.py` | Hợp lệ 6/6 panel | Hợp lệ 6/6 panel | dashboard đủ 6 panel |
| `pytest` | [200] OK nhưng thiếu correlation ID (MISSING) | 24/24 passed | pass toàn bộ test case |
| Số traces hợp lệ | 0 unique correlation IDs | 16 unique correlation IDs | request thành công đều được gán id |
| Số PII leak | 0 | 0 | dữ liệu nhạy cảm đã được loại bỏ |
| Latency P95 / TTFT P95 | Chưa có số liệu chuẩn | 2873.1 ms / 50.6 ms | nằm trong ngưỡng slo |
| Retrieval success rate | Chưa có số liệu | 100% | truy vấn cơ sở dữ liệu ổn định |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** middleware đọc header request hoặc tạo chuỗi ngẫu nhiên mới rồi gán vào structlog để các log sau tự động nhận diện
- **Các metadata được ghi vào structured log:** ghi thêm user_hash, session_id, feature, model, env vào log thông qua bind_contextvars trong endpoint
- **Cách bảo đảm PII được scrub trước khi ghi:** cấu hình processor gọi hàm scrub_event để quét và thay thế email số điện thoại cccd thẻ tín dụng theo regex
- **Cách kiểm chứng kết quả:** chạy tập lệnh validate_logs để kiểm tra file đầu ra đảm bảo không sót dữ liệu nhạy cảm

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

- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1
- **Khoảng thời gian điều tra:**  11:55 ngày 30/09/2026
- **Triệu chứng từ metrics:** Latency đo được tại góc nhìn người dùng tăng vọt lên đến 8-13 giây do tắc nghẽn rq. Latency thực tế ở phía backend cho mỗi rq vượt qua 2500ms (vượt quá ngưỡng cho phép 2000ms)
- **Log line và correlation ID liên quan:** Request bị ảnh hưởng có correlation_id là `req-b6fc58a1`. Dòng log ghi nhận `"latency_ms": 2652`, chứng tỏ request này bị kẹt rất lâu
- **Trace ID và span gây ảnh hưởng:** Trace ID `7938ccb993a5263b0423d9b37f3bfeab` (của request `req-b6fc58a1`). Span bị chậm là `retrieval` chiếm 2.50s (trong tổng số 2.65s của cả trace)
- **Root cause:** Lỗi do logic truy xuất cơ sở dữ liệu RAG (bước `retrieval`) bị chậm bất thường, gây nghẽn toàn bộ luồng xử lý của Agent
- **Fix action:** Tối ưu hóa lại truy vấn RAG, kiểm tra trạng thái của Vector Database
- **Preventive measure:** Bổ sung alert cảnh báo ngay khi P95 Latency vượt 2000ms. Thiết lập timeout hợp lý cho bước `retrieval` để không làm treo toàn bộ ứng dụng khi DB bị chậm.


## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** sử dụng processor để xử lý log tập trung cho việc xoá pii và format jsonl giúp giảm code thừa ở các hàm xử lý
- **Một lỗi/blocker đã gặp:** import lỗi khi chạy test do thiếu đường dẫn
- **Cách tìm nguyên nhân và xử lý:** Đọc thông báo lỗi và thêm biến môi trường vào trước lệnh test để ứng dụng nhận diện được đường dẫn
- **Cách hiểu luồng Metrics → Logs → Traces:** metrics báo hiệu biến động tổng quan logs giúp khoanh vùng thời điểm và traces soi chi tiết từng bước bên trong request để bắt đúng hàm gây nghẽn
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** giám sát cost tối ưu ngân sách còn slo định lượng rủi ro cho phép hệ thống có cơ chế rollback phục hồi nhanh khi prompt mới gặp sự cố
- **Điều quan trọng nhất đã học:** cách kết hợp các công cụ observability để giám sát vòng đời một ứng dụng ai
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** chưa bắt hết các định dạng dữ liệu nhạy cảm phức tạp

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Có đúng 3 file text và 5 ảnh runtime theo hướng dẫn.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.


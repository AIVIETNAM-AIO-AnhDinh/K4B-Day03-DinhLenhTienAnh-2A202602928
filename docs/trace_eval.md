# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Đinh Lệnh Tiến Anh  
> **Mã Sinh Viên / Mã Học viên:** 2A202602928  
> **Chủ đề Lựa chọn:** Gợi ý 1.1 — *Trợ lý Học vụ & Tra cứu Lịch thi VinUni* (tra cứu điểm GPA, lịch thi và đặt lịch tư vấn học vụ với Cố vấn)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | **5** / 5 | Yêu cầu điển hình *"Đặt lịch tư vấn cho SV2026001 với cố vấn học tập của em ấy vào 14:00 ngày 15/09/2026"* **không thể** giải trong một bước: Agent bắt buộc phải (1) gọi `academic_query` để biết `advisor` của sinh viên, rồi (2) lấy giá trị đó làm tham số `advisor_name` cho `schedule_appointment`. Đây là chuỗi suy luận nối tiếp có ràng buộc dữ liệu (data dependency), đúng bản chất ReAct đa bước. |
| **2. Tool Interaction** | **5** / 5 | Bài toán cần đủ **2 nhóm công cụ** theo yêu cầu đề bài: 1 công cụ **tra cứu** (`academic_query` → truy vấn hồ sơ học vụ/GPA/lịch thi) và 1 công cụ **hành động ghi dữ liệu** (`schedule_appointment` → tạo booking, trả về `booking_id`). Cả hai được expose qua **MCP Server** (`src/mcp_server.py`) bằng Native Tool Calling chuẩn JSON Schema. LLM thuần không thể tự bịa GPA hay tạo lịch hẹn, nên tương tác công cụ là bắt buộc chứ không phải tùy chọn. |
| **3. Dynamic Decision** | **5** / 5 | Bước kế tiếp phụ thuộc hoàn toàn vào `observation` trả về: nếu `status = SUCCESS` thì Agent trích `advisor` để đặt lịch tiếp; nếu `status = NOT_FOUND` thì Agent phải **dừng nhánh đặt lịch**, không được bịa dữ liệu, và hỏi lại người dùng. Ngoài ra Agent còn phải tự phân luồng. Đây là quyết định động thực sự tại runtime. |
| **4. Long Horizon Goal** | **4** / 5 | Agent phải giữ mục tiêu "đặt lịch tư vấn" xuyên suốt nhiều lượt Thought → Action → Observation, đồng thời mang theo **ngữ cảnh tích lũy** (`student_id`, `advisor`, `datetime_str`) qua các lượt gọi tool mà không để thất lạc. Chưa chấm 5/5 vì tầm nhìn (horizon) của bài toán chỉ kéo dài khoảng **2–3 bước trong một phiên hội thoại**, không có trạng thái bền vững (persistent state) qua nhiều ngày hay tiến trình chờ phê duyệt dài hạn như các bài toán workflow doanh nghiệp. |
| **TỔNG ĐIỂM AGENTIC FIT** | **19 / 20** | *Tổng 19/20 > 12/20 → **Bài toán rất phù hợp triển khai Agentic System (ReAct Agent + MCP), không nên dùng LLM Chatbot Baseline.*** |

**🧭 Kết luận đánh giá:** Chủ đề 1.1 vượt ngưỡng Agentic Fit ở cả 3 tiêu chí lõi (Multi-step, Tool Interaction, Dynamic Decision). Chatbot Baseline sẽ thất bại vì không có khả năng lấy tên cố vấn từ cơ sở dữ liệu trước khi đặt lịch, và có nguy cơ **hallucinate** GPA/lịch hẹn. Do đó, kiến trúc **ReAct Agent + Native Tool Calling qua MCP Server** là lựa chọn kỹ thuật đúng đắn cho bài toán này.

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "em học sinh giỏi văn nhưng nhà nghèo thì nên chọn chương trình nào",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Chào em, \n\nĐại học VinUni là một trường đại học xuất sắc, đào tạo chủ yếu theo chuẩn quốc tế về Kinh doanh, Kỹ thuật - Khoa học Máy tính, Khoa học Sức khỏe và Nghệ thuật - Khoa học Xã hội (chương trình Cử nhân Quản trị Khách sạn, v.v.). Mặc dù học phí tại VinUni thuộc phân khúc cao do chất lượng giáo dục đạt chuẩn quốc tế, nhưng nhà trường có **rất nhiều chính sách hỗ trợ tài chính, học bổng toàn phần và bán phần** dành cho các bạn sinh viên có năng lực học tập xuất sắc nhưng có hoàn cảnh khó khăn (nhà nghèo).\n\nNếu em có thế mạnh về Văn học (tư duy ngôn ngữ, khả năng phân tích, diễn đạt, viết luận tốt) và điều kiện kinh tế gia đình còn hạn chế, em có thể cân nhắc các hướng đi sau tại VinUni:\n\n1. **Các ngành học phù hợp với thế mạnh văn học và tư duy xã hội:**\n   * **Cử nhân Quản trị Khách sạn (Hospitality Management):** Ngành này đòi hỏi kỹ năng giao tiếp xuất sắc, sự thấu cảm, hiểu biết sâu sắc về văn hóa, tâm lý con người và khả năng ngoại ngữ/diễn đạt tốt (những kỹ năng mà một học sinh giỏi Văn thường rất có lợi thế).\n   * **Các chương trình học bổng và xét tuyển toàn diện:** VinUni xét tuyển dựa trên hồ sơ toàn diện (Comprehensive Review), không chỉ nhìn vào điểm số một môn mà đánh giá tiềm năng lãnh đạo, sự sáng tạo, tư duy phản biện và đam mê của em. Khả năng viết luận cá nhân xuất sắc của một học sinh giỏi Văn sẽ là **lợi thế cực kỳ lớn** khi em làm hồ sơ nộp đơn vào VinUni.\n\n2. **Chính sách Hỗ trợ Tài chính & Học bổng tại VinUni:**\n   * **Học bổng Tài năng (Merit-based Scholarships):** Dành cho những học sinh có thành tích học tập và hoạt động ngoại khóa xuất sắc (có thể bao gồm 100% học phí và sinh hoạt phí).\n   * **Hỗ trợ tài chính dựa trên hoàn cảnh (Need-based Financial Aid):** VinUni cam kết tạo cơ hội cho mọi học sinh tài năng đều có thể theo học bất kể hoàn cảnh kinh tế. Trường có các gói hỗ trợ tài chính (giảm học phí từ 50% đến 80% hoặc hơn) dành cho sinh viên có hoàn cảnh khó khăn nhưng chứng minh được năng lực học tập xuất sắc.\n   * **Chính sách trả góp học phí / Hợp tác tín dụng giáo dục:** Giúp giảm áp lực tài chính từng kỳ cho gia đình.\n\nNếu em muốn tìm hiểu chi tiết hơn về các ngành học cụ thể hoặc các chương trình hỗ trợ tài chính/học bổng đang áp dụng cho năm tuyển sinh hiện tại, em có thể cho thầy/cô biết thêm thông tin hoặc đặt lịch gặp Cố vấn tuyển sinh để được tư vấn cụ thể nhé!",
    "latency_ms": 3602.39
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** _7_ / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** __10_ lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!

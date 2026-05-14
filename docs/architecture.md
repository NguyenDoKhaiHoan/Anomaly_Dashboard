# Kiến trúc đề xuất cho Project2

## Mục tiêu
Biến dashboard 1 dataset ban đầu thành web app thực thụ gồm:
- **Admin portal**: quản lý user, model, dataset, giám sát hệ thống.
- **User portal**: đăng nhập, tạo stream session, xem lịch sử, nhận cảnh báo.
- **Model layer**: chỉ dùng 2 model đã train: statistical fraud và IoT LSTM.
- **Database**: MySQL lưu user, sessions, anomaly events, alert rules, notifications.

## Dòng chảy dữ liệu
1. Frontend gửi yêu cầu tạo session.
2. Backend tạo `stream_session` cho user.
3. `session_manager` đọc sample CSV hoặc nguồn dữ liệu thật.
4. Detector tương ứng xử lý event và tính anomaly score.
5. Event được lưu vào MySQL.
6. Event realtime được đẩy về UI qua SSE/WebSocket.
7. Alert rules tạo notification nếu score vượt ngưỡng.

## Vai trò
### User
- đăng ký, đăng nhập
- tạo / chạy / dừng stream
- xem lịch sử anomaly cá nhân
- xem cảnh báo cá nhân
- theo dõi model monitor cơ bản

### Admin
- xem danh sách user
- khóa / mở user
- gán quyền admin
- xem tổng quan models, datasets, active sessions
- seed dữ liệu và giám sát health

## Vì sao giữ thư mục `legacy/`
`legacy/original_project2/` là ảnh chụp mã gốc của đồ án ban đầu để:
- đối chiếu code cũ với code mới
- chứng minh bản refactor đi lên từ Project2 cũ
- hỗ trợ viết báo cáo phần tiến hóa kiến trúc

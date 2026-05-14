# 🚨 Real-time Streaming Anomaly Detection Dashboard

> Hệ thống phát hiện bất thường theo thời gian thực cho dữ liệu giao dịch tài chính và dữ liệu cảm biến IoT.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Vite](https://img.shields.io/badge/Vite-Frontend-purple)
![Machine Learning](https://img.shields.io/badge/ML-Anomaly%20Detection-red)

---

## 📌 Giới thiệu

**Real-time Streaming Anomaly Detection Dashboard** là hệ thống mô phỏng quá trình phát hiện bất thường trong dữ liệu dạng stream.

Hệ thống hỗ trợ hai nhóm dữ liệu chính:

- 💳 **Credit Card Transactions**: phát hiện giao dịch thẻ tín dụng bất thường.
- 🌡️ **IoT Sensor Data**: phát hiện bất thường trong dữ liệu cảm biến IoT.

Người dùng có thể tạo phiên stream, theo dõi dữ liệu theo thời gian thực, xem điểm bất thường, nhận cảnh báo, quản lý lịch sử anomaly và cấu hình ngưỡng phát hiện thông qua giao diện dashboard.

---

## 🎯 Mục tiêu hệ thống

Trong thực tế, dữ liệu từ giao dịch tài chính, cảm biến IoT hoặc hệ thống giám sát thường được sinh ra liên tục theo thời gian. Vì vậy, việc phát hiện bất thường cần được xử lý nhanh để hỗ trợ cảnh báo sớm.

Hệ thống này được xây dựng nhằm:

- Mô phỏng dữ liệu stream từ file CSV.
- Tiền xử lý dữ liệu trước khi đưa vào mô hình.
- Phát hiện anomaly bằng các phương pháp Machine Learning.
- Hiển thị kết quả realtime trên dashboard.
- Lưu lịch sử anomaly vào database.
- Cấu hình cảnh báo khi anomaly score vượt ngưỡng.
- Quản lý user, model, dataset và stream session.

---

## 🛠️ Công nghệ sử dụng

### Backend

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **MySQL**
- **JWT Authentication**
- **Server-Sent Events**
- **WebSocket**
- **PyTorch**
- **Scikit-learn**
- **Pandas / NumPy**

### Frontend

- **Vite**
- **JavaScript**
- **HTML / CSS**
- **Realtime Dashboard**
- **REST API**
- **EventSource / WebSocket**

### Machine Learning

- **Statistical Anomaly Detection**
- **Z-score**
- **EMA**
- **Sliding Window**
- **LSTM Sequence Classifier**

---

## 📂 Cấu trúc thư mục

```txt
Project2/
│
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/routes/        # API routers
│   │   │   ├── core/                 # Config, database, security
│   │   │   ├── db_models/            # SQLAlchemy models
│   │   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── services/             # Business logic
│   │   │   ├── utils/                # Helper functions
│   │   │   └── main.py               # FastAPI entrypoint
│   │   │
│   │   ├── requirements.txt
│   │   └── tests/
│   │
│   └── web/
│       ├── src/
│       │   ├── pages/                # Frontend pages
│       │   ├── services/             # API services
│       │   ├── router/               # Frontend router
│       │   ├── state/                # Auth state
│       │   └── utils/
│       │
│       ├── package.json
│       └── vite.config.js
│
├── configs/                          # Local config examples
├── data/
│   ├── raw/                          # Raw datasets
│   └── samples/                      # Sample datasets
│
├── database/
│   └── init_mysql.sql                # MySQL init script
│                        
├── models/                           # Model metadata / registry
├── notebooks/
│   ├── colab/                        # Colab inference server
│   └── experiments/                  # Training notebooks
│
├── scripts/                          # Helper scripts
├── .env.example
├── .gitignore
└── README.md
```

---

## ✨ Chức năng chính

### 🔐 Authentication

Người dùng có thể đăng ký, đăng nhập và truy cập hệ thống thông qua JWT token.

API chính:

```txt
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

---

### 📡 Streaming Dashboard

Người dùng có thể tạo phiên stream realtime với các thông tin:

- Stream type
- Dataset
- Model
- Interval
- Threshold override

Trong quá trình stream, hệ thống sẽ liên tục đọc dữ liệu, xử lý, dự đoán anomaly và gửi kết quả realtime về frontend.

API chính:

```txt
GET    /api/v1/streams/sessions
POST   /api/v1/streams/sessions
POST   /api/v1/streams/sessions/{id}/start
POST   /api/v1/streams/sessions/{id}/stop
PATCH  /api/v1/streams/sessions/{id}
GET    /api/v1/streams/sessions/{id}/events
```

---

### 💳 Credit Card Anomaly Detection

Đối với dữ liệu giao dịch thẻ tín dụng, hệ thống sử dụng phương pháp thống kê.

Các đặc trưng chính:

- `amt`
- `distance`
- `city_pop`
- `ema_diff`

Các kỹ thuật sử dụng:

- Rolling mean
- Rolling standard deviation
- Z-score
- EMA
- Weighted anomaly score

Nếu anomaly score vượt qua threshold, giao dịch sẽ được đánh dấu là bất thường.

---

### 🌡️ IoT Sensor Anomaly Detection

Đối với dữ liệu cảm biến IoT, hệ thống sử dụng mô hình LSTM Sequence Classifier.

Các đặc trưng chính:

- `Temperature`
- `Humidity`
- `Battery_Level`

Quy trình xử lý:

1. Nhận dữ liệu cảm biến.
2. Lưu dữ liệu vào sequence buffer.
3. Chờ đủ sliding window.
4. Scale dữ liệu.
5. Đưa chuỗi dữ liệu vào LSTM.
6. Tính xác suất anomaly.
7. So sánh với threshold để phân loại.

---

### 📜 History Management

Người dùng có thể xem lại lịch sử anomaly event đã được xử lý.

Chức năng gồm:

- Xem danh sách anomaly event.
- Lọc theo stream type.
- Lọc theo thời gian.
- Lọc theo session.
- Xem chi tiết raw payload và feature payload.
- Export lịch sử ra CSV.

API chính:

```txt
GET /api/v1/history/events
GET /api/v1/history/events/export
```

---

### 🔔 Alert System

Người dùng có thể tạo rule cảnh báo dựa trên anomaly score.

Một alert rule gồm:

- Tên rule
- Stream type
- Score threshold
- Consecutive count
- Channel cảnh báo
- Trạng thái bật/tắt

Khi anomaly event thỏa điều kiện rule, hệ thống sẽ tạo notification.

API chính:

```txt
GET    /api/v1/alerts/rules
POST   /api/v1/alerts/rules
DELETE /api/v1/alerts/rules/{id}

GET    /api/v1/alerts/notifications
POST   /api/v1/alerts/notifications/{id}/read
DELETE /api/v1/alerts/notifications/{id}
```

---

### 📊 Model Monitor

Trang Model Monitor dùng để theo dõi trạng thái hệ thống:

- Backend health status
- Model đã được load
- Số session đang chạy
- Runtime status
- Thông tin detector registry

API chính:

```txt
GET /api/v1/health
```

---

### 👤 Admin Dashboard

Admin có thể quản lý hệ thống thông qua các chức năng:

- Xem danh sách user.
- Khóa hoặc mở khóa user.
- Cấp hoặc gỡ quyền admin.
- Xem thống kê tổng quan hệ thống.
- Theo dõi model registry và dataset registry.

API chính:

```txt
GET   /api/v1/admin/users
PATCH /api/v1/admin/users/{id}
GET   /api/v1/admin/overview
```

---

## 🗄️ Database

Hệ thống sử dụng **MySQL** để lưu dữ liệu.

Các bảng chính:

| Bảng | Chức năng |
|---|---|
| `users` | Lưu thông tin tài khoản |
| `stream_sessions` | Lưu phiên stream |
| `anomaly_events` | Lưu kết quả phát hiện anomaly |
| `alert_rules` | Lưu rule cảnh báo |
| `alert_notifications` | Lưu thông báo cảnh báo |
| `model_registry` | Lưu danh sách model |
| `dataset_registry` | Lưu danh sách dataset |
| `assets` | Lưu thông tin asset mở rộng |


## 🚀 Cài đặt và chạy hệ thống

### 1. Clone project

```bash
git clone https://github.com/NguyenDoKhaiHoan/Anomaly_Dashboard.git
cd Anomaly_Dashboard
```

---

### 2. Cài đặt backend

```bash
cd apps/backend
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows:

```bash
.venv\Scripts\activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

---

### 3. Cấu hình môi trường

Tạo file `.env` từ file mẫu:

```bash
copy .env.example .env
```

Ví dụ cấu hình:

```env
APP_NAME=Streaming Anomaly Detection Dashboard
ENV=local

DATABASE_URL=mysql+pymysql://root:password@localhost:3306/anomaly_dashboard

SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

BACKEND_CORS_ORIGINS=http://localhost:5173
```


---

### 4. Khởi tạo MySQL

Tạo database:

```sql
CREATE DATABASE anomaly_dashboard
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Hoặc chạy file:

```txt
database/init_mysql.sql
```

---

### 5. Chạy backend

Từ thư mục `apps/backend`:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend chạy tại:

```txt
http://localhost:8000
```

Swagger API docs:

```txt
http://localhost:8000/docs
```

---

### 6. Cài đặt frontend

Mở terminal mới:

```bash
cd apps/web
npm install
```

Chạy frontend:

```bash
npm run dev
```

Frontend chạy tại:

```txt
http://localhost:5173
```
---

## 🔑 Tài khoản demo

Sau khi seed dữ liệu, có thể sử dụng tài khoản demo:

```txt
Username: demo
Password: demo123
```


---

## 🤖 Model sử dụng

### Fraud Statistical Detector

Model phát hiện bất thường giao dịch dựa trên phương pháp thống kê.

Feature chính:

```txt
amt
distance
city_pop
ema_diff
```

Kỹ thuật sử dụng:

```txt
Z-score
EMA
Rolling Window
Weighted Score
Threshold Classification
```

---

### IoT LSTM Detector

Model phát hiện bất thường IoT dựa trên chuỗi thời gian.

Feature chính:

```txt
Temperature
Humidity
Battery_Level
```

Kỹ thuật sử dụng:

```txt
Sliding Window
Feature Scaling
LSTM
Sigmoid Probability
Threshold Classification
```

---

## ☁️ Colab Inference Server

Hệ thống có notebook triển khai FastAPI inference server trên Google Colab.

Đường dẫn:

```txt
notebooks/colab/server.ipynb
```

Các endpoint chính:

```txt
GET  /health
GET  /models
POST /predict/fraud
POST /predict/iot
POST /sessions/reset/{session_id}
```

Colab server phù hợp khi muốn thử nghiệm inference trên môi trường cloud hoặc GPU.

---

## 📦 Dataset

Hệ thống sử dụng dữ liệu mẫu để mô phỏng stream.

Các file sample nhỏ nên đặt tại:

```txt
data/samples/
```

Các file raw dataset lớn nên đặt tại:

```txt
data/raw/
```

Do giới hạn dung lượng GitHub, không nên commit các file CSV lớn.

---

## 🚫 Các file không nên commit

Các file sau không nên đưa lên GitHub:

```txt
.env
.venv/
node_modules/
dist/
build/
__pycache__/
.ipynb_checkpoints/

data/raw/**/*.csv

*.pkl
*.pt
*.pth
*.joblib
*.h5
```

Nếu cần lưu file lớn, có thể sử dụng:

- Git LFS
- Google Drive
- Kaggle Dataset
- Cloud Storage
- Link tải trong README

---

## ⚠️ Hạn chế hiện tại

Một số hạn chế của phiên bản hiện tại:

- Dữ liệu stream chủ yếu được giả lập từ file CSV.
- Chưa kết nối trực tiếp với nguồn dữ liệu realtime thật.
- Colab inference server chưa tích hợp hoàn toàn với backend local.
- Alert SMS hiện chủ yếu là mock/log.
- Upload dataset từ giao diện chưa hoàn thiện.
- Cần tối ưu thêm mô hình để giảm false positive và false negative.
- Dataset lớn chưa được quản lý bằng cloud storage hoặc Git LFS.

---

## 🔮 Hướng phát triển

Trong tương lai, hệ thống có thể được mở rộng theo các hướng:

- Tích hợp nguồn dữ liệu realtime thật.
- Cho phép upload dataset trực tiếp từ giao diện.
- Tích hợp backend local với Colab inference server.
- Bổ sung drift detection.
- Cải thiện chất lượng mô hình phát hiện bất thường.
- Tối ưu latency cho realtime stream.
- Tích hợp email/SMS/push notification thật.
- Thêm dashboard thống kê nâng cao.
- Hỗ trợ nhiều người dùng chạy stream đồng thời.

---

## 📚 Ý nghĩa học thuật

Project tập trung vào các chủ đề:

- Real-time data streaming
- Anomaly detection
- Online monitoring
- Sliding window processing
- Threshold tuning
- False positive management
- Machine Learning deployment
- Backend API design
- Dashboard visualization
- Alert management system

---

## 👨‍💻 Tác giả

Project được xây dựng phục vụ mục đích học tập, nghiên cứu và thực hành triển khai hệ thống phát hiện bất thường theo thời gian thực.

**Author:** NguyenDoKhaiHoan  
**Repository:** `Anomaly_Dashboard`

---

## ⭐ Ghi chú

Nếu project hữu ích, hãy star repository để đánh dấu và tiếp tục phát triển thêm các chức năng mới.

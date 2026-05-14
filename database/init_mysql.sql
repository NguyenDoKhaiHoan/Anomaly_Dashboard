CREATE DATABASE IF NOT EXISTS anomaly_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'anomaly_user'@'localhost' IDENTIFIED BY 'anomaly_pass';
GRANT ALL PRIVILEGES ON anomaly_dashboard.* TO 'anomaly_user'@'localhost';
FLUSH PRIVILEGES;

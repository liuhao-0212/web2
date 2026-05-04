-- Optional: create database and user for local dev (run as MySQL admin).
CREATE DATABASE IF NOT EXISTS webapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'webapp'@'%' IDENTIFIED BY 'webapp_secret';
GRANT ALL PRIVILEGES ON webapp_db.* TO 'webapp'@'%';
FLUSH PRIVILEGES;

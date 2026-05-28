-- SmartAttend Database Schema
-- Run: mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS smartattend_db;
USE smartattend_db;

CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  roll_number VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  code VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT REFERENCES subjects(id),
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ended_at TIMESTAMP NULL
);

CREATE TABLE enrollments (
  student_id INT REFERENCES students(id),
  subject_id INT REFERENCES subjects(id),
  PRIMARY KEY (student_id, subject_id)
);

CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id INT REFERENCES sessions(id),
  student_id INT REFERENCES students(id),
  marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  method VARCHAR(20) DEFAULT 'face_recognition'
);
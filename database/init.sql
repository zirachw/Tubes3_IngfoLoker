CREATE DATABASE IF NOT EXISTS ingfoloker;
USE ingfoloker;

-- Create ApplicantProfile table
CREATE TABLE IF NOT EXISTS ApplicantProfile (
    applicant_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL COMMENT 'Encrypted field',
    last_name VARCHAR(50) NOT NULL COMMENT 'Encrypted field',
    date_of_birth VARCHAR(10) DEFAULT NULL COMMENT 'Encrypted field',
    address VARCHAR(255) DEFAULT NULL COMMENT 'Encrypted field',
    phone_number VARCHAR(20) DEFAULT NULL COMMENT 'Encrypted field',
    INDEX idx_applicant_name (first_name, last_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create ApplicationDetail table
CREATE TABLE IF NOT EXISTS ApplicationDetail (
    detail_id INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id INT NOT NULL,
    application_role VARCHAR(100) DEFAULT NULL,
    cv_path TEXT NOT NULL,
    CONSTRAINT `FK1` FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_application_role (application_role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
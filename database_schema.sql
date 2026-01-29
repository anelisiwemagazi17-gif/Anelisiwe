-- Database schema for SOR Dashboard
-- Run this in your MySQL database

-- Table to track SOR generation requests
CREATE TABLE IF NOT EXISTS sor_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id INT NOT NULL,
    learner_name VARCHAR(255) NOT NULL,
    learner_email VARCHAR(255),
    status ENUM('pending', 'pdf_generated', 'signature_sent', 'signed', 'uploaded', 'failed') DEFAULT 'pending',
    pdf_path VARCHAR(500),
    signed_pdf_path VARCHAR(500),
    signature_request_id VARCHAR(255),
    assignment_id INT,
    overall_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    signature_sent_at TIMESTAMP NULL,
    signed_at TIMESTAMP NULL,
    uploaded_at TIMESTAMP NULL,
    error_message TEXT,
    INDEX idx_learner_id (learner_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for audit logging
CREATE TABLE IF NOT EXISTS sor_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sor_request_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    status ENUM('success', 'error', 'warning') DEFAULT 'success',
    user VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sor_request_id (sor_request_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (sor_request_id) REFERENCES sor_requests(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for system settings
CREATE TABLE IF NOT EXISTS sor_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default settings
INSERT INTO sor_settings (setting_key, setting_value, description) VALUES
('signature_timeout_days', '7', 'Days before signature request is considered overdue'),
('auto_remind_enabled', 'true', 'Enable automatic reminders for unsigned documents'),
('dashboard_refresh_interval', '30', 'Dashboard auto-refresh interval in seconds')
ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value);

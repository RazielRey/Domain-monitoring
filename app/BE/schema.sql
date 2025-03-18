-- Domain Monitoring System Database Schema

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS scans;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_google_user BOOLEAN DEFAULT FALSE,
    profile_picture VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scans table to store domain monitoring results
CREATE TABLE scans (
    scan_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    url VARCHAR(512) NOT NULL,
    status_code VARCHAR(50),
    ssl_status VARCHAR(50),
    expiration_date VARCHAR(50),
    issuer VARCHAR(255),
    last_scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, url)
);

-- Create indexes for performance
CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_url ON scans(url);

-- Add comments to tables and columns for documentation
COMMENT ON TABLE users IS 'Stores user account information';
COMMENT ON COLUMN users.user_id IS 'Unique identifier for each user';
COMMENT ON COLUMN users.username IS 'Username for login (email address)';
COMMENT ON COLUMN users.password IS 'User password (should be encrypted in production)';
COMMENT ON COLUMN users.is_google_user IS 'True if user authenticated via Google OAuth';
COMMENT ON COLUMN users.profile_picture IS 'URL to user profile picture (for Google users)';

COMMENT ON TABLE scans IS 'Stores domain monitoring scan results';
COMMENT ON COLUMN scans.scan_id IS 'Unique identifier for each scan';
COMMENT ON COLUMN scans.user_id IS 'Reference to the user who owns this domain';
COMMENT ON COLUMN scans.url IS 'Domain URL being monitored';
COMMENT ON COLUMN scans.status_code IS 'HTTP status result (OK/FAILED)';
COMMENT ON COLUMN scans.ssl_status IS 'SSL certificate status (valid/failed)';
COMMENT ON COLUMN scans.expiration_date IS 'SSL certificate expiration date';
COMMENT ON COLUMN scans.issuer IS 'SSL certificate issuer name';
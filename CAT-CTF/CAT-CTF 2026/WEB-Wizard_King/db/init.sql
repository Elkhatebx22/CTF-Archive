CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(128) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL,
  role VARCHAR(32) NOT NULL DEFAULT 'user',
  display_name VARCHAR(128) NOT NULL DEFAULT ''
);

ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(32) NOT NULL DEFAULT 'user';
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(128) NOT NULL DEFAULT '';
UPDATE users SET role = 'user' WHERE role = '';
UPDATE users SET display_name = username WHERE display_name = '';

INSERT INTO users (username, password, role, display_name) VALUES
  ('riley', 'REDACTED', 'user', 'Riley Chen'),
  ('morgan', 'REDACTED', 'user', 'Morgan Patel')
ON DUPLICATE KEY UPDATE
  password = VALUES(password),
  role = VALUES(role),
  display_name = VALUES(display_name);

INSERT INTO users (username, password, role, display_name) VALUES
  ('owner', SHA2(UUID(), 256), 'owner', 'Aster Owner')
ON DUPLICATE KEY UPDATE
  password = SHA2(UUID(), 256),
  role = VALUES(role),
  display_name = VALUES(display_name);

DELETE FROM users WHERE username = 'admin';

CREATE TABLE IF NOT EXISTS tickets (
  id CHAR(36) PRIMARY KEY,
  owner VARCHAR(128) NOT NULL,
  title TEXT NOT NULL,
  body MEDIUMTEXT NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  INDEX idx_tickets_owner_created (owner, created_at)
);

CREATE USER IF NOT EXISTS 'clover'@'%' IDENTIFIED BY 'REDACTED';
CREATE USER IF NOT EXISTS 'clover_writer'@'%' IDENTIFIED BY 'REDACTED';
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'clover'@'%';
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'clover_writer'@'%';
GRANT SELECT ON clover.* TO 'clover'@'%';
GRANT INSERT ON clover.users TO 'clover_writer'@'%';
FLUSH PRIVILEGES;

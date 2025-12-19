-- This file runs only on first initialization (empty data dir).
-- You can create multiple users/databases and grant privileges here.
-- Edit as needed.

-- Example: create additional database and user 'volans'
CREATE DATABASE IF NOT EXISTS `volans` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'volans'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON `volans`.* TO 'volans'@'%';

-- Example: ensure default appdb/appuser (matches env defaults)
CREATE DATABASE IF NOT EXISTS `lepus` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'lepus'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON `lepus`.* TO 'lepus'@'%';

FLUSH PRIVILEGES;



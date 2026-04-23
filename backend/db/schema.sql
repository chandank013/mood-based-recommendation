-- ─────────────────────────────────────────────────────────────────────────────
-- Mood Recommender — Complete MySQL Schema (with Authentication)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE DATABASE IF NOT EXISTS mood_recommender
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mood_recommender;

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    last_login    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email    (email),
    INDEX idx_username (username)
);

-- ── Sessions (anonymous fallback — used when not logged in) ──────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id         INT         AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    user_id    INT         DEFAULT NULL,
    created_at DATETIME    DEFAULT CURRENT_TIMESTAMP,
    last_seen  DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_session_id (session_id)
);

-- ── Mood logs ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mood_logs (
    id           INT          AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          DEFAULT NULL,
    session_id   VARCHAR(64)  NOT NULL,
    raw_input    TEXT,
    input_type   ENUM('text','emoji','slider','face','voice') DEFAULT 'text',
    emotion      VARCHAR(32)  NOT NULL,
    confidence   FLOAT,
    intensity    TINYINT      DEFAULT 5,
    context_time ENUM('morning','afternoon','evening','night') DEFAULT NULL,
    context_who  ENUM('alone','family','friends','partner')    DEFAULT NULL,
    mode         ENUM('amplify','contrast')      DEFAULT 'amplify',
    weather      VARCHAR(64)  DEFAULT NULL,
    location     VARCHAR(128) DEFAULT NULL,
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id  (user_id),
    INDEX idx_session  (session_id),
    INDEX idx_emotion  (emotion),
    INDEX idx_created  (created_at)
);

-- ── Recommendations ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    id          INT         AUTO_INCREMENT PRIMARY KEY,
    mood_log_id INT         NOT NULL,
    user_id     INT         DEFAULT NULL,
    category    ENUM('music','movie','book','food','activity','podcast') NOT NULL,
    title       VARCHAR(255),
    external_id VARCHAR(128),
    thumbnail   TEXT,
    source      VARCHAR(64),
    metadata    JSON,
    created_at  DATETIME    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mood_log_id) REFERENCES mood_logs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users(id)     ON DELETE SET NULL,
    INDEX idx_mood_log (mood_log_id),
    INDEX idx_rec_user (user_id)
);

-- ── Social mood aggregation ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS social_moods (
    id        INT         AUTO_INCREMENT PRIMARY KEY,
    emotion   VARCHAR(32) NOT NULL,
    count     INT         DEFAULT 1,
    hour_slot DATETIME    NOT NULL,
    UNIQUE KEY uniq_emotion_hour (emotion, hour_slot),
    INDEX idx_hour (hour_slot)
);

-- ── Context signals ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS context_signals (
    id           INT          AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          DEFAULT NULL,
    session_id   VARCHAR(64)  NOT NULL,
    signal_type  VARCHAR(32)  NOT NULL,
    signal_value VARCHAR(128) NOT NULL,
    recorded_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_cs_user    (user_id),
    INDEX idx_cs_session (session_id)
);




USE mood_recommender;
ALTER TABLE mood_logs ADD COLUMN user_id INT DEFAULT NULL AFTER session_id;
ALTER TABLE mood_logs ADD INDEX idx_user_id (user_id);
ALTER TABLE recommendations ADD COLUMN user_id INT DEFAULT NULL AFTER mood_log_id;
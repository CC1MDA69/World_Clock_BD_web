
PRAGMA foreign_keys = ON;
PRAGMA encoding = "UTF-8";

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    email       TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,  -- bcrypt hash
    avatar_url  TEXT,
    created_at  DATETIME DEFAULT (datetime('now')),
    updated_at  DATETIME DEFAULT (datetime('now'))
);

-- Таблица городов / часовых поясов
CREATE TABLE IF NOT EXISTS cities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    country     TEXT    NOT NULL,
    timezone    TEXT    NOT NULL,  -- IANA: Europe/Moscow
    utc_offset  TEXT    NOT NULL,  -- UTC+3
    latitude    REAL,
    longitude   REAL
);

-- Города пользователя (избранные)
CREATE TABLE IF NOT EXISTS user_cities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    city_id     INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    sort_order  INTEGER DEFAULT 0,
    added_at    DATETIME DEFAULT (datetime('now')),
    UNIQUE(user_id, city_id)
);

-- История сессий
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       TEXT    NOT NULL UNIQUE,
    created_at  DATETIME DEFAULT (datetime('now')),
    expires_at  DATETIME NOT NULL
);

-- ============================================
-- Начальные данные: города России
-- ============================================
INSERT OR IGNORE INTO cities (name, country, timezone, utc_offset, latitude, longitude) VALUES
    ('Москва',        'Россия', 'Europe/Moscow',      'UTC+3',  55.7558,  37.6173),
    ('Краснодар',     'Россия', 'Europe/Moscow',      'UTC+3',  45.0448,  38.9760),
    ('Сочи',          'Россия', 'Europe/Moscow',      'UTC+3',  43.6028,  39.7342),
    ('Мурманск',      'Россия', 'Europe/Moscow',      'UTC+3',  68.9792,  33.0925),
    ('Санкт-Петербург','Россия','Europe/Moscow',      'UTC+3',  59.9343,  30.3351),
    ('Екатеринбург',  'Россия', 'Asia/Yekaterinburg', 'UTC+5',  56.8389,  60.6057),
    ('Новосибирск',   'Россия', 'Asia/Novosibirsk',   'UTC+7',  54.9893,  82.9140),
    ('Красноярск',    'Россия', 'Asia/Krasnoyarsk',   'UTC+7',  56.0096,  92.8726),
    ('Владивосток',   'Россия', 'Asia/Vladivostok',   'UTC+10', 43.1155, 131.8855),
    ('Калининград',   'Россия', 'Europe/Kaliningrad',  'UTC+2',  54.7104,  20.4522),
    ('Лондон',        'Великобритания', 'Europe/London', 'UTC+0', 51.5074,  -0.1278),
    ('Берлин',        'Германия',       'Europe/Berlin', 'UTC+1', 52.5200,  13.4050),
    ('Нью-Йорк',      'США',            'America/New_York','UTC-5',40.7128,-74.0060),
    ('Токио',         'Япония',         'Asia/Tokyo',    'UTC+9', 35.6762, 139.6503),
    ('Пекин',         'Китай',          'Asia/Shanghai', 'UTC+8', 39.9042, 116.4074);
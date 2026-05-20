
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "time.db"


def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con



# Пользователи


def hash_password(password: str) -> str:
    """Простое хеширование через SHA-256 + соль.
    В продакшне замените на bcrypt: pip install bcrypt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split(":", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed


def register_user(username: str, email: str, password: str) -> dict | None:
    """Регистрация нового пользователя. Возвращает пользователя или None."""
    with get_connection() as con:
        try:
            cur = con.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hash_password(password))
            )
            con.commit()
            return get_user_by_id(cur.lastrowid)
        except sqlite3.IntegrityError:
            return None  # username или email уже существует


def login_user(login: str, password: str) -> str | None:
    with get_connection() as con:
        row = con.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (login, login)
        ).fetchone()

        if not row or not verify_password(password, row["password"]):
            return None

        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(days=30)
        con.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (row["id"], token, expires.isoformat())
        )
        con.commit()
        return token


#Получить пользователя по токену сессии
def get_user_by_token(token: str) -> dict | None:
    with get_connection() as con:
        row = con.execute("""
            SELECT u.* FROM users u
            JOIN sessions s ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > datetime('now')
        """, (token,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_connection() as con:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def logout_user(token: str):
    with get_connection() as con:
        con.execute("DELETE FROM sessions WHERE token = ?", (token,))
        con.commit()



# Города / часовые пояса

"""Все доступные города."""
def get_all_cities() -> list[dict]:
    with get_connection() as con:
        rows = con.execute("SELECT * FROM cities ORDER BY country, name").fetchall()
        return [dict(r) for r in rows]


"""Поиск городов по названию или стране."""
def search_cities(query: str) -> list[dict]:
    with get_connection() as con:
        rows = con.execute(
            "SELECT * FROM cities WHERE name LIKE ? OR country LIKE ? ORDER BY name",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
        return [dict(r) for r in rows]


"""Добавить город в избранное пользователя."""
def add_city_to_user(user_id: int, city_id: int) -> bool:
    with get_connection() as con:
        try:
            con.execute(
                "INSERT INTO user_cities (user_id, city_id) VALUES (?, ?)",
                (user_id, city_id)
            )
            con.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # уже добавлен


"""Удалить город из избранного."""
def remove_city_from_user(user_id: int, city_id: int):
    with get_connection() as con:
        con.execute(
            "DELETE FROM user_cities WHERE user_id = ? AND city_id = ?",
            (user_id, city_id)
        )
        con.commit()


"""Список избранных городов пользователя."""
def get_user_cities(user_id: int) -> list[dict]:
    with get_connection() as con:
        rows = con.execute("""
            SELECT c.*, uc.sort_order, uc.added_at
            FROM cities c
            JOIN user_cities uc ON uc.city_id = c.id
            WHERE uc.user_id = ?
            ORDER BY uc.sort_order, c.name
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────
# Демо
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== TIME APP — тест БД ===\n")

    # Регистрация
    user = register_user("Macan_Hiylan", "macan@example.com", "secret123")
    if user:
        print(f"✓ Зарегистрирован: {user['username']} (id={user['id']})")
    else:
        print("! Пользователь уже существует")
        user = {"id": 1, "username": "Macan_Hiylan"}

    # Авторизация
    token = login_user("Macan_Hiylan", "secret123")
    print(f"✓ Токен сессии: {token[:20]}...")

    # Добавить города
    add_city_to_user(user["id"], 1)  # Москва
    add_city_to_user(user["id"], 2)  # Краснодар
    add_city_to_user(user["id"], 3)  # Сочи

    cities = get_user_cities(user["id"])
    print(f"\n✓ Избранные города {user['username']}:")
    for c in cities:
        print(f"  • {c['name']} ({c['country']}) — {c['utc_offset']}")

    # Поиск
    results = search_cities("Мос")
    print(f"\n✓ Поиск 'Мос': {[r['name'] for r in results]}")

    # Все города
    all_cities = get_all_cities()
    print(f"\n✓ Всего городов в БД: {len(all_cities)}")
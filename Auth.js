
const TimeAuth = (() => {
const USERS_KEY   = 'time_users';
const SESSION_KEY = 'time_session';

//Утилиты

function hashPassword(password) {
    // Простой хэш для демо (в продакшне используйте bcrypt на сервере)
    let hash = 0;
    const str = password + 'time_salt_2024';
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return hash.toString(36);
}

function generateToken() {
    return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function getUsers() {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
}

function saveUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
}
// Регистрация

function register(username, email, password) {
    const users = getUsers();

    if (users.find(u => u.username === username)) {
        return { ok: false, error: 'Пользователь с таким логином уже существует' };
    }
    if (users.find(u => u.email === email)) {
        return { ok: false, error: 'Email уже используется' };
    }

    const user = {
        id:         generateToken(),
        username,
        email,
        password:   hashPassword(password),
        cities:     [],
        created_at: new Date().toISOString()
    };

    users.push(user);
    saveUsers(users);
    return { ok: true, user: publicUser(user) };
}

  // Авторизация

function login(login, password) {
    const users = getUsers();
    const user  = users.find(u =>
        (u.username === login || u.email === login)
    );

    if (!user || user.password !== hashPassword(password)) {
        return { ok: false, error: 'Неверный логин или пароль' };
    }

    const session = {
        token:    generateToken(),
        userId:   user.id,
        username: user.username,
      expires:  Date.now() + 30 * 24 * 60 * 60 * 1000 // 30 дней
    };

    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    return { ok: true, user: publicUser(user) };
}

// Выход

function logout() {
    localStorage.removeItem(SESSION_KEY);
    window.location.href = 'index_Avtorizate1.html';
}
// Текущий пользователь

function currentUser() {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;

    const session = JSON.parse(raw);
    if (Date.now() > session.expires) {
        localStorage.removeItem(SESSION_KEY);
        return null;
    }

    const users = getUsers();
    const user  = users.find(u => u.id === session.userId);
    return user ? publicUser(user) : null;
}

function isLoggedIn() {
    return !!currentUser();
}

// Города пользователя

function getUserCities() {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    if (!session) return [];

    const users = getUsers();
    const user  = users.find(u => u.id === session.userId);
    return user ? (user.cities || []) : [];
}

function addCity(city) {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    if (!session) return false;

    const users = getUsers();
    const idx   = users.findIndex(u => u.id === session.userId);
    if (idx === -1) return false;

    const already = users[idx].cities.find(c => c.id === city.id);
    if (already) return false;

    users[idx].cities.push({ ...city, added_at: new Date().toISOString() });
    saveUsers(users);
    return true;
}

function removeCity(cityId) {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    if (!session) return;

    const users = getUsers();
    const idx   = users.findIndex(u => u.id === session.userId);
    if (idx === -1) return;

    users[idx].cities = users[idx].cities.filter(c => c.id !== cityId);
    saveUsers(users);
}

function requireAuth(redirectTo = 'index_Avtorizate1.html') {
    if (!isLoggedIn()) window.location.href = redirectTo;
}

function redirectIfLoggedIn(redirectTo = 'index_glavnay.html') {
    if (isLoggedIn()) window.location.href = redirectTo;
}
// Внутренние

function publicUser(user) {
    const { password, ...safe } = user;
    return safe;
}

return {
    register, login, logout,
    currentUser, isLoggedIn,
    getUserCities, addCity, removeCity,
    requireAuth, redirectIfLoggedIn
};
})();
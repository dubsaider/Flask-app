-- Создание таблиц
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS team_members (
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    team_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

-- Начальные данные для тестирования
INSERT OR IGNORE INTO users (id, username, email) VALUES 
    (1, 'alice', 'alice@example.com'),
    (2, 'bob', 'bob@example.com'),
    (3, 'charlie', 'charlie@example.com');

INSERT OR IGNORE INTO teams (id, name, description) VALUES 
    (1, 'Development Team', 'Main development team'),
    (2, 'Design Team', 'UI/UX design team');

INSERT OR IGNORE INTO team_members (team_id, user_id, role) VALUES 
    (1, 1, 'admin'),
    (1, 2, 'member'),
    (2, 1, 'member'),
    (2, 3, 'admin');

INSERT OR IGNORE INTO boards (id, title, description, team_id) VALUES 
    (1, 'Sprint 1', 'First sprint board', 1),
    (2, 'Design Tasks', 'Design related tasks', 2);
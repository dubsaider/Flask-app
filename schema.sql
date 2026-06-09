-- Пользователи системы
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL DEFAULT 'hash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Команды
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    curator_id INTEGER,  -- куратор команды
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curator_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Участники команды с ролями
CREATE TABLE IF NOT EXISTS team_members (
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('leader', 'developer')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Доски
CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    team_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

-- Колонки
CREATE TABLE IF NOT EXISTS columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    board_id INTEGER NOT NULL,
    is_done INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
);

-- Карточки/задачи
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    position INTEGER NOT NULL,
    column_id INTEGER NOT NULL,
    assignee_id INTEGER,
    created_by INTEGER,  -- кто создал задачу (руководитель)
    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived')),
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Комментарии к задачам
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    card_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Уведомления
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    board_id INTEGER,
    card_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE SET NULL
);

-- Тестовые данные
INSERT OR IGNORE INTO users (id, username, email) VALUES 
    (1, 'alice', 'alice@example.com'),      -- разработчик
    (2, 'bob', 'bob@example.com'),          -- разработчик
    (3, 'charlie', 'charlie@example.com'),  -- руководитель
    (4, 'diana', 'diana@example.com'),      -- куратор
    (5, 'eve', 'eve@example.com');          -- разработчик

INSERT OR IGNORE INTO teams (id, name, description, curator_id) VALUES 
    (1, 'Development Team', 'Main development team', 4),
    (2, 'Design Team', 'UI/UX design team', NULL);

INSERT OR IGNORE INTO team_members (team_id, user_id, role) VALUES 
    (1, 1, 'developer'),
    (1, 2, 'developer'),
    (1, 3, 'leader'),
    (2, 5, 'leader'),
    (2, 1, 'developer');

INSERT OR IGNORE INTO boards (id, title, description, team_id) VALUES 
    (1, 'Sprint 1', 'First sprint board', 1),
    (2, 'Design Tasks', 'Design related tasks', 2);

INSERT OR IGNORE INTO columns (id, title, position, board_id, is_done) VALUES 
    (1, 'To Do', 0, 1, 0),
    (2, 'In Progress', 1, 1, 0),
    (3, 'Review', 2, 1, 0),
    (4, 'Done', 3, 1, 1),
    (5, 'To Do', 0, 2, 0),
    (6, 'In Progress', 1, 2, 0),
    (7, 'Done', 2, 2, 1);

INSERT OR IGNORE INTO cards (id, title, description, position, column_id, assignee_id, created_by, priority, status) VALUES 
    (1, 'Setup project', 'Initialize repository and project structure', 0, 1, 1, 3, 'high', 'active'),
    (2, 'Design database', 'Create database schema', 1, 1, 2, 3, 'high', 'active'),
    (3, 'Implement API', 'Create REST API endpoints', 0, 2, 1, 3, 'medium', 'active'),
    (4, 'Write tests', 'Add unit tests', 0, 3, NULL, 3, 'low', 'active');

INSERT OR IGNORE INTO comments (id, text, card_id, user_id) VALUES 
    (1, 'Need to use PostgreSQL instead of SQLite', 1, 4),
    (2, 'I will start working on this today', 1, 1);
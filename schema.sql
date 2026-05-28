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

CREATE TABLE IF NOT EXISTS columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    board_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    position INTEGER NOT NULL,
    column_id INTEGER NOT NULL,
    assignee_id INTEGER,
    priority TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Начальные данные
INSERT OR IGNORE INTO users (id, username, email) VALUES 
    (1, 'alice', 'alice@example.com'),
    (2, 'bob', 'bob@example.com'),
    (3, 'charlie', 'charlie@example.com'),
    (4, 'diana', 'diana@example.com');

INSERT OR IGNORE INTO teams (id, name, description) VALUES 
    (1, 'Development Team', 'Main development team'),
    (2, 'Design Team', 'UI/UX design team');

INSERT OR IGNORE INTO team_members (team_id, user_id, role) VALUES 
    (1, 1, 'admin'),
    (1, 2, 'member'),
    (1, 3, 'member'),
    (2, 1, 'member'),
    (2, 4, 'admin');

INSERT OR IGNORE INTO boards (id, title, description, team_id) VALUES 
    (1, 'Sprint 1', 'First sprint board', 1),
    (2, 'Design Tasks', 'Design related tasks', 2);

-- Добавляем колонки по умолчанию для досок
INSERT OR IGNORE INTO columns (id, title, position, board_id) VALUES 
    (1, 'To Do', 0, 1),
    (2, 'In Progress', 1, 1),
    (3, 'Review', 2, 1),
    (4, 'Done', 3, 1),
    (5, 'To Do', 0, 2),
    (6, 'In Progress', 1, 2),
    (7, 'Done', 2, 2);

-- Добавляем тестовые карточки
INSERT OR IGNORE INTO cards (id, title, description, position, column_id, assignee_id, priority) VALUES 
    (1, 'Setup project', 'Initialize repository and project structure', 0, 1, 1, 'high'),
    (2, 'Design database', 'Create database schema', 1, 1, 2, 'high'),
    (3, 'Implement API', 'Create REST API endpoints', 0, 2, 3, 'medium'),
    (4, 'Write tests', 'Add unit tests', 0, 3, 1, 'low'),
    (5, 'Create wireframes', 'Design wireframes for main pages', 0, 5, 4, 'high'),
    (6, 'Design components', 'Create UI components', 0, 6, 4, 'medium');
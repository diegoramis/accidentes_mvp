CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accident_case (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_token VARCHAR(64) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_date VARCHAR(30) NOT NULL,
    event_time VARCHAR(20) NOT NULL,
    location_text VARCHAR(255) NOT NULL,
    latitude VARCHAR(40) NOT NULL,
    longitude VARCHAR(40) NOT NULL,
    narrative TEXT NOT NULL,
    damaged_only BOOLEAN DEFAULT 1,
    status VARCHAR(30) DEFAULT 'Registrado',
    owner_id INTEGER NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES user(id)
);

CREATE TABLE driver (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accident_id INTEGER NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    license_number VARCHAR(60) NOT NULL,
    phone VARCHAR(40),
    FOREIGN KEY(accident_id) REFERENCES accident_case(id)
);

CREATE TABLE vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accident_id INTEGER NOT NULL,
    owner_name VARCHAR(120) NOT NULL,
    plate VARCHAR(20) NOT NULL,
    brand VARCHAR(60) NOT NULL,
    model VARCHAR(60) NOT NULL,
    color VARCHAR(40),
    FOREIGN KEY(accident_id) REFERENCES accident_case(id)
);

CREATE TABLE photo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accident_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(accident_id) REFERENCES accident_case(id)
);

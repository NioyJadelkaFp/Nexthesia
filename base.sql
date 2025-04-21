-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    contraseña VARCHAR(255),
    rango VARCHAR(50) DEFAULT 'User',
    xp INT DEFAULT 0
);

-- Tabla de publicaciones
CREATE TABLE publicaciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100),
    contenido TEXT,
    user_id INT REFERENCES usuarios(id),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

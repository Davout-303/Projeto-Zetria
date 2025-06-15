CREATE DATABASE IF NOT EXISTS zetria CHARACTER
SET
    utf8mb4 COLLATE utf8mb4_unicode_ci;

USE zetria;


CREATE TABLE
    IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome_usuario VARCHAR(80) UNIQUE NOT NULL,
        senha_hash VARCHAR(255) NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


CREATE TABLE
    IF NOT EXISTS notas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT NOT NULL,
        titulo VARCHAR(255) NOT NULL,
        conteudo TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
    );


CREATE TABLE
    IF NOT EXISTS etiquetas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(50) UNIQUE NOT NULL
    );


CREATE TABLE
    IF NOT EXISTS nota_etiquetas (
        nota_id INT NOT NULL,
        etiqueta_id INT NOT NULL,
        PRIMARY KEY (nota_id, etiqueta_id),
        FOREIGN KEY (nota_id) REFERENCES notas (id) ON DELETE CASCADE,
        FOREIGN KEY (etiqueta_id) REFERENCES etiquetas (id) ON DELETE CASCADE
    );


CREATE TABLE
    IF NOT EXISTS ligacoes_notas (
        nota_origem_id INT NOT NULL,
        nota_destino_id INT NOT NULL,
        PRIMARY KEY (nota_origem_id, nota_destino_id),
        FOREIGN KEY (nota_origem_id) REFERENCES notas (id) ON DELETE CASCADE,
        FOREIGN KEY (nota_destino_id) REFERENCES notas (id) ON DELETE CASCADE
    );


CREATE TABLE
    IF NOT EXISTS flashcards (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nota_id INT NOT NULL,
        frente_conteudo TEXT NOT NULL,
        verso_conteudo TEXT NOT NULL,
        caminho_audio VARCHAR(255) NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        revisar_em TIMESTAMP NULL,
        FOREIGN KEY (nota_id) REFERENCES notas (id) ON DELETE CASCADE
    );


CREATE TABLE
    IF NOT EXISTS tarefas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT NOT NULL,
        titulo VARCHAR(255) NOT NULL,
        descricao TEXT NULL,
        data_limite DATETIME NULL,
        recorrente BOOLEAN DEFAULT FALSE,
        regra_recorrencia VARCHAR(100) NULL,
        concluida BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
    );
import sqlite3

# cria ou conecta ao banco
conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# =========================
# TABELA USUARIOS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (

id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT NOT NULL,
senha TEXT NOT NULL

)
""")

# usuário padrão

cursor.execute("""
INSERT INTO usuarios (usuario,senha)
VALUES ('admin','zenlife123')
""")


# =========================
# TABELA CLIENTES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (

id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
telefone TEXT,
Endereco TEXT,
Cep TEXT, 
Cidade TEXT
Estado TEXT
email TEXT

)
""")


# =========================
# TABELA LEADS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (

id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
telefone TEXT,
seguro TEXT,
origem TEXT,
status TEXT

)
""")


# =========================
# TABELA APOLICES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS apolices (

id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente TEXT,
seguro TEXT,
seguradora TEXT,
valor REAL,
data_inicio DATE,
data_renovacao DATE

)
""")


# =========================
# TABELA AGENDA
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS agenda (

id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente TEXT,
descricao TEXT,
data_contato DATE

)
""")


conn.commit()

conn.close()

print("Banco de dados criado com sucesso!")
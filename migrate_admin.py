from flask import Flask
from models import db, Usuario
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/promoprecco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def migrate_admin_field():
    """Adiciona o campo is_admin à tabela usuario se não existir"""
    
    # Conecta diretamente ao SQLite para verificar a estrutura
    conn = sqlite3.connect('instance/promoprecco.db')
    cursor = conn.cursor()
    
    try:
        # Verifica se a coluna is_admin já existe na tabela usuario
        cursor.execute("PRAGMA table_info(usuario)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adicionando coluna is_admin à tabela usuario...")
            cursor.execute("ALTER TABLE usuario ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_usuario_is_admin ON usuario (is_admin)")
            conn.commit()
            print("Coluna is_admin adicionada com sucesso!")
        else:
            print("Coluna is_admin já existe na tabela usuario.")
            
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        migrate_admin_field()
        print("Migração de admin concluída!")
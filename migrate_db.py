from flask import Flask
from models import db, Produto, Estabelecimento, Preco, Usuario, Favorito
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///promoprecco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def migrate_database():
    """Migra o banco de dados adicionando a coluna usuario_id se não existir"""
    
    # Conecta diretamente ao SQLite para verificar a estrutura
    conn = sqlite3.connect('instance/promoprecco.db')
    cursor = conn.cursor()
    
    try:
        # Verifica se a coluna usuario_id já existe na tabela preco
        cursor.execute("PRAGMA table_info(preco)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'usuario_id' not in columns:
            print("Adicionando coluna usuario_id à tabela preco...")
            cursor.execute("ALTER TABLE preco ADD COLUMN usuario_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_preco_usuario_id ON preco (usuario_id)")
            conn.commit()
            print("Coluna usuario_id adicionada com sucesso!")
        else:
            print("Coluna usuario_id já existe na tabela preco.")
            
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        migrate_database()
        print("Migração concluída!")
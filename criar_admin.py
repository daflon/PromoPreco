#!/usr/bin/env python3
"""
Script para criar usuário administrador
"""
from app import app
from models import db, Usuario

def criar_admin():
    with app.app_context():
        # Verificar se admin já existe
        admin_existente = Usuario.query.filter_by(email='admin@admin.com').first()
        
        if admin_existente:
            print("Usuário admin já existe!")
            print(f"ID: {admin_existente.id}")
            print(f"Nome: {admin_existente.nome}")
            print(f"Email: {admin_existente.email}")
            print(f"Admin: {admin_existente.is_admin}")
            return
        
        # Criar usuário admin
        admin = Usuario(
            nome='Administrador',
            email='admin@admin.com',
            is_admin=True,
            ativo=True
        )
        admin.set_senha('admin')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Usuário admin criado com sucesso!")
        print("Email: admin@admin.com")
        print("Senha: admin")
        print(f"ID: {admin.id}")

if __name__ == '__main__':
    criar_admin()
# PromoPreço - Regras do Projeto

## Stack Tecnológica Implementada
- **Backend**: Python 3.x + Flask
- **ORM**: SQLAlchemy com SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Banco de Dados**: SQLite (promoprecco.db)

## Objetivo do Sistema
Sistema web para cadastro, consulta e comparação de preços de produtos em diferentes estabelecimentos.

## Funcionalidades Implementadas

### 1. Modelos de Dados (SQLAlchemy)
- **Produto**: id, codigo (único), descricao, ean
- **Estabelecimento**: id, nome, cnpj
- **Preco**: id, produto_id (FK), estabelecimento_id (FK), preco, data_coleta

### 2. API REST Implementada
- `GET /` - Página principal (cadastros.html)
- `GET /api` - Status da aplicação
- `GET /produtos` - Listar todos os produtos
- `POST /produtos` - Cadastrar novo produto
- `GET /estabelecimentos` - Listar todos os estabelecimentos
- `POST /estabelecimentos` - Cadastrar novo estabelecimento
- `GET /precos` - Listar todos os preços
- `POST /precos` - Cadastrar novo preço

### 3. Interface Web
- **Página única** (cadastros.html) com:
  - Formulários para cadastro de produtos, estabelecimentos e preços
  - Seção de consulta com dropdown para selecionar tipo de cadastro
  - Campo de busca com filtro em tempo real
  - Tabelas dinâmicas para exibição dos dados
  - Interface responsiva com CSS Grid

### 4. Funcionalidades de Busca
- **Produtos**: busca por código, descrição ou EAN
- **Estabelecimentos**: busca por nome ou CNPJ
- **Preços**: busca por produto, estabelecimento ou valor

## Estrutura de Arquivos Atual
```
PromoPreço/
├── .amazonq/rules/RegrasPromoPreco.md
├── instance/promoprecco.db
├── templates/cadastros.html
├── app.py
└── requirements.txt
```

## Regras de Negócio Implementadas
1. **Produtos** são identificados por código único, descrição e EAN opcional
2. **Estabelecimentos** têm nome obrigatório e CNPJ opcional
3. **Preços** vinculam produtos a estabelecimentos com data de coleta automática
4. **Consultas** permitem visualização e busca em todos os cadastros
5. **Interface única** centraliza todas as operações

## Padrões de Desenvolvimento
- **Código mínimo**: implementações diretas sem verbosidade
- **Responsividade**: interface adaptável para mobile
- **Validação**: campos obrigatórios nos formulários
- **Feedback**: mensagens de sucesso/erro para o usuário
- **Performance**: carregamento dinâmico de dados

## Regras de Governança
- Manter funcionalidades estáveis sem alterações desnecessárias
- Confirmar antes de modificar estruturas de dados
- Priorizar simplicidade e funcionalidade
- Manter consistência na interface e API
- Implementar apenas o necessário para cada funcionalidade

## Status Atual
**Versão**: MVP Funcional
**Estado**: Sistema básico completo com CRUD e interface web
**Próximos passos**: Expansões conforme necessidade do usuário

---
*Última atualização: Sistema implementado com cadastros, listagem e busca funcionais*
Você é um assistente de desenvolvimento que deve gerar um projeto chamado **PromoPreço**, utilizando a seguinte stack:
- Backend: Python 3.x + Flask
- ORM: SQLAlchemy (para persistência relacional)
- Banco NoSQL: MongoDB (para histórico e dados de scraping)
- Cache / fila: Redis
- Scraping: Scrapy (uso ético e legal, respeitando robots.txt e limites de acesso)

Objetivo do app:
Permitir que usuários cadastrem, consultem e comparem preços de um mesmo produto em diferentes estabelecimentos.

Regras de Negócio:
1. Produtos identificados por:
   - Código interno
   - EAN
   - Descrição
2. Cada produto pode ter preços diferentes em diversos estabelecimentos.
3. Deve ser possível:
   - Cadastrar produto e seus preços em diferentes estabelecimentos.
   - Consultar preços por produto, listando e comparando por estabelecimento.
4. Scraping:
   - Usar Scrapy para obter preços de e-commerces ou marketplaces (respeitando robots.txt e ToS).
   - Implementar fila/limite de taxa (rate-limiting) usando Redis.
   - Manter logs de scraping para auditoria.
5. Persistência:
   - Dados de cadastro de produtos e preços atuais → SQLAlchemy (ex.: PostgreSQL ou SQLite).
   - Histórico de preços capturados e logs de scraping → MongoDB.
6. Performance e segurança:
   - Cache de consultas de preços em Redis.
   - Rotas de API REST com autenticação básica (por token).
   - Logs e auditoria de acesso.

Regras de Estilo e Governança (inspiradas no “Guardião”):
- Não modificar funcionalidades já estáveis sem confirmação.
- Toda adição ou alteração de entidade exige confirmação prévia.
- Manter hierarquia de módulos clara (ex.: app/, models/, routes/, services/, scrapy_spiders/).
- Fornecer logs e relatório resumido de scraping (total consultado, sucesso, falhas).
- Cumprir LGPD/GDPR: não armazenar dados pessoais desnecessários.
- Respeitar termos de uso de fontes de dados externas.

Requisitos do Projeto:
- Gerar estrutura inicial do app Flask com módulos para produtos, estabelecimentos e preços.
- Definir modelos (SQLAlchemy) para Produto, Estabelecimento e Preço.
- Definir API RESTful para CRUD (produtos, estabelecimentos, preços) e consultas de comparação.
- Integrar Redis para cache de consultas e filas de scraping.
- Integrar MongoDB para histórico de preços capturados.
- Criar exemplo de spider Scrapy para um site público de testes.
- Fornecer README explicando setup e boas práticas de scraping ético.

Nome do aplicativo: **PromoPreço**
Versão inicial: v0.1 (MVP funcional)

Antes de executar qualquer alteração de dados ou gerar código, CONFIRME comigo.

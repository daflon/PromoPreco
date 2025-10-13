# PromoPreço - Regras do Projeto

## Stack Tecnológica Implementada
- **Backend**: Python 3.x + Flask + SQLAlchemy + RapidFuzz
- **Banco de Dados**: SQLite (promoprecco.db)
- **Frontend**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Validações**: Backend com regex para CNPJ/EAN
- **Busca**: Fuzzy search com RapidFuzz
- **Cache**: Flask-Caching para otimização
- **Rate Limiting**: Flask-Limiter para controle de acesso
- **Relatórios**: ReportLab (PDF), XlsxWriter (Excel), CSV nativo
- **Testes**: Requests para testes de API

## Objetivo do Sistema
Sistema web completo para cadastro, edição, exclusão e comparação de preços de produtos em diferentes estabelecimentos.

## Funcionalidades Implementadas

### 1. Modelos de Dados (SQLAlchemy)
- **Produto**: id, descricao (obrigatório), ean (13 dígitos, opcional)
- **Estabelecimento**: id, nome (obrigatório), cnpj (14 dígitos, opcional), bairro (obrigatório), cidade (obrigatório)
- **Preco**: id, produto_id (FK), estabelecimento_id (FK), preco (>0), data_coleta (automática)

### 2. API REST Completa
**Produtos**
- `GET /produtos` - Listar todos
- `POST /produtos` - Criar novo
- `PUT /produtos/<id>` - Editar existente
- `DELETE /produtos/<id>` - Excluir

**Estabelecimentos**
- `GET /estabelecimentos` - Listar todos
- `POST /estabelecimentos` - Criar novo
- `PUT /estabelecimentos/<id>` - Editar existente
- `DELETE /estabelecimentos/<id>` - Excluir

**Preços**
- `GET /precos` - Listar todos (com paginação)
- `GET /precos/detalhados` - Listar com dados completos de produtos/estabelecimentos
- `POST /precos` - Criar novo
- `PUT /precos/<id>` - Editar existente
- `DELETE /precos/<id>` - Excluir

**Produtos com Preços**
- `GET /produtos/com-precos` - Listar apenas produtos que têm preços cadastrados

**Relatórios e Estatísticas**
- `GET /relatorios` - Interface de relatórios
- `GET /api/historico-precos/<produto_id>` - Histórico de preços por produto
- `GET /api/relatorio-precos` - Relatório geral com filtros e exportação
- `GET /precos/ordenados` - Preços com ordenação avançada
- `GET /api/estatisticas-avancadas` - Estatísticas para gráficos

**Sistema**
- `GET /` - Interface principal de cadastros
- `GET /dashboard` - Interface de dashboard e relatórios
- `GET /dashboard/stats` - Estatísticas do sistema
- `GET /comparar/<produto_id>` - Comparação de preços por produto
- `GET /comparar?q=<termo>` - Comparação com busca fuzzy
- `GET /api` - Status da aplicação

### 3. Validações Implementadas
- **CNPJ**: 14 dígitos numéricos (opcional)
- **EAN**: 13 dígitos numéricos (opcional)
- **Preço**: valor numérico maior que zero
- **Campos obrigatórios**: descrição (produto), nome/bairro/cidade (estabelecimento)
- **Tratamento de erros**: respostas HTTP apropriadas
- **Integridade referencial**: foreign keys validadas

### 4. Interface Web Responsiva
- **Cadastros**: Formulários com validação frontend/backend
- **Dashboard**: Estatísticas e comparação de preços inteligente
- **Listagem**: Tabelas dinâmicas com busca fuzzy e filtros
- **CRUD Completo**: Criar, editar, excluir via interface
- **Design Responsivo**: Adaptável para mobile
- **UX**: Feedback visual, auto-seleção e comparação automática
- **Busca Inteligente**: Fuzzy search com debounce e highlights
- **Auto-seleção**: Seleção automática do primeiro resultado
- **Comparação Automática**: Para resultados únicos de busca

## Estrutura de Arquivos
```
PromoPreço/
├── .amazonq/rules/RegrasPromoPreco.md
├── instance/promoprecco.db
├── templates/cadastros.html
├── app.py (Flask + SQLAlchemy + Validações)
├── requirements.txt
├── README.md
├── ROADMAP.md
├── reset_db.py
└── force_reset.py
```

## Regras de Negócio
1. **Produtos**: descrição obrigatória, EAN opcional com 13 dígitos
2. **Estabelecimentos**: nome/bairro/cidade obrigatórios, CNPJ opcional com 14 dígitos
3. **Preços**: produto e estabelecimento obrigatórios, valor > 0
4. **Data de coleta**: automática no momento do cadastro
5. **CRUD completo**: criar, ler, atualizar e excluir para todas entidades
6. **Listagem de preços**: usa dados detalhados com nomes de produtos/estabelecimentos

## Padrões de Desenvolvimento
- **Validação dupla**: frontend (UX) + backend (segurança)
- **Código mínimo**: implementações diretas e eficientes
- **Tratamento de erros**: respostas JSON padronizadas
- **Responsividade**: interface adaptável
- **Performance**: consultas otimizadas

## Regras de Governança
- Manter validações consistentes entre frontend/backend
- Confirmar antes de modificar estruturas de dados
- Priorizar funcionalidade sobre complexidade
- Manter API RESTful padronizada
- Implementar apenas funcionalidades necessárias

### 5. Funcionalidades Avançadas
- **Busca Fuzzy**: Tolerante a erros de digitação usando RapidFuzz
- **Cache Inteligente**: 60s para consultas, 30s para preços detalhados
- **Rate Limiting**: 30 req/min para buscas, 20 req/min para preços
- **Performance**: Logs de queries lentas (>0.5s)
- **Sanitização**: Proteção contra XSS e SQL injection
- **Auto-seleção**: Seleção automática do primeiro resultado de busca
- **Comparação Automática**: Para produtos únicos encontrados
- **Feedback Visual**: Highlights, animações e contadores

### 6. Sistema de Relatórios
- **Exportação Múltipla**: PDF, Excel e CSV
- **Histórico de Preços**: Acompanhamento temporal por produto
- **Filtros Avançados**: Por produto, estabelecimento, preço e período
- **Ordenação Flexível**: Por preço, produto, estabelecimento ou data
- **Estatísticas Avançadas**: Top produtos, estabelecimentos e variações
- **Interface de Relatórios**: Página dedicada para geração de relatórios

## Status Atual
**Versão**: Sistema Completo com Relatórios Avançados
**Estado**: CRUD, validações, dashboard, busca fuzzy, comparação automática e relatórios funcionais
**Melhorias**: Busca fuzzy, auto-seleção, comparação automática, produtos com preços, relatórios completos
**Próximos passos**: Sistema de usuários, geolocalização, API mobile

---
*Última atualização: Implementação de sistema completo de relatórios com exportação PDF/Excel/CSV*
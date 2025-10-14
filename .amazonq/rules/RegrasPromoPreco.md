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

**Sistema e Interface**
- `GET /` - Interface principal AdminLTE (dashboard)
- `GET /cadastros` - Interface de cadastros AdminLTE
- `GET /dashboard` - Interface de dashboard clássica
- `GET /dashboard/adminlte` - Interface de dashboard AdminLTE
- `GET /relatorios` - Interface de relatórios AdminLTE
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

### 4. Interface Web Moderna (AdminLTE)
- **Interface AdminLTE**: Design moderno e profissional com AdminLTE 3.x
- **Múltiplas Interfaces**: Suporte a interface clássica e AdminLTE
- **Cadastros**: Formulários estilizados com validação frontend/backend
- **Dashboard**: Estatísticas e comparação de preços com cards modernos
- **Relatórios**: Interface dedicada para geração e exportação
- **Listagem**: Tabelas responsivas com busca fuzzy e filtros
- **CRUD Completo**: Criar, editar, excluir via interface moderna
- **Design Responsivo**: Totalmente adaptável para mobile e desktop
- **UX Moderna**: Cards, ícones, feedback visual aprimorado
- **Navegação**: Menu lateral colapsível com ícones FontAwesome
- **Busca Inteligente**: Fuzzy search com debounce e highlights
- **Auto-seleção**: Seleção automática do primeiro resultado
- **Comparação Automática**: Para resultados únicos de busca

## Estrutura de Arquivos
```
PromoPreço/
├── .amazonq/rules/RegrasPromoPreco.md
├── instance/promoprecco.db
├── templates/
│   ├── base_adminlte.html (Template base AdminLTE)
│   ├── cadastros_adminlte.html (Cadastros AdminLTE)
│   ├── dashboard_adminlte.html (Dashboard AdminLTE)
│   ├── relatorios_adminlte.html (Relatórios AdminLTE)
│   ├── cadastros.html (Interface clássica)
│   ├── dashboard.html (Dashboard clássico)
│   └── relatorios.html (Relatórios clássicos)
├── Testes/ (Scripts de teste e população)
├── app.py (Flask + SQLAlchemy + AdminLTE + Relatórios)
├── requirements.txt
├── README.md
├── ROADMAP.md
├── ADMINLTE_GUIDE.md
├── ATUALIZACOES_DOCUMENTACAO.md
└── CORRECOES_APLICADAS.md
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
**Versão**: Sistema Completo com Interface AdminLTE e Relatórios Avançados
**Estado**: CRUD, validações, dashboard AdminLTE, busca fuzzy, comparação automática, relatórios e interface moderna funcionais
**Melhorias**: Interface AdminLTE responsiva, busca fuzzy, auto-seleção, comparação automática, produtos com preços, relatórios completos, múltiplas interfaces
**Próximos passos**: Sistema de usuários, geolocalização, API mobile, PWA

### Interface Atual
- **Interface Principal**: AdminLTE 3.x responsiva e moderna
- **Múltiplas Interfaces**: Suporte a interface clássica e AdminLTE
- **Navegação**: Menu lateral colapsível com ícones
- **Responsividade**: Totalmente adaptada para mobile e desktop
- **UX Moderna**: Cards, botões estilizados, feedback visual aprimorado

---
*Última atualização: Implementação completa da interface AdminLTE com sistema de relatórios avançados*
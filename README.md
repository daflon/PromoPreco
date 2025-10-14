# 🛒 PromoPreço

Sistema para comparação de preços de produtos em diferentes estabelecimentos, permitindo aos usuários encontrar as melhores ofertas.

## 📋 Sobre o Projeto

O PromoPreço é uma aplicação web que permite cadastrar produtos, estabelecimentos e seus respectivos preços, facilitando a comparação e busca pelas melhores ofertas disponíveis no mercado.

## ✨ Funcionalidades

### Core
- ✅ **CRUD Completo**: Criar, editar e excluir produtos, estabelecimentos e preços
- ✅ **Validações**: CNPJ (14 dígitos), EAN (13 dígitos), preços > 0
- ✅ **API REST**: Endpoints completos com PUT/DELETE
- ✅ **Interface Moderna**: AdminLTE 3.x responsiva e profissional
- ✅ **Múltiplas Interfaces**: AdminLTE (principal) + clássica (alternativa)
- ✅ **Tratamento de Erros**: Respostas padronizadas e feedback visual
- ✅ **Sistema Completo de Relatórios**: Exportação em PDF, Excel e CSV

### Busca Inteligente 🆕
- ✅ **Busca Fuzzy**: Tolerante a erros de digitação ("arrz" encontra "arroz")
- ✅ **Auto-seleção**: Seleciona automaticamente o primeiro resultado
- ✅ **Comparação Automática**: Para resultados únicos de busca
- ✅ **Debounce**: Busca otimizada com delay de 300ms
- ✅ **Highlights**: Destaque visual dos termos encontrados
- ✅ **Produtos com Preços**: Filtra apenas produtos que têm preços cadastrados

### Interface AdminLTE 🆕
- ✅ **Design Moderno**: AdminLTE 3.x com Bootstrap 4
- ✅ **Menu Lateral**: Navegação colapsível com ícones FontAwesome
- ✅ **Cards Modernos**: Layout em cards para melhor organização
- ✅ **Responsividade Total**: Adaptado para mobile, tablet e desktop
- ✅ **Consistência Visual**: Padrão profissional em todas as páginas

### Dashboard e Analytics
- ✅ **Estatísticas**: Totais e rankings do sistema
- ✅ **Comparação Inteligente**: Preços ordenados do mais barato ao mais caro
- ✅ **Destaque do Melhor Preço**: Visual diferenciado para menor preço
- ✅ **Estatísticas de Economia**: Valor e percentual de economia
- ✅ **Performance**: Cache e rate limiting implementados
- ✅ **Interface Dedicada**: Página de relatórios AdminLTE

## 🚀 Tecnologias

- **Backend**: Flask + SQLAlchemy + RapidFuzz
- **Banco de Dados**: SQLite
- **Frontend**: AdminLTE 3.x + Bootstrap 4 + FontAwesome
- **Interface**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: REST JSON
- **Cache**: Flask-Caching (60s consultas, 30s preços)
- **Rate Limiting**: Flask-Limiter (30 req/min buscas, 20 req/min preços)
- **Busca**: RapidFuzz para busca fuzzy tolerante a erros
- **Relatórios**: ReportLab (PDF), XlsxWriter (Excel), CSV nativo
- **UI Framework**: AdminLTE para interface moderna e responsiva

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd PromoPreço
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação**
```bash
python app.py
```

4. **Acesse no navegador**
```
http://localhost:5000
```

## ⚙️ Validações e Regras de Negócio

### Validações Implementadas

#### Produtos
- **Descrição**: Campo obrigatório, não pode ser vazio
- **EAN**: Opcional, mas se informado deve ter exatamente 13 dígitos numéricos
- **Formato aceito**: Remove automaticamente caracteres não numéricos

#### Estabelecimentos
- **Nome**: Campo obrigatório, não pode ser vazio
- **Bairro**: Campo obrigatório, não pode ser vazio (✅ **CORRIGIDO**: Adicionado ao formulário)
- **Cidade**: Campo obrigatório, não pode ser vazio (✅ **CORRIGIDO**: Adicionado ao formulário)
- **CNPJ**: Opcional, mas se informado deve ter exatamente 14 dígitos numéricos
- **Formato aceito**: Remove automaticamente caracteres não numéricos (pontos, barras, hífens)

#### Preços
- **Produto**: Campo obrigatório, deve referenciar um produto existente
- **Estabelecimento**: Campo obrigatório, deve referenciar um estabelecimento existente
- **Preço**: Campo obrigatório, deve ser um número maior que zero
- **Data de Coleta**: Preenchida automaticamente com timestamp UTC

### Tratamento de Erros
- **400 Bad Request**: Dados inválidos ou campos obrigatórios ausentes
- **404 Not Found**: Recurso não encontrado para edição/exclusão
- **500 Internal Server Error**: Erros de banco de dados ou servidor

### Exemplos de Respostas de Erro
```json
{
  "error": "Descrição é obrigatória"
}
```

```json
{
  "error": "EAN deve ter 13 dígitos"
}
```

```json
{
  "error": "Preço deve ser maior que zero"
}
```

## 🔧 Uso

### Interface Web
Acesse `http://localhost:5000` para a interface principal AdminLTE.

**Interfaces disponíveis:**
- `/` - Dashboard AdminLTE (principal)
- `/cadastros` - Cadastros AdminLTE
- `/relatorios` - Relatórios AdminLTE
- `/dashboard` - Dashboard clássico (alternativo)
- `/dashboard/adminlte` - Dashboard AdminLTE (alternativo)

### API Endpoints

#### Produtos
- `GET /produtos` - Lista todos os produtos
- `GET /produtos?q=<termo>` - Busca fuzzy de produtos
- `GET /produtos/com-precos` - Lista apenas produtos com preços cadastrados
- `GET /produtos/com-precos?q=<termo>` - Busca fuzzy em produtos com preços
- `POST /produtos` - Cria novo produto
- `PUT /produtos/<id>` - Edita produto existente
- `DELETE /produtos/<id>` - Exclui produto
```json
{
  "descricao": "Produto Exemplo",
  "ean": "1234567890123"
}
```

#### Estabelecimentos
- `GET /estabelecimentos` - Lista todos os estabelecimentos
- `POST /estabelecimentos` - Cria novo estabelecimento
- `PUT /estabelecimentos/<id>` - Edita estabelecimento existente
- `DELETE /estabelecimentos/<id>` - Exclui estabelecimento
```json
{
  "nome": "Supermercado Exemplo",
  "cnpj": "12345678000199",
  "bairro": "Centro",
  "cidade": "São Paulo"
}
```

#### Preços
- `GET /precos` - Lista todos os preços (com filtros e paginação)
- `GET /precos/detalhados` - Lista preços com dados completos (✅ **CORRIGIDO**: Usado na interface)
- `POST /precos` - Registra novo preço
- `PUT /precos/<id>` - Edita preço existente
- `DELETE /precos/<id>` - Exclui preço

**Parâmetros de busca:**
- `produto_id` - Filtrar por produto específico
- `estabelecimento_id` - Filtrar por estabelecimento
- `preco_min` - Preço mínimo
- `preco_max` - Preço máximo
- `page` - Página (padrão: 1)
- `per_page` - Itens por página (padrão: 10)

```json
{
  "produto_id": 1,
  "estabelecimento_id": 1,
  "preco": 15.99
}
```

#### Dashboard e Relatórios
- `GET /dashboard/stats` - Estatísticas gerais do sistema
- `GET /comparar/<produto_id>` - Compara preços de um produto (ordenado por preço)
- `GET /comparar?q=<termo>` - Comparação com busca fuzzy
- `GET /api/historico-precos/<produto_id>` - Histórico de preços
- `GET /api/relatorio-precos` - Relatório geral com filtros
- `GET /precos/ordenados` - Preços com ordenação avançada
- `GET /api/estatisticas-avancadas` - Estatísticas para gráficos

**Exemplo de resposta das estatísticas:**
```json
{
  "totais": {
    "produtos": 150,
    "estabelecimentos": 25,
    "precos": 500
  },
  "produto_mais_precos": {
    "nome": "Arroz Tipo 1 5kg",
    "total": 12
  },
  "estabelecimento_mais_precos": {
    "nome": "Supermercado Central",
    "total": 45
  }
}
```

## 📁 Estrutura do Projeto

```
PromoPreço/
├── app.py                    # Aplicação Flask + AdminLTE + Relatórios
├── requirements.txt          # Dependências Python
├── templates/                # Templates HTML
│   ├── base_adminlte.html    # Template base AdminLTE
│   ├── cadastros_adminlte.html # Cadastros AdminLTE
│   ├── dashboard_adminlte.html # Dashboard AdminLTE
│   ├── relatorios_adminlte.html # Relatórios AdminLTE
│   ├── cadastros.html        # Interface clássica
│   ├── dashboard.html        # Dashboard clássico
│   └── relatorios.html       # Relatórios clássicos
├── Testes/                   # Scripts de teste
├── instance/                 # Dados da aplicação
│   └── promoprecco.db        # Banco SQLite
├── .amazonq/rules/           # Regras do projeto
├── ADMINLTE_GUIDE.md         # Guia do AdminLTE
├── ROADMAP.md               # Roadmap do projeto
└── README.md                # Este arquivo
```

## 🗄️ Modelo de Dados

### Produto
- `id`: Identificador único (auto-increment)
- `descricao`: Descrição do produto (obrigatório)
- `ean`: Código de barras EAN-13 (opcional, validado)

### Estabelecimento
- `id`: Identificador único (auto-increment)
- `nome`: Nome do estabelecimento (obrigatório)
- `cnpj`: CNPJ com 14 dígitos (opcional, validado)
- `bairro`: Bairro do estabelecimento (obrigatório)
- `cidade`: Cidade do estabelecimento (obrigatório)

### Preço
- `id`: Identificador único (auto-increment)
- `produto_id`: Referência ao produto (FK, obrigatório)
- `estabelecimento_id`: Referência ao estabelecimento (FK, obrigatório)
- `preco`: Valor numérico (obrigatório, > 0)
- `data_coleta`: Timestamp automático (UTC)

## 🏗️ Arquitetura

### Padrão Arquitetural
O sistema segue uma arquitetura **MVC simplificada** com API REST:

- **Model**: Classes SQLAlchemy (Produto, Estabelecimento, Preço)
- **View**: Templates HTML + JavaScript para interface
- **Controller**: Rotas Flask com lógica de negócio
- **API**: Endpoints REST JSON para integração

### Fluxo de Dados
```
Frontend (HTML/JS) → API REST (Flask) → ORM (SQLAlchemy) → Database (SQLite)
```

### Componentes Principais

#### Backend (Flask)
- **Rotas de API**: CRUD completo para todas entidades
- **Validações**: Regras de negócio no servidor
- **ORM**: SQLAlchemy para abstração do banco
- **Serialização**: JSON para comunicação com frontend

#### Frontend (Vanilla JS)
- **Interface Responsiva**: CSS Grid/Flexbox
- **AJAX**: Fetch API para comunicação com backend
- **Validação**: Validação básica no cliente + servidor
- **UX**: Feedback visual para ações do usuário

#### Banco de Dados
- **SQLite**: Banco embarcado para desenvolvimento
- **Relacionamentos**: Foreign keys com integridade referencial
- **Migrações**: SQLAlchemy para evolução do schema

### Segurança Atual
- **Validação de Entrada**: Sanitização de dados no backend
- **SQL Injection**: Proteção via ORM SQLAlchemy
- **CORS**: Configurado para desenvolvimento local

**Nota**: Para produção, implementar autenticação, HTTPS e rate limiting.

## 🛣️ Roadmap

Consulte o arquivo [ROADMAP.md](ROADMAP.md) para ver as próximas funcionalidades planejadas:

- **✅ Fase 1**: MVP com cadastros básicos
- **✅ Fase 2**: Validações e CRUD completo
- **✅ Fase 3**: Dashboard, relatórios e busca avançada
- **🔄 Fase 4**: Sistema de usuários e geolocalização
- **Fase 5**: App mobile e integrações
- **Fase 6**: Segurança e performance
- **Fase 7**: Deploy em produção

## 🤝 Contribuição

### Como Contribuir

1. **Fork do Projeto**
   ```bash
   git clone <seu-fork>
   cd PromoPreço
   ```

2. **Configuração do Ambiente**
   ```bash
   pip install -r requirements.txt
   python app.py  # Testa se tudo funciona
   ```

3. **Crie uma Branch**
   ```bash
   git checkout -b feature/nova-funcionalidade
   # ou
   git checkout -b fix/correcao-bug
   ```

4. **Desenvolva e Teste**
   - Siga as convenções de código existentes
   - Teste suas alterações localmente
   - Adicione validações quando necessário

5. **Commit e Push**
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   git push origin feature/nova-funcionalidade
   ```

6. **Pull Request**
   - Descreva claramente as mudanças
   - Referencie issues relacionadas
   - Inclua screenshots se aplicável

### Convenções

#### Commits
Use o padrão [Conventional Commits](https://conventionalcommits.org/):
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Atualização de documentação
- `style:` - Formatação, sem mudança de lógica
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes

#### Código Python
- Siga PEP 8 para formatação
- Use nomes descritivos para variáveis e funções
- Adicione docstrings para funções complexas
- Mantenha funções pequenas e focadas

#### Frontend
- Use nomes de classes CSS descritivos
- Mantenha JavaScript organizado e comentado
- Teste em diferentes navegadores

### Áreas que Precisam de Ajuda
- **Testes**: Implementação de testes unitários
- **UI/UX**: Melhorias na interface do usuário
- **Performance**: Otimizações de consultas
- **Documentação**: Exemplos e tutoriais
- **Mobile**: Responsividade e PWA

### Reportar Bugs
Ao reportar bugs, inclua:
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots/logs quando possível
- Versão do Python e navegador

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🎯 Dashboard e Analytics

### Funcionalidades do Dashboard
Acesse `/dashboard` para visualizar:

- **Estatísticas Gerais**: Total de produtos, estabelecimentos e preços cadastrados
- **Rankings**: Produtos e estabelecimentos com mais registros
- **Comparação de Preços**: Visualize todos os preços de um produto específico
- **Busca Avançada**: Filtros por faixa de preço, produto e estabelecimento

### Comparação de Preços
Use o endpoint `/comparar/<produto_id>` para obter uma lista ordenada dos preços de um produto em diferentes estabelecimentos, facilitando a identificação das melhores ofertas.

## 🔧 Utilitários

### Scripts de Banco de Dados
- `reset_db.py` - Reseta o banco mantendo a estrutura
- `force_reset.py` - Reseta completamente o banco
- `migrate_db.py` - Executa migrações do banco
- `populate_test_data.py` - Popula com dados de teste

### Executar Scripts
```bash
# Reset suave (mantém estrutura)
python reset_db.py

# Reset completo
python force_reset.py

# Adicionar dados de teste
python populate_test_data.py
```

## 📈 Relatórios e Exportação

### Funcionalidades de Relatórios
- **Histórico de Preços**: Acompanhe a variação de preços ao longo do tempo
- **Relatório Geral**: Filtre por produto, estabelecimento, faixa de preço e período
- **Exportação Múltipla**: PDF, Excel e CSV
- **Ordenação Avançada**: Por preço, produto, estabelecimento ou data
- **Estatísticas Avançadas**: Top produtos, estabelecimentos e variações

### Formatos de Exportação
- **PDF**: Relatórios formatados com tabelas e cabeçalhos
- **Excel**: Planilhas com dados estruturados
- **CSV**: Formato universal para análise de dados

### Endpoints de Relatórios
```bash
# Histórico de preços (30 dias)
GET /api/historico-precos/1?dias=30

# Relatório em PDF
GET /api/relatorio-precos?formato=pdf&dias=7

# Relatório em Excel
GET /api/relatorio-precos?formato=excel&produto_id=1

# Estatísticas avançadas
GET /api/estatisticas-avancadas
```

## ✨ Melhorias Recentes

### Interface AdminLTE (Mais Recente) 🆕
- **AdminLTE 3.x**: Interface moderna e profissional implementada
- **Múltiplas Interfaces**: Suporte a AdminLTE e interface clássica
- **Design Responsivo**: Totalmente adaptado para todos os dispositivos
- **Menu Lateral**: Navegação colapsível com ícones FontAwesome
- **Cards Modernos**: Layout organizado em cards para melhor UX
- **Consistência Visual**: Padrão profissional em todas as páginas

### Funcionalidades Core Implementadas
- **Busca Fuzzy**: Implementada com RapidFuzz para tolerância a erros
- **Auto-seleção**: Primeiro resultado selecionado automaticamente
- **Comparação Automática**: Para buscas com resultado único
- **Produtos com Preços**: Nova rota que filtra apenas produtos com preços
- **Performance**: Cache inteligente e rate limiting
- **UX Melhorada**: Feedback visual, highlights e animações
- **Dashboard Inteligente**: Ordenação automática e estatísticas de economia
- **Sistema Completo de Relatórios**: Exportação em PDF, Excel e CSV
- **Histórico de Preços**: Acompanhamento temporal por produto
- **Ordenação Avançada**: Múltiplos critérios de ordenação
- **Estatísticas Avançadas**: Dados para gráficos e análises

## 🐛 Troubleshooting

### Problemas Comuns

**Erro de banco de dados não encontrado:**
```bash
python app.py  # Cria automaticamente o banco na primeira execução
```

**Erro de dependências:**
```bash
pip install --upgrade -r requirements.txt
```

**Porta 5000 já em uso:**
```bash
# Altere a porta no final do app.py
app.run(debug=True, port=5001)
```

**Problemas de CORS (desenvolvimento frontend separado):**
```bash
pip install flask-cors
# Adicione no app.py: from flask_cors import CORS; CORS(app)
```

### Logs e Debug
Para ativar logs detalhados, execute com:
```bash
FLASK_ENV=development python app.py
```

## 🧪 Testes

### Testando a API
Use ferramentas como Postman, Insomnia ou curl:

```bash
# Testar status da API
curl http://localhost:5000/api

# Listar produtos
curl http://localhost:5000/produtos

# Criar produto
curl -X POST http://localhost:5000/produtos \
  -H "Content-Type: application/json" \
  -d '{"descricao":"Teste","ean":"1234567890123"}'
```

### Dados de Teste
Execute `python populate_test_data.py` para adicionar dados de exemplo e testar todas as funcionalidades.

## 📊 Performance

### Otimizações Implementadas
- **Paginação**: Listagens de preços com paginação automática (10 itens por página)
- **Índices**: Foreign keys indexadas automaticamente pelo SQLAlchemy
- **Validações**: Validações no backend reduzem consultas desnecessárias
- **Consultas Otimizadas**: JOINs eficientes para dashboard e comparações
- **Cache Inteligente**: 60s para consultas gerais, 30s para preços detalhados
- **Rate Limiting**: 30 req/min para buscas, 20 req/min para preços detalhados
- **Busca Fuzzy**: RapidFuzz com score mínimo de 60% para relevância
- **Debounce**: 300ms para otimizar requisições de busca
- **Sanitização**: Proteção contra XSS e SQL injection
- **Performance Monitoring**: Logs para queries lentas (>0.5s)

### Limites Atuais
- **Banco**: SQLite adequado para desenvolvimento e pequenos volumes (<100k registros)
- **Cache**: Sem sistema de cache, consultas executadas diretamente no banco
- **Autenticação**: Acesso livre a todos os endpoints (adequado para desenvolvimento)
- **Concorrência**: SQLite com limitações para múltiplos usuários simultâneos

### Recomendações para Produção
- Migrar para PostgreSQL para melhor performance
- Implementar Redis para cache de consultas frequentes
- Adicionar autenticação e autorização
- Configurar índices customizados para consultas específicas

## 📈 Estatísticas do Projeto

### Status Atual
- **Linhas de Código**: ~1200+ (Python + HTML + CSS + JS + AdminLTE)
- **Cobertura de Testes**: 0% (próxima fase)
- **Endpoints API**: 20+ endpoints funcionais
- **Modelos de Dados**: 3 entidades principais
- **Validações**: 8 regras de negócio implementadas
- **Interfaces**: 2 interfaces completas (AdminLTE + clássica)
- **Funcionalidades Avançadas**: AdminLTE, busca fuzzy, cache, rate limiting, auto-seleção, relatórios completos

### Tecnologias e Versões
- **Python**: 3.8+
- **Flask**: 2.3+
- **SQLAlchemy**: 2.0+
- **RapidFuzz**: 3.5+ (busca fuzzy)
- **Flask-Caching**: 2.1+ (cache)
- **Flask-Limiter**: 3.5+ (rate limiting)
- **SQLite**: 3.x
- **HTML5/CSS3/ES6**: Padrões modernos

## 📞 Suporte e Contato

### Canais de Suporte
- **Issues**: Para bugs e solicitações de features
- **Discussions**: Para dúvidas e discussões gerais
- **Wiki**: Documentação adicional e tutoriais

### FAQ

**P: Como adicionar novos campos aos modelos?**
R: Edite as classes no `app.py`, execute `python migrate_db.py` e atualize os formulários HTML.

**P: Como fazer backup dos dados?**
R: Copie o arquivo `instance/promoprecco.db` para local seguro.

**P: Posso usar com PostgreSQL?**
R: Sim, altere a `SQLALCHEMY_DATABASE_URI` no `app.py` e instale `psycopg2`.

**P: Como contribuir sem conhecimento técnico?**
R: Reporte bugs, sugira melhorias, teste a aplicação e compartilhe feedback.

### Links Úteis
- [Roadmap Detalhado](ROADMAP.md)
- [Regras do Projeto](.amazonq/rules/RegrasPromoPreco.md)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
# Guia de Implementação AdminLTE - PromoPreço

## 1. Estrutura Base

### 1.1 Template Base (base_adminlte.html)
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}PromoPreço{% endblock %}</title>
    
    <!-- AdminLTE CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte.min.css">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="hold-transition sidebar-mini">
    <div class="wrapper">
        <!-- Navbar -->
        <nav class="main-header navbar navbar-expand navbar-white navbar-light">
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link" data-widget="pushmenu" href="#" role="button"><i class="fas fa-bars"></i></a>
                </li>
            </ul>
            <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                    <span class="navbar-text">PromoPreço v1.0</span>
                </li>
            </ul>
        </nav>

        <!-- Sidebar -->
        <aside class="main-sidebar sidebar-dark-primary elevation-4">
            <a href="/" class="brand-link">
                <i class="fas fa-tags brand-image"></i>
                <span class="brand-text font-weight-light">PromoPreço</span>
            </a>
            
            <div class="sidebar">
                <nav class="mt-2">
                    <ul class="nav nav-pills nav-sidebar flex-column" data-widget="treeview">
                        <li class="nav-item">
                            <a href="/dashboard" class="nav-link">
                                <i class="nav-icon fas fa-tachometer-alt"></i>
                                <p>Dashboard</p>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="/cadastros" class="nav-link">
                                <i class="nav-icon fas fa-plus-circle"></i>
                                <p>Cadastros</p>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="/relatorios" class="nav-link">
                                <i class="nav-icon fas fa-chart-bar"></i>
                                <p>Relatórios</p>
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
        </aside>

        <!-- Content -->
        <div class="content-wrapper">
            <div class="content-header">
                <div class="container-fluid">
                    <div class="row mb-2">
                        <div class="col-sm-6">
                            <h1 class="m-0">{% block page_title %}{% endblock %}</h1>
                        </div>
                    </div>
                </div>
            </div>
            
            <section class="content">
                <div class="container-fluid">
                    {% block content %}{% endblock %}
                </div>
            </section>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/js/adminlte.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

## 2. Dashboard AdminLTE

### 2.1 Template Dashboard (dashboard_adminlte.html)
```html
{% extends "base_adminlte.html" %}

{% block title %}Dashboard - PromoPreço{% endblock %}
{% block page_title %}Dashboard{% endblock %}

{% block content %}
<!-- Cards de Estatísticas -->
<div class="row">
    <div class="col-lg-3 col-6">
        <div class="small-box bg-info">
            <div class="inner">
                <h3 id="total-produtos">{{ total_produtos }}</h3>
                <p>Produtos Cadastrados</p>
            </div>
            <div class="icon">
                <i class="fas fa-box"></i>
            </div>
        </div>
    </div>
    
    <div class="col-lg-3 col-6">
        <div class="small-box bg-success">
            <div class="inner">
                <h3 id="total-lojas">{{ total_lojas }}</h3>
                <p>Lojas Monitoradas</p>
            </div>
            <div class="icon">
                <i class="fas fa-store"></i>
            </div>
        </div>
    </div>
    
    <div class="col-lg-3 col-6">
        <div class="small-box bg-warning">
            <div class="inner">
                <h3 id="promocoes-ativas">{{ promocoes_ativas }}</h3>
                <p>Promoções Ativas</p>
            </div>
            <div class="icon">
                <i class="fas fa-percentage"></i>
            </div>
        </div>
    </div>
    
    <div class="col-lg-3 col-6">
        <div class="small-box bg-danger">
            <div class="inner">
                <h3 id="alertas">{{ alertas }}</h3>
                <p>Alertas</p>
            </div>
            <div class="icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
        </div>
    </div>
</div>

<!-- Gráficos -->
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Preços por Período</h3>
            </div>
            <div class="card-body">
                <canvas id="precoChart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Produtos Mais Monitorados</h3>
            </div>
            <div class="card-body">
                <canvas id="produtosChart"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- Tabela de Últimas Atualizações -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Últimas Atualizações de Preços</h3>
            </div>
            <div class="card-body table-responsive p-0">
                <table class="table table-hover text-nowrap">
                    <thead>
                        <tr>
                            <th>Produto</th>
                            <th>Loja</th>
                            <th>Preço Anterior</th>
                            <th>Preço Atual</th>
                            <th>Variação</th>
                            <th>Data</th>
                        </tr>
                    </thead>
                    <tbody id="ultimas-atualizacoes">
                        <!-- Dados carregados via JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Configuração dos gráficos
const precoCtx = document.getElementById('precoChart').getContext('2d');
const produtosCtx = document.getElementById('produtosChart').getContext('2d');

// Gráfico de preços
const precoChart = new Chart(precoCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Preço Médio',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    }
});

// Gráfico de produtos
const produtosChart = new Chart(produtosCtx, {
    type: 'doughnut',
    data: {
        labels: [],
        datasets: [{
            data: [],
            backgroundColor: [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF'
            ]
        }]
    },
    options: {
        responsive: true
    }
});

// Função para carregar dados do dashboard
function carregarDashboard() {
    fetch('/api/dashboard')
        .then(response => response.json())
        .then(data => {
            // Atualizar cards
            document.getElementById('total-produtos').textContent = data.total_produtos;
            document.getElementById('total-lojas').textContent = data.total_lojas;
            document.getElementById('promocoes-ativas').textContent = data.promocoes_ativas;
            document.getElementById('alertas').textContent = data.alertas;
            
            // Atualizar gráfico de preços
            precoChart.data.labels = data.precos_periodo.labels;
            precoChart.data.datasets[0].data = data.precos_periodo.data;
            precoChart.update();
            
            // Atualizar gráfico de produtos
            produtosChart.data.labels = data.produtos_monitorados.labels;
            produtosChart.data.datasets[0].data = data.produtos_monitorados.data;
            produtosChart.update();
            
            // Atualizar tabela
            const tbody = document.getElementById('ultimas-atualizacoes');
            tbody.innerHTML = '';
            data.ultimas_atualizacoes.forEach(item => {
                const row = `
                    <tr>
                        <td>${item.produto}</td>
                        <td>${item.loja}</td>
                        <td>R$ ${item.preco_anterior}</td>
                        <td>R$ ${item.preco_atual}</td>
                        <td class="${item.variacao > 0 ? 'text-danger' : 'text-success'}">
                            ${item.variacao > 0 ? '+' : ''}${item.variacao}%
                        </td>
                        <td>${item.data}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(error => console.error('Erro ao carregar dashboard:', error));
}

// Carregar dados ao inicializar
document.addEventListener('DOMContentLoaded', carregarDashboard);

// Atualizar a cada 5 minutos
setInterval(carregarDashboard, 300000);
</script>
{% endblock %}
```

## 3. Cadastros AdminLTE

### 3.1 Template Cadastros (cadastros_adminlte.html)
```html
{% extends "base_adminlte.html" %}

{% block title %}Cadastros - PromoPreço{% endblock %}
{% block page_title %}Cadastros{% endblock %}

{% block content %}
<div class="row">
    <!-- Cadastro de Produtos -->
    <div class="col-md-6">
        <div class="card card-primary">
            <div class="card-header">
                <h3 class="card-title">Cadastrar Produto</h3>
            </div>
            <form id="form-produto">
                <div class="card-body">
                    <div class="form-group">
                        <label for="nome-produto">Nome do Produto</label>
                        <input type="text" class="form-control" id="nome-produto" required>
                    </div>
                    <div class="form-group">
                        <label for="categoria-produto">Categoria</label>
                        <select class="form-control" id="categoria-produto" required>
                            <option value="">Selecione uma categoria</option>
                            <option value="eletronicos">Eletrônicos</option>
                            <option value="casa">Casa e Jardim</option>
                            <option value="moda">Moda</option>
                            <option value="esportes">Esportes</option>
                            <option value="livros">Livros</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="descricao-produto">Descrição</label>
                        <textarea class="form-control" id="descricao-produto" rows="3"></textarea>
                    </div>
                </div>
                <div class="card-footer">
                    <button type="submit" class="btn btn-primary">Cadastrar Produto</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Cadastro de Lojas -->
    <div class="col-md-6">
        <div class="card card-success">
            <div class="card-header">
                <h3 class="card-title">Cadastrar Loja</h3>
            </div>
            <form id="form-loja">
                <div class="card-body">
                    <div class="form-group">
                        <label for="nome-loja">Nome da Loja</label>
                        <input type="text" class="form-control" id="nome-loja" required>
                    </div>
                    <div class="form-group">
                        <label for="url-loja">URL da Loja</label>
                        <input type="url" class="form-control" id="url-loja" required>
                    </div>
                    <div class="form-group">
                        <label for="tipo-loja">Tipo</label>
                        <select class="form-control" id="tipo-loja" required>
                            <option value="">Selecione o tipo</option>
                            <option value="marketplace">Marketplace</option>
                            <option value="loja_fisica">Loja Física</option>
                            <option value="e-commerce">E-commerce</option>
                        </select>
                    </div>
                </div>
                <div class="card-footer">
                    <button type="submit" class="btn btn-success">Cadastrar Loja</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Associar Produto à Loja -->
<div class="row">
    <div class="col-12">
        <div class="card card-warning">
            <div class="card-header">
                <h3 class="card-title">Associar Produto à Loja</h3>
            </div>
            <form id="form-associacao">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-group">
                                <label for="select-produto">Produto</label>
                                <select class="form-control" id="select-produto" required>
                                    <option value="">Selecione um produto</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label for="select-loja">Loja</label>
                                <select class="form-control" id="select-loja" required>
                                    <option value="">Selecione uma loja</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label for="url-produto">URL do Produto na Loja</label>
                                <input type="url" class="form-control" id="url-produto" required>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="preco-inicial">Preço Inicial</label>
                                <input type="number" step="0.01" class="form-control" id="preco-inicial" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="preco-alvo">Preço Alvo (Alerta)</label>
                                <input type="number" step="0.01" class="form-control" id="preco-alvo">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <button type="submit" class="btn btn-warning">Associar</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Lista de Produtos Cadastrados -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Produtos Cadastrados</h3>
            </div>
            <div class="card-body table-responsive p-0">
                <table class="table table-hover text-nowrap">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Categoria</th>
                            <th>Lojas</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="lista-produtos">
                        <!-- Dados carregados via JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Carregar dados iniciais
document.addEventListener('DOMContentLoaded', function() {
    carregarProdutos();
    carregarLojas();
    carregarListaProdutos();
});

// Cadastro de produto
document.getElementById('form-produto').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const dados = {
        nome: document.getElementById('nome-produto').value,
        categoria: document.getElementById('categoria-produto').value,
        descricao: document.getElementById('descricao-produto').value
    };
    
    fetch('/api/produtos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Produto cadastrado com sucesso!');
            this.reset();
            carregarProdutos();
            carregarListaProdutos();
        } else {
            alert('Erro ao cadastrar produto: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao cadastrar produto');
    });
});

// Cadastro de loja
document.getElementById('form-loja').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const dados = {
        nome: document.getElementById('nome-loja').value,
        url: document.getElementById('url-loja').value,
        tipo: document.getElementById('tipo-loja').value
    };
    
    fetch('/api/lojas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Loja cadastrada com sucesso!');
            this.reset();
            carregarLojas();
        } else {
            alert('Erro ao cadastrar loja: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao cadastrar loja');
    });
});

// Associação produto-loja
document.getElementById('form-associacao').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const dados = {
        produto_id: document.getElementById('select-produto').value,
        loja_id: document.getElementById('select-loja').value,
        url_produto: document.getElementById('url-produto').value,
        preco_inicial: document.getElementById('preco-inicial').value,
        preco_alvo: document.getElementById('preco-alvo').value
    };
    
    fetch('/api/produto-loja', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Associação criada com sucesso!');
            this.reset();
            carregarListaProdutos();
        } else {
            alert('Erro ao criar associação: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao criar associação');
    });
});

// Funções auxiliares
function carregarProdutos() {
    fetch('/api/produtos')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('select-produto');
            select.innerHTML = '<option value="">Selecione um produto</option>';
            data.forEach(produto => {
                select.innerHTML += `<option value="${produto.id}">${produto.nome}</option>`;
            });
        });
}

function carregarLojas() {
    fetch('/api/lojas')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('select-loja');
            select.innerHTML = '<option value="">Selecione uma loja</option>';
            data.forEach(loja => {
                select.innerHTML += `<option value="${loja.id}">${loja.nome}</option>`;
            });
        });
}

function carregarListaProdutos() {
    fetch('/api/produtos-completo')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('lista-produtos');
            tbody.innerHTML = '';
            data.forEach(produto => {
                const row = `
                    <tr>
                        <td>${produto.id}</td>
                        <td>${produto.nome}</td>
                        <td>${produto.categoria}</td>
                        <td>${produto.lojas_count} loja(s)</td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="editarProduto(${produto.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="excluirProduto(${produto.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}

function editarProduto(id) {
    // Implementar edição
    alert('Funcionalidade de edição em desenvolvimento');
}

function excluirProduto(id) {
    if (confirm('Tem certeza que deseja excluir este produto?')) {
        fetch(`/api/produtos/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Produto excluído com sucesso!');
                carregarListaProdutos();
                carregarProdutos();
            } else {
                alert('Erro ao excluir produto: ' + data.message);
            }
        });
    }
}
</script>
{% endblock %}
```

## 4. Relatórios AdminLTE

### 4.1 Template Relatórios (relatorios_adminlte.html)
```html
{% extends "base_adminlte.html" %}

{% block title %}Relatórios - PromoPreço{% endblock %}
{% block page_title %}Relatórios{% endblock %}

{% block content %}
<!-- Filtros -->
<div class="row">
    <div class="col-12">
        <div class="card card-info">
            <div class="card-header">
                <h3 class="card-title">Filtros</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="filtro-produto">Produto</label>
                            <select class="form-control" id="filtro-produto">
                                <option value="">Todos os produtos</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="filtro-loja">Loja</label>
                            <select class="form-control" id="filtro-loja">
                                <option value="">Todas as lojas</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="filtro-data-inicio">Data Início</label>
                            <input type="date" class="form-control" id="filtro-data-inicio">
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="filtro-data-fim">Data Fim</label>
                            <input type="date" class="form-control" id="filtro-data-fim">
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <button class="btn btn-primary" onclick="aplicarFiltros()">
                            <i class="fas fa-search"></i> Aplicar Filtros
                        </button>
                        <button class="btn btn-secondary" onclick="limparFiltros()">
                            <i class="fas fa-eraser"></i> Limpar
                        </button>
                        <button class="btn btn-success" onclick="exportarRelatorio()">
                            <i class="fas fa-download"></i> Exportar CSV
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Gráfico de Evolução de Preços -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Evolução de Preços</h3>
            </div>
            <div class="card-body">
                <canvas id="evolucaoChart" height="100"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- Estatísticas -->
<div class="row">
    <div class="col-md-3">
        <div class="info-box">
            <span class="info-box-icon bg-info"><i class="fas fa-chart-line"></i></span>
            <div class="info-box-content">
                <span class="info-box-text">Menor Preço</span>
                <span class="info-box-number" id="menor-preco">R$ 0,00</span>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="info-box">
            <span class="info-box-icon bg-success"><i class="fas fa-chart-line"></i></span>
            <div class="info-box-content">
                <span class="info-box-text">Maior Preço</span>
                <span class="info-box-number" id="maior-preco">R$ 0,00</span>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="info-box">
            <span class="info-box-icon bg-warning"><i class="fas fa-calculator"></i></span>
            <div class="info-box-content">
                <span class="info-box-text">Preço Médio</span>
                <span class="info-box-number" id="preco-medio">R$ 0,00</span>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="info-box">
            <span class="info-box-icon bg-danger"><i class="fas fa-percentage"></i></span>
            <div class="info-box-content">
                <span class="info-box-text">Variação</span>
                <span class="info-box-number" id="variacao">0%</span>
            </div>
        </div>
    </div>
</div>

<!-- Tabela de Histórico -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Histórico de Preços</h3>
            </div>
            <div class="card-body table-responsive p-0">
                <table class="table table-hover text-nowrap" id="tabela-historico">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Produto</th>
                            <th>Loja</th>
                            <th>Preço</th>
                            <th>Variação</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Dados carregados via JavaScript -->
                    </tbody>
                </table>
            </div>
            <div class="card-footer">
                <div class="row">
                    <div class="col-sm-12 col-md-5">
                        <div class="dataTables_info">
                            Mostrando <span id="info-inicio">0</span> a <span id="info-fim">0</span> de <span id="info-total">0</span> registros
                        </div>
                    </div>
                    <div class="col-sm-12 col-md-7">
                        <div class="dataTables_paginate">
                            <ul class="pagination" id="paginacao">
                                <!-- Paginação gerada via JavaScript -->
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let evolucaoChart;
let paginaAtual = 1;
let itensPorPagina = 10;

document.addEventListener('DOMContentLoaded', function() {
    inicializarGrafico();
    carregarFiltros();
    carregarRelatorio();
});

function inicializarGrafico() {
    const ctx = document.getElementById('evolucaoChart').getContext('2d');
    evolucaoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': R$ ' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

function carregarFiltros() {
    // Carregar produtos
    fetch('/api/produtos')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filtro-produto');
            data.forEach(produto => {
                select.innerHTML += `<option value="${produto.id}">${produto.nome}</option>`;
            });
        });

    // Carregar lojas
    fetch('/api/lojas')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('filtro-loja');
            data.forEach(loja => {
                select.innerHTML += `<option value="${loja.id}">${loja.nome}</option>`;
            });
        });

    // Definir datas padrão (últimos 30 dias)
    const hoje = new Date();
    const trintaDiasAtras = new Date(hoje.getTime() - (30 * 24 * 60 * 60 * 1000));
    
    document.getElementById('filtro-data-fim').value = hoje.toISOString().split('T')[0];
    document.getElementById('filtro-data-inicio').value = trintaDiasAtras.toISOString().split('T')[0];
}

function aplicarFiltros() {
    paginaAtual = 1;
    carregarRelatorio();
}

function limparFiltros() {
    document.getElementById('filtro-produto').value = '';
    document.getElementById('filtro-loja').value = '';
    document.getElementById('filtro-data-inicio').value = '';
    document.getElementById('filtro-data-fim').value = '';
    carregarRelatorio();
}

function carregarRelatorio() {
    const filtros = {
        produto_id: document.getElementById('filtro-produto').value,
        loja_id: document.getElementById('filtro-loja').value,
        data_inicio: document.getElementById('filtro-data-inicio').value,
        data_fim: document.getElementById('filtro-data-fim').value,
        pagina: paginaAtual,
        itens_por_pagina: itensPorPagina
    };

    const params = new URLSearchParams();
    Object.keys(filtros).forEach(key => {
        if (filtros[key]) params.append(key, filtros[key]);
    });

    fetch(`/api/relatorio-precos?${params}`)
        .then(response => response.json())
        .then(data => {
            atualizarGrafico(data.grafico);
            atualizarEstatisticas(data.estatisticas);
            atualizarTabela(data.historico);
            atualizarPaginacao(data.paginacao);
        })
        .catch(error => {
            console.error('Erro ao carregar relatório:', error);
        });
}

function atualizarGrafico(dadosGrafico) {
    evolucaoChart.data.labels = dadosGrafico.labels;
    evolucaoChart.data.datasets = dadosGrafico.datasets;
    evolucaoChart.update();
}

function atualizarEstatisticas(stats) {
    document.getElementById('menor-preco').textContent = `R$ ${stats.menor_preco.toFixed(2)}`;
    document.getElementById('maior-preco').textContent = `R$ ${stats.maior_preco.toFixed(2)}`;
    document.getElementById('preco-medio').textContent = `R$ ${stats.preco_medio.toFixed(2)}`;
    document.getElementById('variacao').textContent = `${stats.variacao.toFixed(1)}%`;
}

function atualizarTabela(historico) {
    const tbody = document.querySelector('#tabela-historico tbody');
    tbody.innerHTML = '';
    
    historico.forEach(item => {
        const variacao = item.variacao || 0;
        const statusClass = variacao > 0 ? 'text-danger' : variacao < 0 ? 'text-success' : 'text-muted';
        const statusIcon = variacao > 0 ? 'fa-arrow-up' : variacao < 0 ? 'fa-arrow-down' : 'fa-minus';
        
        const row = `
            <tr>
                <td>${new Date(item.data).toLocaleDateString('pt-BR')}</td>
                <td>${item.produto}</td>
                <td>${item.loja}</td>
                <td>R$ ${item.preco.toFixed(2)}</td>
                <td class="${statusClass}">
                    <i class="fas ${statusIcon}"></i>
                    ${variacao !== 0 ? Math.abs(variacao).toFixed(1) + '%' : '-'}
                </td>
                <td>
                    <span class="badge ${item.promocao ? 'badge-success' : 'badge-secondary'}">
                        ${item.promocao ? 'Promoção' : 'Normal'}
                    </span>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function atualizarPaginacao(paginacao) {
    document.getElementById('info-inicio').textContent = paginacao.inicio;
    document.getElementById('info-fim').textContent = paginacao.fim;
    document.getElementById('info-total').textContent = paginacao.total;
    
    const paginacaoEl = document.getElementById('paginacao');
    paginacaoEl.innerHTML = '';
    
    // Botão anterior
    if (paginacao.pagina_atual > 1) {
        paginacaoEl.innerHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="mudarPagina(${paginacao.pagina_atual - 1})">Anterior</a>
            </li>
        `;
    }
    
    // Páginas
    for (let i = Math.max(1, paginacao.pagina_atual - 2); 
         i <= Math.min(paginacao.total_paginas, paginacao.pagina_atual + 2); 
         i++) {
        const activeClass = i === paginacao.pagina_atual ? 'active' : '';
        paginacaoEl.innerHTML += `
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" onclick="mudarPagina(${i})">${i}</a>
            </li>
        `;
    }
    
    // Botão próximo
    if (paginacao.pagina_atual < paginacao.total_paginas) {
        paginacaoEl.innerHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="mudarPagina(${paginacao.pagina_atual + 1})">Próximo</a>
            </li>
        `;
    }
}

function mudarPagina(pagina) {
    paginaAtual = pagina;
    carregarRelatorio();
}

function exportarRelatorio() {
    const filtros = {
        produto_id: document.getElementById('filtro-produto').value,
        loja_id: document.getElementById('filtro-loja').value,
        data_inicio: document.getElementById('filtro-data-inicio').value,
        data_fim: document.getElementById('filtro-data-fim').value,
        formato: 'csv'
    };

    const params = new URLSearchParams();
    Object.keys(filtros).forEach(key => {
        if (filtros[key]) params.append(key, filtros[key]);
    });

    window.open(`/api/exportar-relatorio?${params}`, '_blank');
}
</script>
{% endblock %}
```

## 5. Implementação no Flask

### 5.1 Rotas AdminLTE no app.py
```python
# Rotas AdminLTE
@app.route('/dashboard')
def dashboard_adminlte():
    return render_template('dashboard_adminlte.html')

@app.route('/cadastros')
def cadastros_adminlte():
    return render_template('cadastros_adminlte.html')

@app.route('/relatorios')
def relatorios_adminlte():
    return render_template('relatorios_adminlte.html')

# APIs para Dashboard
@app.route('/api/dashboard')
def api_dashboard():
    try:
        # Estatísticas básicas
        total_produtos = db.session.query(Produto).count()
        total_lojas = db.session.query(Loja).count()
        
        # Promoções ativas (preços abaixo do alvo)
        promocoes_ativas = db.session.query(ProdutoLoja).join(HistoricoPreco).filter(
            HistoricoPreco.preco < ProdutoLoja.preco_alvo
        ).count()
        
        # Alertas (produtos sem atualização recente)
        data_limite = datetime.now() - timedelta(days=1)
        alertas = db.session.query(ProdutoLoja).filter(
            ~ProdutoLoja.id.in_(
                db.session.query(HistoricoPreco.produto_loja_id).filter(
                    HistoricoPreco.data_coleta >= data_limite
                )
            )
        ).count()
        
        # Dados para gráficos
        precos_periodo = obter_precos_periodo()
        produtos_monitorados = obter_produtos_monitorados()
        ultimas_atualizacoes = obter_ultimas_atualizacoes()
        
        return jsonify({
            'total_produtos': total_produtos,
            'total_lojas': total_lojas,
            'promocoes_ativas': promocoes_ativas,
            'alertas': alertas,
            'precos_periodo': precos_periodo,
            'produtos_monitorados': produtos_monitorados,
            'ultimas_atualizacoes': ultimas_atualizacoes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# APIs para Cadastros
@app.route('/api/produtos', methods=['GET', 'POST'])
def api_produtos():
    if request.method == 'GET':
        produtos = db.session.query(Produto).all()
        return jsonify([{
            'id': p.id,
            'nome': p.nome,
            'categoria': p.categoria,
            'descricao': p.descricao
        } for p in produtos])
    
    elif request.method == 'POST':
        try:
            dados = request.get_json()
            produto = Produto(
                nome=dados['nome'],
                categoria=dados['categoria'],
                descricao=dados.get('descricao', '')
            )
            db.session.add(produto)
            db.session.commit()
            return jsonify({'success': True, 'id': produto.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/lojas', methods=['GET', 'POST'])
def api_lojas():
    if request.method == 'GET':
        lojas = db.session.query(Loja).all()
        return jsonify([{
            'id': l.id,
            'nome': l.nome,
            'url': l.url,
            'tipo': l.tipo
        } for l in lojas])
    
    elif request.method == 'POST':
        try:
            dados = request.get_json()
            loja = Loja(
                nome=dados['nome'],
                url=dados['url'],
                tipo=dados['tipo']
            )
            db.session.add(loja)
            db.session.commit()
            return jsonify({'success': True, 'id': loja.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400

# APIs para Relatórios
@app.route('/api/relatorio-precos')
def api_relatorio_precos():
    try:
        # Parâmetros de filtro
        produto_id = request.args.get('produto_id')
        loja_id = request.args.get('loja_id')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        pagina = int(request.args.get('pagina', 1))
        itens_por_pagina = int(request.args.get('itens_por_pagina', 10))
        
        # Construir query
        query = db.session.query(HistoricoPreco).join(ProdutoLoja).join(Produto).join(Loja)
        
        if produto_id:
            query = query.filter(Produto.id == produto_id)
        if loja_id:
            query = query.filter(Loja.id == loja_id)
        if data_inicio:
            query = query.filter(HistoricoPreco.data_coleta >= data_inicio)
        if data_fim:
            query = query.filter(HistoricoPreco.data_coleta <= data_fim)
        
        # Paginação
        total = query.count()
        historico = query.order_by(HistoricoPreco.data_coleta.desc()).offset(
            (pagina - 1) * itens_por_pagina
        ).limit(itens_por_pagina).all()
        
        # Dados para gráfico
        grafico = gerar_dados_grafico(query)
        
        # Estatísticas
        estatisticas = calcular_estatisticas(query)
        
        return jsonify({
            'grafico': grafico,
            'estatisticas': estatisticas,
            'historico': [{
                'data': h.data_coleta.isoformat(),
                'produto': h.produto_loja.produto.nome,
                'loja': h.produto_loja.loja.nome,
                'preco': float(h.preco),
                'variacao': calcular_variacao(h),
                'promocao': h.preco < h.produto_loja.preco_alvo if h.produto_loja.preco_alvo else False
            } for h in historico],
            'paginacao': {
                'pagina_atual': pagina,
                'total_paginas': (total + itens_por_pagina - 1) // itens_por_pagina,
                'total': total,
                'inicio': (pagina - 1) * itens_por_pagina + 1,
                'fim': min(pagina * itens_por_pagina, total)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 6. Próximos Passos

1. **Implementar funções auxiliares** para gráficos e estatísticas
2. **Adicionar validações** nos formulários
3. **Implementar notificações** em tempo real
4. **Adicionar temas** personalizáveis
5. **Otimizar performance** das consultas
6. **Implementar cache** para dados frequentes
7. **Adicionar testes** automatizados
8. **Documentar APIs** com Swagger

Este guia fornece uma base sólida para a implementação completa do AdminLTE no projeto PromoPreço.
# 🧪 Scripts de Teste - PromoPreço

Esta pasta contém scripts para popular e testar o banco de dados com dados realistas.

## 📁 Scripts Disponíveis

### 🚀 `popular_dados_completos.py`
**Objetivo**: Popular o banco com dados completos de teste
- **100 produtos** com nomes realistas (categorias: alimentos, bebidas, higiene, etc.)
- **20 estabelecimentos** distribuídos em diferentes bairros e cidades
- **2000 preços** (cada produto em cada estabelecimento)

```bash
python Testes/popular_dados_completos.py
```

### 🔄 `reset_e_popular.py`
**Objetivo**: Reset completo + população automática
- Executa `force_reset.py` para limpar o banco
- Executa `popular_dados_completos.py` para popular
- Processo totalmente automatizado

```bash
python Testes/reset_e_popular.py
```

### 🔍 `verificar_dados.py`
**Objetivo**: Verificar os dados após população
- Mostra estatísticas gerais
- Lista amostras de cada entidade
- Verifica distribuição de preços
- Confirma se objetivos foram atingidos

```bash
python Testes/verificar_dados.py
```

## 🎯 Dados Gerados

### Produtos (100 itens)
Categorias realistas com marcas e tamanhos:
- **Alimentos**: Arroz Tio João 5kg, Feijão Camil 1kg, etc.
- **Bebidas**: Refrigerante Coca-Cola 2L, Suco Del Valle 1L, etc.
- **Higiene**: Shampoo Dove 400ml, Sabonete Lux 90g, etc.
- **Limpeza**: Detergente Ypê 500ml, Sabão OMO 1kg, etc.
- E mais 6 categorias...

### Estabelecimentos (20 itens)
Redes conhecidas em locais realistas:
- **Extra Centro** (São Paulo)
- **Carrefour Vila Madalena** (São Paulo)
- **Pão de Açúcar Jardins** (São Paulo)
- **Atacadão Mooca** (São Paulo)
- E mais 16 estabelecimentos...

### Preços (2000 itens)
- Cada produto tem preço em cada estabelecimento
- Variação realista de -30% a +40% do preço base
- Preços base por categoria (ex: carnes ~R$25, bebidas ~R$4)

## 🚦 Como Usar

### 1. Primeira Vez (Setup Completo)
```bash
# 1. Certifique-se que o Flask está rodando
python app.py

# 2. Em outro terminal, execute o setup completo
python Testes/reset_e_popular.py

# 3. Verifique os dados
python Testes/verificar_dados.py
```

### 2. Apenas Popular (Banco Vazio)
```bash
python Testes/popular_dados_completos.py
```

### 3. Apenas Verificar
```bash
python Testes/verificar_dados.py
```

## ⚠️ Pré-requisitos

1. **Flask rodando**: Execute `python app.py` antes dos scripts
2. **Dependências**: `pip install requests` (já está no requirements.txt)
3. **Banco limpo**: Use `reset_e_popular.py` ou `force_reset.py` se necessário

## 📊 Tempo de Execução

- **População completa**: ~2-3 minutos (2000 requisições HTTP)
- **Reset + População**: ~3-4 minutos
- **Verificação**: ~5-10 segundos

## 🎮 Testando Funcionalidades

Após popular, teste:

### Dashboard
```
http://localhost:5000/dashboard
```
- Estatísticas gerais
- Produtos/estabelecimentos com mais preços

### Comparação de Preços
```
http://localhost:5000/comparar/1
```
- Veja preços do produto ID 1 em todos estabelecimentos

### Busca Avançada
```
http://localhost:5000/precos?preco_min=5&preco_max=15&page=1
```
- Filtre preços entre R$5 e R$15

### API Endpoints
```bash
# Listar produtos
curl http://localhost:5000/produtos

# Estatísticas
curl http://localhost:5000/dashboard/stats

# Preços com filtros
curl "http://localhost:5000/precos?produto_id=1&estabelecimento_id=2"
```

## 🐛 Troubleshooting

**Erro "API não está respondendo":**
```bash
python app.py  # Certifique-se que Flask está rodando
```

**Erro de conexão:**
```bash
pip install requests  # Instale dependências
```

**Dados duplicados:**
```bash
python force_reset.py  # Reset completo do banco
```

**Performance lenta:**
- Normal para 2000 inserções via HTTP
- Use `verificar_dados.py` para acompanhar progresso

## 📈 Próximos Passos

Após popular, explore:
1. **Interface Web**: Navegue pelos cadastros
2. **Dashboard**: Analise estatísticas
3. **API**: Teste endpoints com dados reais
4. **Filtros**: Experimente buscas avançadas
5. **Performance**: Observe comportamento com volume de dados
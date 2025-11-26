# 🗺️ Análise de Grafos - Bairros do Recife

Projeto final de Teoria dos Grafos que implementa algoritmos fundamentais (BFS, DFS, Dijkstra, Bellman-Ford) em Python. A aplicação prática modela a malha urbana do Recife para análise de rotas e métricas de conectividade, além de realizar um estudo comparativo de performance dos algoritmos utilizando um dataset de transações de Bitcoin.

## 📋 Índice
- [Instalação](#-instalação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Guia de Uso](#-guia-de-uso)
  - [1. Processamento de Dados](#1-processamento-de-dados-obrigatório)
  - [2. Análise Completa do Grafo](#2-análise-completa-do-grafo-obrigatório)
  - [3. Busca de Caminhos](#3-busca-de-caminhos)
  - [4. Cálculo de Distâncias em Lote](#4-cálculo-de-distâncias-em-lote)
  - [5. Visualizações](#5-visualizações)
  - [6. Testes de Algoritmos](#6-testes-de-algoritmos)
  - [7. Consulta de Informações](#7-consulta-de-informações)
- [Estrutura de Saída](#-estrutura-de-saída)
- [Arquitetura](#-arquitetura)


## 📦 Instalação

### 1. Clone o repositório

```bash
git clone git@github.com:Taverna-Hub/projeto-grafos.git
cd projeto-grafos
```

### 2. Crie e Inicialize o ambiente virtual

```bash
python -m venv venv
```

- No Windows
  ```bash
    .\venv\Scripts\activate
  ```

- No Linux/macOS
  ```bash
    source venv/bin/activate
  ```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```


## 📂 Estrutura do Projeto

```
projeto-grafos/
├── data/                           # Dados de entrada
│   ├── adjacencias_bairros.csv     # Arestas do grafo (conexões entre bairros)
│   ├── bairros_recife.csv          # Lista de bairros e microrregiões
│   ├── bairros_unique.csv          # Bairros únicos processados
│   └── enderecos.csv               # Pares de endereços para cálculo de distância
├── src/                            # Código fonte
│   ├── cli.py                      # Interface de linha de comando
│   ├── solve.py                    # Análise principal do grafo
│   ├── viz.py                      # Visualizações analíticas
│   ├── constants.py                # Constantes e caminhos de arquivos
│   ├── graphs/                     # Implementação de grafos
│   │   ├── graph.py                # Classe Graph (lista de adjacências)
│   │   ├── algorithms.py           # Algoritmos (BFS, DFS, Dijkstra, Bellman-Ford)
│   │   └── io.py                   # Carregamento de dados
│   └── utils/                      # Utilitários
│       └── normalize.py            # Normalização de nomes
├── tests/                          # Testes automatizados
│   ├── comprehensive_tests.py      # Testes abrangentes de todos os algoritmos
│   ├── test_bfs.py                 # Testes específicos de BFS
│   ├── test_dfs.py                 # Testes específicos de DFS
│   ├── test_dijkstra.py            # Testes específicos de Dijkstra
│   └── test_bellman_ford.py        # Testes específicos de Bellman-Ford
├── out/                            # Resultados gerados (criado automaticamente)
├── main.py                         # Script principal (alternativa ao CLI)
├── requirements.txt                # Dependências do projeto
└── README.md                       # Este arquivo
```


## 🚀 Guia de Uso

### Ordem de Execução Recomendada

Para obter todos os resultados do projeto, execute os comandos na seguinte ordem:

```
1. process      → Processa dados de entrada
2. analyze      → Calcula métricas do grafo
3. distances    → Calcula distâncias entre endereços
4. path         → Busca caminho específico (Nova Descoberta → Boa Viagem)
5. visualize    → Gera árvore de percurso
6. interactive  → Gera grafo interativo HTML
7. plots        → Gera gráficos analíticos estáticos
8. test         → Executa testes de algoritmos
9. info         → Consulta resultados
```

---

### 1. Processamento de Dados (OBRIGATÓRIO)

**Comando:**
```bash
python src/cli.py process
```

**O que faz:**
- Lê o arquivo `data/bairros_recife.csv`
- Remove duplicatas de bairros
- Normaliza nomes (capitalização, espaços)
- Gera `data/bairros_unique.csv`

**Por que rodar primeiro:**
Este comando prepara os dados de entrada, removendo inconsistências e garantindo que os nomes dos bairros estejam padronizados. Todos os outros comandos dependem desse processamento.

**Saída:**
```
data/bairros_unique.csv
```

---

### 2. Análise Completa do Grafo (OBRIGATÓRIO)

**Comando:**
```bash
python src/cli.py analyze
```

**O que faz:**
1. **Carrega dados**: Lê adjacências e bairros processados
2. **Constrói o grafo**: Cria estrutura de lista de adjacências
3. **Calcula métricas globais**:
   - Ordem (|V|): número de bairros
   - Tamanho (|E|): número de conexões
   - Densidade: quão conectado é o grafo (0 a 1)
4. **Calcula métricas por microrregião**:
   - Extrai subgrafos induzidos por cada microrregião (1.1, 1.2, ..., 6.3)
   - Calcula ordem, tamanho e densidade de cada subgrafo
5. **Calcula ego-networks**:
   - Para cada bairro, extrai a ego-network (bairro + vizinhos)
   - Calcula densidade ego (quão conectados são os vizinhos entre si)
6. **Gera ranking por grau**: Lista bairros ordenados por número de conexões

**Por que rodar em segundo lugar:**
Este é o comando central que gera todas as métricas fundamentais. Outros comandos (especialmente `info` e `plots`) dependem dos arquivos JSON e CSV gerados aqui.

---

### 3. Busca de Caminhos

**Comando:**
```bash
python src/cli.py path "Bairro Origem" "Bairro Destino"
```

**Exemplo:**
```bash
python src/cli.py path "Nova Descoberta" "Boa Viagem (Setúbal)"
```

**O que faz:**
1. Carrega o grafo de adjacências
2. Executa o algoritmo de **Dijkstra** para encontrar o caminho mínimo
3. Retorna o custo total e a sequência de bairros
4. **Caso especial**: Se a origem for "Nova Descoberta" e o destino "Boa Viagem (Setúbal)", salva o resultado em JSON para uso posterior

**Algoritmo utilizado:**
- **Dijkstra**: Encontra o caminho de menor custo em grafos com pesos não-negativos
- Complexidade: O((|V| + |E|) log |V|)

**Quando rodar:**
- Após `analyze` (para garantir que o grafo está construído)
- Sempre que quiser buscar o caminho mínimo entre dois bairros

---

### 4. Cálculo de Distâncias em Lote

**Comando:**
```bash
python src/cli.py distances
```

**O que faz:**
1. Lê o arquivo `data/enderecos.csv` com pares de endereços
2. Para cada par (origem, destino):
   - Extrai os bairros dos endereços
   - Executa Dijkstra para calcular a distância
   - Salva o resultado
3. Gera uma tabela CSV com todas as distâncias calculadas

**Formato esperado de `enderecos.csv`:**
```csv
endereco_origem,endereco_destino
"Rua X, Bairro A",Rua Y, Bairro B"
"Av. Z, Bairro C","Rua W, Bairro D"
```

---

### 5. Visualizações

#### 5.1. Árvore de Percurso

**Comando:**
```bash
python src/cli.py visualize
```

**O que faz:**
1. Lê um arquivo JSON com dados de um percurso (origem, destino, custo, caminho)
2. Gera uma visualização em árvore do caminho
3. Cria tanto um arquivo HTML interativo quanto uma imagem PNG estática

**Pré-requisito:**
- Executar `path "Nova Descoberta" "Boa Viagem (Setúbal)"` antes

---

#### 5.2. Grafo Interativo

**Comando:**
```bash
python src/cli.py interactive
```

**O que faz:**
1. Carrega o grafo completo da cidade
2. Lê o percurso destacado (Nova Descoberta → Boa Viagem)
3. Gera um grafo interativo HTML com:
   - Todos os bairros como nós
   - Todas as conexões como arestas
   - Caminho destacado em vermelho
   - Tooltips com informações de cada bairro
   - Busca de bairros por nome
   - Layout force-directed (nós se repelem, arestas atraem)

**Tecnologia:**
- PyVis (wrapper para vis.js)
- Permite zoom, pan, arrastar nós, etc.

**Como visualizar:**
Abra o arquivo `grafo_interativo.html` em qualquer navegador web.

**Pré-requisitos:**
- Executar `analyze` (para ter o grafo completo)
- Executar `path "Nova Descoberta" "Boa Viagem (Setúbal)"` (para ter o caminho destacado)

---

#### 5.3. Gráficos Estáticos Analíticos

**Comando:**
```bash
python src/cli.py plots
```

**O que faz:**
Gera 3 gráficos analíticos que revelam diferentes aspectos da estrutura urbana:

**1. Ranking de Densidade de Ego-Network por Microrregião**
- **Métrica**: Densidade média das ego-networks dos bairros de cada microrregião
- **Interpretação**: Mede quão interconectados são os vizinhos dos bairros
  - Alta densidade → vizinhanças bem integradas, múltiplas rotas alternativas
  - Baixa densidade → bairros são pontes entre regiões, menos redundância

**2. Subgrafo dos Top 10 Bairros com Maior Grau**
- **Métrica**: Número de conexões diretas (grau)
- **Interpretação**: Identifica os "hubs" estratégicos da cidade
  - Bairros com muitas conexões são pontos de convergência de fluxo
  - São passagens obrigatórias para muitos deslocamentos
  - Falhas nesses bairros impactam grandes áreas

**3. Histograma de Distribuição de Graus**
- **Métrica**: Frequência de bairros por número de conexões
- **Interpretação**: Revela o padrão global de conectividade
  - Distribuição típica: assimétrica (poucos hubs, muitos periféricos)
  - Mostra média, mediana, outliers

**Pré-requisitos:**
- Executar `analyze` (para ter as métricas ego e graus)

---

### 6. Testes de Algoritmos

**Comando:**
```bash
python src/cli.py test
```

**O que faz:**
Executa uma bateria completa de testes para validar a implementação de todos os algoritmos no dataset da parte 2:

**Algoritmos testados:**
1. **BFS (Busca em Largura)**
   - Testa exploração de vizinhanças
   - Valida ordem de visita (nível por nível)
   
2. **DFS (Busca em Profundidade)**
   - Testa exploração em profundidade
   - Valida backtracking

3. **Dijkstra (Caminho Mínimo)**
   - Testa múltiplos pares origem-destino
   - Valida custos calculados vs. esperados
   - Verifica propriedades de optimalidade

4. **Bellman-Ford (Pesos Negativos)**
   - Testa com grafos contendo pesos negativos
   - Valida detecção de ciclos negativos
   - Compara resultados com Dijkstra em casos sem pesos negativos

**Quando rodar:**
- Após qualquer modificação nos algoritmos (para validação)
- Para verificar correção da implementação
- Pode ser executado a qualquer momento (não depende de outros comandos)

---

### 7. Consulta de Informações

**Comando:**
```bash
python src/cli.py info --type <tipo>
```

**Tipos disponíveis:**
- `global`: Métricas globais da cidade
- `microregions`: Métricas por microrregião
- `ego`: Ranking de bairros por densidade ego
- `degree`: Ranking de bairros por grau

**Exemplos:**

#### 7.1. Métricas Globais
```bash
python src/cli.py info --type global
```

#### 7.2. Métricas por Microrregião
```bash
python src/cli.py info --type microregions
```

#### 7.3. Ranking por Densidade Ego
```bash
python src/cli.py info --type ego
```

#### 7.4. Ranking por Grau
```bash
python src/cli.py info --type degree
```

**Pré-requisitos:**
- Executar `analyze` antes (gera os arquivos JSON/CSV consultados)


## 📊 Estrutura de Saída

Todos os resultados são salvos no diretório `out/`, organizado por itens:

```
out/
└── 1. Grafo dos Bairros do Recife/
    ├── 1.3 Métricas globais e por grupo/
    │   ├── recife_global.json      
    │   ├── microrregioes.json     
    │   └── ego_bairro.csv          
    │
    ├── 1.4 Graus e Rankings/
    │   └── graus.csv               
    │
    ├── 1.6 Distância entre endereços X e Y/
    │   ├── distancias_enderecos.csv
    │   └── percurso_nova_descoberta_setubal.json
    │
    ├── 1.7 Transforme o percurso em árvore e mostre/
    │   ├── arvore_percurso.html
    │   └── arvore_percurso.png
    │
    ├── 1.8 Explorações e visualizações analíticas/
    │   ├── ranking_densidade_microrregiao.png
    │   ├── ranking_densidade_microrregiao.csv
    │   ├── subgrafo_top10_bairros.png
    │   ├── subgrafo_top10_metricas.txt
    │   ├── histograma_distribuicao_graus.png
    │   └── estatisticas_graus.txt
    │
    └── 1.9 Apresentação interativa do grafo/
        └── grafo_interativo.html

└── 2. Dataset Maior e Comparação de Algoritmos/
    └── report.json                 
```


## 🔍 Exemplos de Uso Completo

### Fluxo de Trabalho Completo

```bash
# 1. Preparar dados
python src/cli.py process

# 2. Analisar grafo
python src/cli.py analyze

# 3. Calcular distâncias
python src/cli.py distances

# 4. Buscar caminho específico
python src/cli.py path "Nova Descoberta" "Boa Viagem (Setúbal)"

# 5. Gerar visualizações
python src/cli.py visualize
python src/cli.py interactive
python src/cli.py plots

# 6. Validar algoritmos
python src/cli.py test

# 7. Consultar resultados
python src/cli.py info --type global
python src/cli.py info --type microregions
python src/cli.py info --type ego
python src/cli.py info --type degree
```

### Busca de Outros Caminhos

```bash
# Exemplo 1: Afogados → Macaxeira
python src/cli.py path "Afogados" "Macaxeira"

# Exemplo 2: Várzea → Santo Amaro
python src/cli.py path "Várzea" "Santo Amaro"

# Exemplo 3: Ponto de Parada → Bongi
python src/cli.py path "Ponto de Parada" "Bongi"
```
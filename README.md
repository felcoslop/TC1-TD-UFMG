# Otimização de Monitoramento de Ativos em Barragens de Mineração

> **Trabalho Computacional 1** - Engenharia de Sistemas UFMG  
> *Algoritmos de Otimização e Metaheurísticas*

## Sobre o Projeto

Imagine que você é responsável pela manutenção de 125 equipamentos críticos espalhados por uma região de mineração. Esses equipamentos precisam de manutenção regular, mas você tem um dilema: 

- **Usar poucas equipes** = economiza dinheiro, mas as equipes precisam percorrer distâncias enormes
- **Usar muitas equipes** = reduz as distâncias, mas explode o orçamento

Este projeto resolve exatamente esse problema usando inteligência computacional!

## O Que Este Projeto Faz

Este trabalho implementa um **algoritmo VNS (Variable Neighborhood Search)** para resolver um problema de otimização multi-objetivo real do setor de mineração. O objetivo é encontrar o equilíbrio perfeito entre:

- **f1**: Minimizar a distância total que as equipes precisam percorrer
- **f2**: Minimizar o número de equipes necessárias

### O Desafio Real
- **125 ativos** espalhados geograficamente
- **14 bases** operacionais disponíveis  
- **Máximo 8 equipes** de manutenção
- **Restrições práticas** de logística e operação

> **Curiosidade**: Este é um problema real que empresas de mineração enfrentam diariamente!

## Modelagem Matemática

### Parâmetros do Problema
- `n = 125` ativos a serem monitorados
- `m = 14` bases operacionais disponíveis  
- `s = 8` equipes máximas de manutenção
- `η = 0.2` (20% - percentual mínimo de ativos por equipe)
- `d_ij` = distância euclidiana entre ativo i e base j

### Variáveis de Decisão
- `x_ij ∈ {0,1}`: 1 se ativo i está na base j, 0 caso contrário
- `y_jk ∈ {0,1}`: 1 se base j está ocupada pela equipe k, 0 caso contrário
- `h_ik ∈ {0,1}`: 1 se ativo i está na equipe k, 0 caso contrário

### Funções Objetivo Conflitantes
- **f1** = Σᵢ Σⱼ d_ij x_ij *(minimizar distância total)*
- **f2** = S *(minimizar número de equipes utilizadas)*

### Restrições Operacionais
1. Cada equipe deve estar em exatamente uma base (se estiver sendo usada)
2. Cada ativo deve estar em exatamente uma base
3. Ativo só pode estar numa base se a base tiver pelo menos uma equipe
4. Cada ativo deve estar em exatamente uma equipe
5. Ativo só pode estar numa equipe se a equipe estiver na base do ativo
6. Cada equipe deve ter pelo menos η·n/s ativos (balanceamento mínimo)

## Algoritmo VNS Implementado

### Estruturas de Vizinhança
1. **Troca ativo de base**: Move um equipamento de uma base para outra
2. **Troca equipe de base**: Move uma equipe inteira de uma base para outra
3. **Troca ativo entre equipes**: Troca equipamentos entre equipes da mesma base

### Heurística Construtiva Inteligente
1. **Ordenação por centralidade**: Calcula distância média de cada base para todos os ativos
2. **Alocação estratégica**: Distribui equipes nas bases mais centrais
3. **Atribuição otimizada**: Cada ativo vai para a base mais próxima que tenha equipe
4. **Balanceamento**: Distribui ativos entre equipes de forma equilibrada

### Busca Local Especializada
- **Para f1**: Foca em reduzir distâncias movendo ativos para bases mais próximas
- **Para f2**: Consolida equipes removendo as que têm poucos ativos

### Operador Shake Adaptativo
- **Intensidade variável**: Aumenta conforme iterações sem melhoria
- **Perturbação inteligente**: Move ativos considerando proximidade geográfica
- **Diversificação**: Para f2, move equipes inteiras para bases vazias

## Como Usar

### Instalação Rápida
```bash
# Clone o repositório
git clone [https://github.com/felcoslop/TC1-TD-UFMG]

# Instale as dependências
pip install -r requirements.txt
```

### Execução Simples
```bash
# Execute o algoritmo completo
python src/monitoramento_ativos_base.py
```

### Estrutura do Projeto
```
TC1-TD-UFMG-main/
├── src/                                    # Código fonte
│   ├── monitoramento_ativos_base.py       # Arquivo principal
│   ├── dados.py                           # Carrega dados do CSV
│   ├── funcoes_objetivo.py                # Calcula f1, f2 e verifica restrições
│   ├── solucoes_iniciais.py               # Gera soluções iniciais
│   ├── busca_local.py                     # Estruturas de vizinhança
│   ├── algoritmos_vns.py                  # Algoritmo VNS
│   ├── visualizacao.py                    # Gera gráficos
│   └── relatorios.py                      # Gera relatórios
├── data/
│   └── probdata.csv                       # Dados do problema (125 ativos)
├── resultados/
│   ├── graficos/                          # Gráficos gerados
│   └── relatorios/                        # Relatórios em texto
├── latex/
│   └── bare_conf.tex                      # Documento LaTeX da entrega
└── requirements.txt                       # Dependências Python
```

## Resultados Gerados

### Gráficos de Análise
- **`analise_convergencia_completa.png`**: Curvas de convergência das 5 execuções
- **`melhor_solucao_f1.png`**: Rede otimizada para minimizar distância
- **`melhor_solucao_f2.png`**: Rede otimizada para minimizar número de equipes
- **`mapa_geografico_f1.png`**: Mapa geográfico da solução f1
- **`mapa_geografico_f2.png`**: Mapa geográfico da solução f2
- **`analise_detalhada_completa.png`**: Análise comparativa completa

### Relatórios Detalhados
- **`relatorio_entrega_1.txt`**: Estatísticas completas (min, max, média, desvio padrão)

## Interpretação dos Resultados

### Função f1 (Distância Total)
- **Objetivo**: Minimizar soma de todas as distâncias
- **Unidade**: Quilômetros
- **Melhor resultado**: 1.239,26 km
- **Interpretação**: Menor valor = maior eficiência espacial

### Função f2 (Número de Equipes)
- **Objetivo**: Minimizar número de equipes utilizadas
- **Unidade**: Quantidade de equipes
- **Melhor resultado**: 1 equipe
- **Interpretação**: Menor valor = menor custo operacional

### Conflito Confirmado
- **f1 baixo** → f2 alto (muitas equipes próximas, distâncias pequenas)
- **f2 baixo** → f1 alto (poucas equipes, distâncias grandes)

## Características Técnicas

### Configuração Experimental
- **5 execuções** independentes para cada função objetivo
- **500 iterações** por execução
- **Busca local especializada** para cada função
- **Shake adaptativo** com intensidade variável (0.3 a 0.8)
- **Verificação completa** de todas as restrições

### Parâmetros do VNS
- Intensidade mínima do shake: 0.3
- Intensidade máxima do shake: 0.8
- Número máximo de perturbações: 60 ativos
- Critério de parada: 500 iterações ou convergência

### Alunos
- Felipe Costa Lopes
- Luiz Felipe dos Santos Alves  
- Stephanie Pereira Barbosa

## Referências

- Hansen, P. & Mladenović, N. (2001). Variable neighborhood search: Principles and applications
- Glover, F. & Kochenberger, G. (2003). Handbook of Metaheuristics
- Gendreau, M. & Potvin, J.-Y. (2010). Handbook of Metaheuristics, 2nd ed.

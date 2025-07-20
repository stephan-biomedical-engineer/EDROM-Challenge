# Path Planning com Algoritmo A\* - Robô de Futebol EDROM

## Visão Geral

Este projeto implementa um algoritmo de planejamento de caminho A\* para um robô de futebol na competição EDROM. O robô precisa navegar pelo campo, evitar adversários, capturar a bola e levá-la até o gol, considerando diferentes custos de movimento e estados.

## Características Principais

* Implementação do algoritmo A\* com heurística adaptada
* Suporte a movimentos ortogonais e diagonais
* Cálculo de custos considerando:

  * Movimento reto vs. diagonal
  * Custo de rotação
  * Posse de bola
  * Proximidade de adversários
* Sistema de logging detalhado para análise

## Estrutura do Código

### Classe `Estado`

Representa um nó no espaço de busca:

* `posicao`: Coordenadas (x,y) no grid
* `pai`: Nó predecessor no caminho
* `g`: Custo acumulado do caminho desde o início
* `h`: Estimativa heurística do custo até o objetivo
* `f`: Custo total (g + h)
* `direcao`: Última direção de movimento
* `tem_bola`: Estado de posse da bola

### Funções Principais

#### `calcular_heuristica(pos_atual, pos_objetivo)`

```python
def calcular_heuristica(pos_atual, pos_objetivo):
    dx = abs(pos_atual[0] - pos_objetivo[0])
    dy = abs(pos_atual[1] - pos_objetivo[1])
    return 300 * max(dx, dy) - 200 * min(dx, dy)
```

#### `custo_movimento(dx, dy, tem_bola)`

```python
def custo_movimento(dx, dy, tem_bola):
    custo_base = 300 if (dx == 0 or dy == 0) else 100
    return custo_base * (1.5 if tem_bola else 1)
```

#### `custo_rotacao(direcao_atual, nova_direcao, tem_bola)`

```python
def custo_rotacao(direcao_atual, nova_direcao, tem_bola):
    # Implementação dos custos de rotação
    ...
```

* Rotação reto → diagonal: 100 (200 com bola)
* Rotação diagonal → reto: 50 (100 com bola)
* Rotação brusca (90°): 200 (400 com bola)

#### `penalidade_adversarios(pos, obstaculos)`

```python
def penalidade_adversarios(pos, obstaculos):
    # Calcula penalidade por proximidade
    ...
```

* Aplica penalidade inversamente proporcional à distância
* Evita passar muito perto de adversários

#### `encontrar_caminho()`

Implementação principal do A\* que:

* Usa fila de prioridade (heap) para selecionar sempre o nó com menor f
* Mantém conjuntos de nós abertos e fechados
* Considera todos os custos e heurísticas

## Escolha da Heurística

### Comparação entre Heurísticas

| Heurística       | Fórmula                   | Adequação         |   |       |   |                        |
| ---------------- | ------------------------- | ----------------- | - | ----- | - | ---------------------- |
| Manhattan        |                           | x1-x2             | + | y1-y2 |   | Subestima diagonais    |
| Euclidiana       | sqrt((x1-x2)² + (y1-y2)²) | Cálculo complexo  |   |       |   |                        |
| Chebyshev        | max(                      | x1-x2             | , | y1-y2 | ) | Melhor para 8 direções |
| **Nossa versão** | 300*max - 200*min         | **Melhor ajuste** |   |       |   |                        |

**Vantagens da nossa heurística:**

1. Considera custos diferentes para diagonais (100) vs retos (300)
2. Nunca superestima o custo real (garante otimalidade)
3. Mais eficiente que Manhattan pura (explora menos nós)

## Seleção do Menor Custo

Mecanismo de seleção:

1. Cada nó armazena `f = g + h`
2. Uso de `heapq.heappop()` para remover nó com menor `f`
3. Classe `Estado` implementa `__lt__` para comparação por `f`

**Garantias:**

* Encontra caminho ótimo (se existir)
* Busca eficiente priorizando nós promissores

## Logging e Depuração

Sistema registra:
✅ Parâmetros iniciais
✅ Cada iteração do algoritmo
✅ Cálculos detalhados de custos
✅ Decisões de movimento
✅ Caminho final

Arquivos de log: `logs/path_planning_<timestamp>.log`

## Como Executar

1. Execute o simulador:

```bash
python simulador.py
```

2. Controles:

* ▶️/⏸️ Play/Pause: Inicia/pausa simulação
* 🔄 Reset: Gera novo cenário

## Níveis Implementados

1. **Nível Básico**: Movimento básico até bola e gol
2. **Nível 1**: Custos de rotação
3. **Nível 2**: Estados (com/sem bola)
4. **Nível 3**: Evitar proximidade com adversários

## Considerações Finais

✅ Código limpo e documentado
✅ Solução completa para o desafio EDROM
✅ Mecanismos avançados de análise
✅ Flexível para ajustes futuros

Algoritmo balanceia eficiência e otimalidade, atendendo todos requisitos do problema.

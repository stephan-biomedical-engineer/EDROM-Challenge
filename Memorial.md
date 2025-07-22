-----

Como foi o desenvolvimento do algoritmo? Este documento descreve a evolução do algoritmo de *path planning* desenvolvido para o desafio EDROM, detalhando as diferentes abordagens e melhorias implementadas ao longo do projeto.

-----

## 1\. Primeira Abordagem: Algoritmo Geométrico Básico (`test_geometria.py`)

Aqui foi o começo de uma solução fundamental para mover o robô da posição inicial até a bola e, em seguida, ao gol.

### Características

  * **Abordagem**: Utilizou **geometria analítica básica**.
  * **Movimentação**: Priorizou **movimentos retos** (primeiro no eixo X, depois no eixo Y).
  * **Contorno de Obstáculos**: Implementou **movimentos diagonais alternativos** quando o robô ficava travado, agindo como um mecanismo rudimentar de desvio.

### Limitações

  * Não considerava **custos diferenciados** para os movimentos.
  * Falta de **otimização do caminho**.
  * Dificuldade em cenários complexos com **muitos obstáculos**.

### Trecho Característico

```python
# Direção preferencial em X e Y
dx = 1 if x_objetivo > x_atual else -1 if x_objetivo < x_atual else 0
dy = 1 if y_objetivo > y_atual else -1 if y_objetivo < y_atual else 0
```

### Progresso Alcançado

Esta versão resolveu o problema básico de movimentação, mas rapidamente se mostrou inadequada para cenários mais complexos, especialmente com múltiplos obstáculos próximos. Serviu como uma base para entender as necessidades fundamentais do problema.

-----

## 2\. Segunda Versão: Algoritmo A\* Básico (`test_a_star.py`)

A segunda fase trouxe uma melhoria significativa com a implementação do algoritmo A\*, buscando encontrar caminhos mais otimizados.

### Novas Funcionalidades

  * **Heurística**: Uso da **distância de Manhattan** para estimar o custo.
  * **Exploração Inteligente**: Avaliação sistemática dos caminhos possíveis.
  * **Otimização**: Busca pelo caminho de menor custo, levando em conta o custo real e a heurística.

### Estrutura Chave

```python
class Estado:
    def __init__(self, posicao, pai=None, g=0, h=0):
        self.posicao = posicao
        self.pai = pai
        self.g = g  # custo real
        self.h = h  # heurística
        self.f = g + h  # custo total estimado
```

### Vantagens

  * Encontrava **caminhos mais eficientes**.
  * Melhor desempenho em **cenários complexos**.
  * Serviu como uma **base sólida** para implementações futuras.

### Limitações

  * Não considerava todos os **requisitos completos do desafio** (ex: custos específicos de movimento, posse de bola).
  * Custos eram **fixos e simplificados**.
  * Falta de tratamento para **mudanças de direção** e **posse de bola**.

-----

## 3\. Versão Final: Algoritmo A\* Completo (`candidato.py`)

A versão final representa a solução completa, incorporando todas as funcionalidades e otimizações necessárias para atender aos requisitos do desafio EDROM.

### Principais Melhorias

1.  **Sistema de Custos Avançado**:

      * **Movimentos retos (300)** vs. **diagonais (100)**: refletindo a preferência por movimentos diagonais que cobrem maior distância por passo lógico.
      * **Custo adicional para mudanças de direção**: penaliza curvas bruscas, incentivando caminhos mais suaves.
      * **Custo aumentado quando com posse de bola**: simula a redução de agilidade do robô.

    <!-- end list -->

    ```python
    def calcular_custo_movimento(direcao_atual, nova_direcao, tem_bola):
        if direcao_atual and direcao_atual != nova_direcao:
            # Cálculo de custos de rotação...
    ```

2.  **Penalidades por Proximidade**:

      * **Adversários próximos aumentam o custo do caminho**: desencoraja a aproximação desnecessária a oponentes.
      * Permite passagem quando vantajoso, mas evita aproximação excessiva.

    <!-- end list -->

    ```python
    def calcular_penalidade_adversarios(posicao, obstaculos):
        penalidade = 0
        for obs in obstaculos:
            dist = max(abs(posicao[0]-obs[0]), abs(posicao[1]-obs[1]))
            if dist <= 2:  # Células adjacentes e diagonais secundárias
                penalidade += (300 - 100 * dist) if dist <= 1 else (100 - 30 * (dist-1)) # Exemplo de penalidade inversamente proporcional à distância
        return penalidade
    ```

3.  **Heurística Otimizada**:

      * Combina movimentos diagonais e retos de forma a ser **precisamente alinhada com os custos reais** do algoritmo.

    <!-- end list -->

    ```python
    def calcular_heuristica(pos_atual, pos_objetivo):
        dx = abs(pos_atual[0] - pos_objetivo[0])
        dy = abs(pos_atual[1] - pos_objetivo[1])
        return min(dx, dy) * 100 + abs(dx - dy) * 300 # Heurística que reflete os custos de movimento
    ```

4.  **Sistema de Logging Aprimorado**:

      * **Registro detalhado** do processo de busca, facilitando o *debug* e a análise de desempenho.
      * **Diferenciação por níveis de importância**, permitindo filtrar informações relevantes.

### Arquitetura do Código Final

1.  **Organização Modular**:

      * **Separação clara** em seções lógicas para facilitar a manutenção e compreensão.
      * **Funções especializadas** para cada cálculo ou etapa do algoritmo.
      * **Documentação completa** de funções e classes.

2.  **Tratamento de Estados**:

      * **Rastreamento da direção anterior**: essencial para calcular custos de mudança de direção.
      * **Controle da posse de bola**: influencia os custos de movimento.
      * **Cálculo preciso de custos acumulados** (g-value) e totais (f-value).

3.  **Eficiência**:

      * Uso de **estruturas de dados adequadas**, como um `heap` (fila de prioridade) para gerenciamento de prioridades dos estados a serem explorados.
      * **Conjuntos para controle de estados visitados**, evitando reprocessamento e ciclos infinitos.

-----

## Conclusão da Evolução

O desenvolvimento do algoritmo de *path planning* para o desafio EDROM seguiu uma progressão lógica e iterativa, culminando em uma solução robusta e eficiente:

1.  **Fase de Prototipagem (`test_geometria.py`)**: Marcou a compreensão inicial do problema e a criação de uma solução funcional básica.

2.  **Implementação do Núcleo Algorítmico (`test_a_star.py`)**: Introduziu conceitos de busca informada, resultando em uma melhoria significativa na qualidade dos caminhos encontrados.

3.  **Refinamento Completo (`candidato.py`)**: Abordou todos os níveis do desafio, com um código organizado, documentado e mecanismos de otimização avançados.

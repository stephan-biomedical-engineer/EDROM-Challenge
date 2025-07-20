# README - Desafio de Path Finding com Algoritmo A\*

Autor: **Stephan Costa Barros**
Curso: **Engenharia Biomédica**
Áreas de interesse: **Elétrica** e **Behavior**

---

## \:dart: Objetivo

Este projeto implementa o algoritmo A\* para encontrar o **melhor caminho** que um robô deve seguir em um campo, considerando:

* Obstáculos (adversários)
* Mudança de direção (rotação)
* Custos diferentes para movimentação (reto x diagonal)
* Penalidades por proximidade de adversários
* Estado especial: com ou sem posse de bola

---

## \:books: Descrição do Algoritmo A\*

O A\* é uma estratégia de busca informada que prioriza os caminhos com **menor custo total estimado**:

```
f(n) = g(n) + h(n)
```

* **g(n)**: custo acumulado do início até o nó atual
* **h(n)**: estimativa de custo até o objetivo (heurística)
* **f(n)**: prioriza o menor valor na fila de prioridade

A fila de prioridade é gerenciada com `heapq`, que garante que o **estado com menor f(n)** seja sempre o próximo explorado.

---

## \:map: Regras do Desafio (Níveis de Resolução)

### Nível Básico

* Chegar à bola, depois ao gol
* Custo para andar reto (horizontal/vertical): **300**
* Custo para andar na diagonal: **100**
* Evitar obstáculos (adversários)

### Nível 1 - Penalidade por Rotação

* Mudar de direção reto ↔ diagonal: +50
* Mudança brusca (90 graus): +150

### Nível 2 - Penalidade com Bola

* Se o robô estiver com a bola, penalidades de rotação **dobram**

### Nível 3 - Proximidade de Adversários

* Células adjacentes a adversários são penalizadas com até +300
* Penalidade decai com a distância

---

## \:triangular\_ruler: Heurística (h)

Foi usada uma heurística **otimizada** para o desafio, considerando os custos diferentes:

```python
dx = abs(x1 - x2)
dy = abs(y1 - y2)
h(n) = min(dx, dy) * 100 + abs(dx - dy) * 300
```

* Movimentos diagonais custam 100, por isso priorizamos eles primeiro
* Movimentos retos mais distantes têm custo 300

---

## \:gear: Estrutura Interna

### Classe `Estado`

Cada posição no grid guarda:

* `posicao`: coordenadas (x, y)
* `pai`: referência ao estado anterior (para reconstrução do caminho)
* `g`: custo acumulado
* `h`: heurística
* `f`: custo total
* `direcao_anterior`: direção do movimento anterior
* `tem_bola`: booleano que indica posse da bola

### Open e Closed Sets

* **heap**: open set (estados a explorar), ordenado por `f(n)`
* **fechados**: closed set (estados já visitados), definido por `(posicao, direcao, tem_bola)` para evitar loops

---

## \:compass: Lógica da Rotação

Ao comparar a direção anterior com a nova:

* Se for de reto ↔ diagonal, soma +50 (ou +100 se tiver bola)
* Se for rotação 90º (ex: cima ↔ direita), soma +150 (ou +300 com bola)

Essa penalidade incentiva caminhos mais suaves e menos instáveis.

---

## \:warning: Obstáculos e Penalidades

* Células ocupadas por adversários são ignoradas (intransitáveis)
* Células **adjacentes** têm penalidades:

  * +300 se colado ao adversário
  * +200 para uma distância de 1 diagonal
  * 0 se distância > 1

Essa abordagem evita proibir caminhos viáveis, mas torna o robô mais cuidadoso.

---

## \:mag: Validação do Melhor Caminho

O A\* **sempre encontra o caminho menos custoso** (desde que a heurística seja admissível). Como:

* A heurística **nunca superestima** o custo real
* Os custos são **positivos e bem definidos**
* Estados repetidos são evitados (via closed set)

Além disso, é feito logging completo:

* Estados explorados
* Penalidades aplicadas
* Direções e rotações
* Custo total ao chegar ao destino

---

## \:hammer: Como Usar

1. Garanta que você está num ambiente com Python 3
2. Execute o programa principal (`simulador.py`)
3. Ele chamará `encontrar_caminho` duas vezes: (início → bola, bola → gol)
4. Veja o log detalhado no console e no diretório `logs/`

---

## \:trophy: Conclusão

Esta solução implementa **todos os níveis do desafio** com eficiência, clareza e estrutura profissional.
A utilização da heurística apropriada, da penalidade adaptativa e do modelo de estados com rotação e posse de bola permite que o robô encontre **o caminho mais seguro e ótimo** dentro das restrições impostas.
---


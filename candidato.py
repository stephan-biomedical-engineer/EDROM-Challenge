#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
NOME DO CANDIDATO: Stephan Costa Barros
CURSO DO CANDIDATO: Engenharia Biomédica
ÁREAS DE INTERESSE: Elétrica e Behavior
'''

import heapq
import logging
from datetime import datetime
import os

# ==================== CONFIGURAÇÃO DE LOGGING ====================
def configurar_logging():
    """Configura o sistema de logging com arquivo e console"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"path_planning_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Sistema de logging configurado")

configurar_logging()

# ==================== DEFINIÇÃO DE CLASSES ====================
class Estado:
    """Representa um estado no espaço de busca do A*"""
    
    def __init__(self, posicao, pai=None, g=0, h=0, direcao_anterior=None, tem_bola=False):
        """
        Inicializa um novo estado
        Args:
            posicao: Tupla (x,y) com a posição no grid
            pai: Estado anterior no caminho
            g: Custo acumulado do caminho
            h: Valor heurístico estimado
            direcao_anterior: Direção do movimento anterior
            tem_bola: Indica se o robô está com a bola
        """
        self.posicao = posicao
        self.pai = pai
        self.g = g          # Custo real acumulado
        self.h = h          # Heurística (estimativa)
        self.f = g + h      # Custo total estimado
        self.direcao_anterior = direcao_anterior
        self.tem_bola = tem_bola
        
        logging.info(f"Novo estado criado - Posição: {posicao} | Custo: g={g}, h={h}, f={self.f} | "
                     f"Direção: {direcao_anterior} | Bola: {'Sim' if tem_bola else 'Não'}")

    def __lt__(self, other):
        """Comparação para heap prioritário (menor custo f primeiro)"""
        return self.f < other.f

# ==================== FUNÇÕES DE CÁLCULO ====================
def calcular_heuristica(pos_atual, pos_objetivo):
    """
    Calcula a heurística otimizada para custos 100/300
    Args:
        pos_atual: Tupla (x,y) com a posição atual
        pos_objetivo: Tupla (x,y) com o objetivo
    Returns:
        Valor heurístico estimado
    """
    dx = abs(pos_atual[0] - pos_objetivo[0])
    dy = abs(pos_atual[1] - pos_objetivo[1])
    return min(dx, dy) * 100 + abs(dx - dy) * 300  # Combina movimentos diagonais e retos

def calcular_custo_movimento(direcao_atual, nova_direcao, tem_bola):
    """
    Calcula o custo total do movimento considerando:
    - Custo base (reto/diagonal)
    - Custo de rotação (se houver mudança de direção)
    Args:
        direcao_atual: Direção do movimento anterior
        nova_direcao: Direção do novo movimento
        tem_bola: Indica se o robô está com a bola
    Returns:
        Custo total do movimento
    """
    # Custo base conforme especificação do desafio
    custo = 100 if (nova_direcao[0] != 0 and nova_direcao[1] != 0) else 300
    
    # Aplica custo adicional para mudanças de direção
    if direcao_atual and direcao_atual != nova_direcao:
        # Mudança entre movimento reto e diagonal
        if (abs(direcao_atual[0]) + abs(direcao_atual[1])) != (abs(nova_direcao[0]) + abs(nova_direcao[1])):
            custo += 50 * (2 if tem_bola else 1)  # Nível 1 e 2
            logging.info(f"Custo de rotação reto/diagonal: {'com bola' if tem_bola else 'sem bola'}")
        # Mudança brusca (90 graus)
        elif direcao_atual[0] * nova_direcao[0] + direcao_atual[1] * nova_direcao[1] == 0:
            custo += 150 * (2 if tem_bola else 1)  # Nível 1 e 2
            logging.info(f"Custo de rotação 90°: {'com bola' if tem_bola else 'sem bola'}")
    
    return custo

def calcular_penalidade_adversarios(posicao, obstaculos):
    """
    Calcula penalidade por proximidade de adversários (Nível 3)
    Args:
        posicao: Tupla (x,y) sendo avaliada
        obstaculos: Lista de posições dos adversários
    Returns:
        Valor total da penalidade
    """
    penalidade = 0
    for obs in obstaculos:
        # Usa distância de Chebyshev (melhor para movimentos diagonais)
        dist = max(abs(posicao[0]-obs[0]), abs(posicao[1]-obs[1]))
        if dist <= 1:  # Apenas para células adjacentes
            penalidade += 300 - 100 * dist  # Penalidade decrescente com distância
            logging.info(f"Penalidade adversário: {posicao} próximo a {obs} (dist={dist})")
    
    return penalidade

# ==================== ALGORITMO PRINCIPAL ====================
def encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    """
    Implementação do algoritmo A* para encontrar o caminho ótimo
    Args:
        pos_inicial: Tupla (x,y) com a posição inicial
        pos_objetivo: Tupla (x,y) com o objetivo
        obstaculos: Lista de posições dos adversários
        largura_grid: Largura do grid de busca
        altura_grid: Altura do grid de busca
        tem_bola: Indica se o robô começa com a bola
    Returns:
        Lista de posições representando o caminho encontrado (vazia se não houver)

    - Nível Básico: Movimentos com custos diferenciados (reto:300, diagonal:100)
    - Nível 1: Custo adicional para mudanças de direção
    - Nível 2: Custo aumentado com posse de bola
    - Nível 3: Penalidade por proximidade de adversários
    """
    logging.info("\n" + "="*50 + " INÍCIO DA BUSCA " + "="*50)
    logging.info(f"Origem: {pos_inicial} | Destino: {pos_objetivo} | Posse de bola: {tem_bola}")
    logging.info(f"Grid: {largura_grid}x{altura_grid} | Obstáculos: {len(obstaculos)}")
    
    # Direções possíveis (8 movimentos)
    movimentos = [
        (1, 0), (-1, 0), (0, 1), (0, -1),  # Movimentos retos
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Movimentos diagonais
    ]
    
    # Inicializa estruturas de dados
    heap = []  # Fila de prioridade (abertos)
    fechados = set()  # Conjunto de estados já explorados
    
    # Adiciona o estado inicial
    heapq.heappush(heap, Estado(
        posicao=pos_inicial,
        g=0,
        h=calcular_heuristica(pos_inicial, pos_objetivo),
        direcao_anterior=None,
        tem_bola=tem_bola
    ))

    while heap:
        estado_atual = heapq.heappop(heap)
        logging.info(f"\nExplorando estado: {estado_atual.posicao} | Custo: f={estado_atual.f} (g={estado_atual.g}, h={estado_atual.h})")

        # Verifica se chegou ao objetivo
        if estado_atual.posicao == pos_objetivo:
            caminho = []
            estado = estado_atual
            while estado:
                caminho.append(estado.posicao)
                estado = estado.pai
            
            logging.info("\n" + "="*50 + " CAMINHO ENCONTRADO " + "="*50)
            logging.info(f"Custo total: {estado_atual.g} | Passos: {len(caminho)}")
            logging.info(f"Trajeto: {caminho[::-1]}")
            return caminho[::-1]

        # Marca o estado como explorado
        chave_estado = (estado_atual.posicao, estado_atual.direcao_anterior, estado_atual.tem_bola)
        if chave_estado in fechados:
            continue
        fechados.add(chave_estado)

        # Explora os vizinhos
        for movimento in movimentos:
            nova_pos = (
                estado_atual.posicao[0] + movimento[0], 
                estado_atual.posicao[1] + movimento[1]
            )
            
            # Verifica se a nova posição é válida
            if not (0 <= nova_pos[0] < largura_grid and 0 <= nova_pos[1] < altura_grid):
                logging.info(f"Posição inválida: {nova_pos} (fora do grid)")
                continue
                
            if nova_pos in obstaculos:
                logging.info(f"Posição inválida: {nova_pos} (obstáculo)")
                continue

            # Calcula os custos do movimento
            custo_mov = calcular_custo_movimento(
                estado_atual.direcao_anterior, 
                movimento, 
                estado_atual.tem_bola
            )
            
            penalidade = calcular_penalidade_adversarios(nova_pos, obstaculos)
            novo_custo_g = estado_atual.g + custo_mov + penalidade
            
            # Atualiza o status da bola (se alcançou o objetivo intermediário)
            nova_posse_bola = estado_atual.tem_bola or (nova_pos == pos_objetivo)

            # Cria novo estado
            novo_estado = Estado(
                posicao=nova_pos,
                pai=estado_atual,
                g=novo_custo_g,
                h=calcular_heuristica(nova_pos, pos_objetivo),
                direcao_anterior=movimento,
                tem_bola=nova_posse_bola
            )
            
            # Adiciona à fila de prioridade
            heapq.heappush(heap, novo_estado)
            logging.info(f"Movimento válido: {movimento} -> {nova_pos} | Custo: {custo_mov} + Penalidade: {penalidade}")

    logging.warning("Nenhum caminho válido encontrado!")
    return []
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
 NOME DO CANDIDATO: Stephan Costa Barros
 CURSO DO CANDIDATO: Engenharia Biomédica
 AREAS DE INTERESSE: Elétrica e Behavior
'''

import heapq
import logging
from datetime import datetime
import os

# Configuração do logging
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"path_planning_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    logging.info("Inicializando sistema de logging para path planning")

setup_logging()

class Estado:
    def __init__(self, posicao, pai=None, g=0, h=0, direcao=(0, 0), tem_bola=False):
        self.posicao = posicao
        self.pai = pai
        self.g = g
        self.h = h
        self.f = g + h
        self.direcao = direcao
        self.tem_bola = tem_bola
        logging.debug(f"Novo estado criado: Posição={posicao}, g={g}, h={h}, f={self.f}, "
                     f"Direção={direcao}, TemBola={tem_bola}")

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.posicao == other.posicao

    def __hash__(self):
        return hash((self.posicao, self.direcao, self.tem_bola))

def calcular_heuristica(pos_atual, pos_objetivo):
    """Heurística de Chebyshev para movimentos diagonais"""
    # heuristica = abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1]) # Heurística de Manhattan
    dx = abs(pos_atual[0] - pos_objetivo[0])
    dy = abs(pos_atual[1] - pos_objetivo[1])
    heuristica = 300 * max(dx, dy) - 200 * min(dx, dy) # Heurística de Chebyshev

    logging.debug(f"Cálculo heurística: De {pos_atual} para {pos_objetivo} = {heuristica}")
    return heuristica

def custo_movimento(dx, dy, tem_bola):
    """Custo básico de movimento (Nível Básico)"""
    movimento_tipo = "RETA" if dx == 0 or dy == 0 else "DIAGONAL"
    custo_base = 300 if movimento_tipo == "RETA" else 100
    fator_bola = 1.5 if tem_bola else 1
    custo_total = custo_base * fator_bola
    
    logging.debug(f"Custo movimento {movimento_tipo}: dx={dx}, dy={dy}, "
                 f"TemBola={tem_bola} -> Custo={custo_total}")
    return custo_total

def custo_rotacao(direcao_atual, nova_direcao, tem_bola):
    """Custos de rotação (Níveis 1 e 2)"""
    if direcao_atual == (0, 0) or direcao_atual == nova_direcao:
        logging.debug("Sem custo de rotação: mesma direção ou início")
        return 0
    
    # Tipos de rotação
    reto_anterior = abs(direcao_atual[0]) + abs(direcao_atual[1]) == 1
    reto_novo = abs(nova_direcao[0]) + abs(nova_direcao[1]) == 1
    
    if reto_anterior and not reto_novo:  # Reto -> Diagonal
        tipo_rotacao = "RETA->DIAGONAL"
        custo = 100 * (2 if tem_bola else 1)
    elif not reto_anterior and reto_novo:  # Diagonal -> Reto
        tipo_rotacao = "DIAGONAL->RETA"
        custo = 50 * (2 if tem_bola else 1)
    else:  # Mudança brusca (90°)
        tipo_rotacao = "ROTAÇÃO BRUSCA (90°)"
        custo = 200 * (2 if tem_bola else 1)
    
    logging.debug(f"Custo rotação {tipo_rotacao}: De {direcao_atual} para {nova_direcao}, "
                 f"TemBola={tem_bola} -> Custo={custo}")
    return custo

def penalidade_adversarios(pos, obstaculos):
    """Penalidade por proximidade de adversários (Nível 3)"""
    penalidade_total = 0
    detalhes = []
    
    for obs in obstaculos:
        distancia = max(abs(pos[0]-obs[0]), abs(pos[1]-obs[1]))
        if distancia <= 1.5:  # 1.5 para incluir diagonais
            penalidade = 300 / (distancia + 0.1)
            penalidade_total += penalidade
            detalhes.append(f"Obstáculo {obs}: dist={distancia:.1f} -> +{penalidade:.1f}")
    
    if penalidade_total > 0:
        logging.debug(f"Penalidade adversários em {pos}:\n  " + "\n  ".join(detalhes) +
                     f"\n  TOTAL: {penalidade_total:.1f}")
    
    return penalidade_total

def encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    logging.info("\n" + "="*80)
    logging.info(f"INICIANDO BUSCA DE CAMINHO")
    logging.info(f"Posição inicial: {pos_inicial}")
    logging.info(f"Objetivo: {pos_objetivo}")
    logging.info(f"Tem bola: {tem_bola}")
    logging.info(f"Obstáculos: {len(obstaculos)} posições")
    logging.info(f"Dimensões do grid: {largura_grid}x{altura_grid}")
    logging.info("="*80 + "\n")
    
    movimentos = [
        (1,0), (-1,0), (0,1), (0,-1),  # Horizontais/verticais
        (1,1), (1,-1), (-1,1), (-1,-1)  # Diagonais
    ]
    
    # Estado inicial
    inicio = Estado(
        pos_inicial,
        g=0,
        h=calcular_heuristica(pos_inicial, pos_objetivo),
        direcao=(0, 0),
        tem_bola=tem_bola
    )
    
    open_set = [inicio]
    closed_set = set()
    iteracao = 0
    
    while open_set:
        iteracao += 1
        atual = heapq.heappop(open_set)
        
        logging.info(f"\nIteração {iteracao}: Explorando nó {atual.posicao}")
        logging.info(f"  f={atual.f} (g={atual.g}, h={atual.h})")
        logging.info(f"  Direção atual: {atual.direcao}")
        logging.info(f"  Tem bola: {atual.tem_bola}")
        
        if atual.posicao == pos_objetivo:
            caminho = []
            node = atual
            while node:
                caminho.append(node.posicao)
                node = node.pai
            
            logging.info("\n" + "="*80)
            logging.info("CAMINHO ENCONTRADO COM SUCESSO!")
            logging.info(f"Posições no caminho: {len(caminho)}")
            logging.info(f"Custo total: {atual.g}")
            logging.info(f"Passos: {caminho[::-1]}")
            logging.info("="*80 + "\n")
            
            return caminho[::-1]
        
        closed_set.add((atual.posicao, atual.direcao, atual.tem_bola))
        
        for dx, dy in movimentos:
            nova_pos = (atual.posicao[0] + dx, atual.posicao[1] + dy)
            
            # Verificar limites do grid
            if not (0 <= nova_pos[0] < largura_grid and 0 <= nova_pos[1] < altura_grid):
                logging.debug(f"  {nova_pos} -> Fora dos limites do grid")
                continue
            
            # Verificar obstáculos
            if nova_pos in obstaculos:
                logging.debug(f"  {nova_pos} -> Obstáculo encontrado")
                continue
            
            # Calcular custos
            custo_base = custo_movimento(dx, dy, atual.tem_bola)
            custo_giro = custo_rotacao(atual.direcao, (dx, dy), atual.tem_bola)
            custo_adv = penalidade_adversarios(nova_pos, obstaculos)
            
            # Atualizar estado da bola
            nova_bola = atual.tem_bola or (nova_pos == pos_objetivo)
            
            # Criar novo estado
            novo_estado = Estado(
                posicao=nova_pos,
                pai=atual,
                g=atual.g + custo_base + custo_giro + custo_adv,
                h=calcular_heuristica(nova_pos, pos_objetivo),
                direcao=(dx, dy),
                tem_bola=nova_bola
            )
            
            logging.info(f"  Analisando movimento para {nova_pos}:")
            logging.info(f"    Custo base: {custo_base}")
            if custo_giro > 0:
                logging.info(f"    Custo rotação: {custo_giro}")
            if custo_adv > 0:
                logging.info(f"    Penalidade adversários: {custo_adv:.1f}")
            logging.info(f"    Custo total acumulado (g): {novo_estado.g}")
            logging.info(f"    Heurística (h): {novo_estado.h}")
            logging.info(f"    f = g + h: {novo_estado.f}")
            
            # Verificar se estado já foi visitado
            estado_chave = (novo_estado.posicao, novo_estado.direcao, novo_estado.tem_bola)
            if estado_chave in closed_set:
                logging.debug(f"    {nova_pos} -> Estado já visitado")
                continue
                
            heapq.heappush(open_set, novo_estado)
            logging.debug(f"    {nova_pos} -> Adicionado à open_set")
    
    logging.warning("\n" + "="*80)
    logging.warning("NENHUM CAMINHO ENCONTRADO!")
    logging.warning(f"Não foi possível encontrar um caminho de {pos_inicial} para {pos_objetivo}")
    logging.warning("="*80 + "\n")
    return []  # Caminho não encontrado
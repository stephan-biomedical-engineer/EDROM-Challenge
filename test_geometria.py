import logging
from datetime import datetime
import os

# Configurações básicas de log para registro da execução
os.makedirs("tests", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join("tests", f"geometria_{timestamp}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("GeometriaAlgoritmo")

def encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    """
    Algoritmo simples baseado em geometria analítica para mover o robô até o objetivo.
    Prioriza movimentos retos (x, depois y), e tenta diagonais se travado.
    """
    caminho = []
    x_atual, y_atual = pos_inicial
    x_objetivo, y_objetivo = pos_objetivo
    x_anterior, y_anterior = None, None
    visitados = set()
    max_passos = 20  # evita loops infinitos

    logger.info("="*20 + " INÍCIO DA BUSCA " + "="*20)
    logger.info(f"Posição inicial: {pos_inicial} | Objetivo: {pos_objetivo}")
    logger.info(f"Obstáculos detectados: {len(obstaculos)}")

    for passo in range(max_passos):
        visitados.add((x_atual, y_atual))
        logger.debug(f"Passo {passo}: posição atual: ({x_atual}, {y_atual})")

        # Objetivo alcançado
        if (x_atual, y_atual) == pos_objetivo:
            logger.info("Objetivo alcançado.")
            break

        # Direção preferencial em X e Y
        dx = 1 if x_objetivo > x_atual else -1 if x_objetivo < x_atual else 0
        dy = 1 if y_objetivo > y_atual else -1 if y_objetivo < y_atual else 0

        # Primeiro tenta mover no eixo X
        nova_pos = (x_atual + dx, y_atual)
        if dx != 0 and 0 <= nova_pos[0] < largura_grid and nova_pos not in obstaculos and nova_pos != (x_anterior, y_anterior):
            logger.debug(f"Movendo em X para {nova_pos}")
            caminho.append(nova_pos)
            x_anterior, y_anterior = x_atual, y_atual
            x_atual, y_atual = nova_pos
            continue

        # Depois tenta mover no eixo Y
        nova_pos = (x_atual, y_atual + dy)
        if dy != 0 and 0 <= nova_pos[1] < altura_grid and nova_pos not in obstaculos and nova_pos != (x_anterior, y_anterior):
            logger.debug(f"Movendo em Y para {nova_pos}")
            caminho.append(nova_pos)
            x_anterior, y_anterior = x_atual, y_atual
            x_atual, y_atual = nova_pos
            continue

        # Se travado, tenta uma direção diagonal alternativa
        movimento_feito = False
        for dx_alt, dy_alt in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nova_pos = (x_atual + dx_alt, y_atual + dy_alt)
            if 0 <= nova_pos[0] < largura_grid and 0 <= nova_pos[1] < altura_grid and nova_pos not in obstaculos and nova_pos not in visitados:
                logger.debug(f"Tentando diagonal para {nova_pos}")
                caminho.append(nova_pos)
                x_anterior, y_anterior = x_atual, y_atual
                x_atual, y_atual = nova_pos
                movimento_feito = True
                break

        # Nenhum movimento possível
        if not movimento_feito:
            logger.warning("Robô travado. Nenhum movimento possível.")
            break

    logger.info(f"Caminho final encontrado: {caminho}")
    return caminho

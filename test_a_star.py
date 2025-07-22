import heapq
import logging
from datetime import datetime
import os

# === CONFIGURAÇÃO DO LOGGING ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("tests", exist_ok=True)
logging.basicConfig(
    filename=f"tests/test_a_star_{timestamp}.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

POSICAO_INICIAL_ORIGINAL = None

class Estado:
    def __init__(self, posicao, pai=None, g=0, h=0):
        self.posicao = posicao
        self.pai = pai
        self.g = g  # custo real
        self.h = h  # heurística
        self.f = g + h  # custo total estimado

    def __lt__(self, outro):
        return self.f < outro.f

    def __eq__(self, outro):
        return self.posicao == outro.posicao and self.f == outro.f

    def __hash__(self):
        return hash(self.posicao)

def calcular_heuristica(pos_atual, pos_objetivo):
    return abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1])

def encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    global POSICAO_INICIAL_ORIGINAL
    if POSICAO_INICIAL_ORIGINAL is None:
        POSICAO_INICIAL_ORIGINAL = pos_inicial
        logging.debug(f"Posição inicial original registrada: {POSICAO_INICIAL_ORIGINAL}")

    logging.info(f"Iniciando cálculo do caminho de {pos_inicial} até {pos_objetivo}")
    logging.debug(f"Obstáculos: {obstaculos if obstaculos else 'Nenhum obstáculo'}")

    abertos = []
    estado_inicial = Estado(pos_inicial, g=0, h=calcular_heuristica(pos_inicial, pos_objetivo))
    heapq.heappush(abertos, estado_inicial)

    fechados = set()
    movimentos_possiveis = [
        (0, 1), (0, -1), (1, 0), (-1, 0),  # Reto
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
    ]

    while abertos:
        estado_atual = heapq.heappop(abertos)
        logging.debug(f"Explorando: {estado_atual.posicao} (f={estado_atual.f}, g={estado_atual.g}, h={estado_atual.h})")

        if estado_atual.posicao == pos_objetivo:
            caminho = []
            atual = estado_atual
            while atual is not None:
                caminho.append(atual.posicao)
                atual = atual.pai
            caminho_final = caminho[::-1]
            logging.info(f"Caminho encontrado: {caminho_final}")
            return caminho_final

        fechados.add(estado_atual.posicao)

        for dx, dy in movimentos_possiveis:
            nova_posicao = (estado_atual.posicao[0] + dx, estado_atual.posicao[1] + dy)

            if not (0 <= nova_posicao[0] < largura_grid and 0 <= nova_posicao[1] < altura_grid):
                continue

            if nova_posicao in obstaculos or nova_posicao in fechados:
                continue

            novo_g = estado_atual.g + 1
            estado_vizinho = Estado(
                posicao=nova_posicao,
                pai=estado_atual,
                g=novo_g,
                h=calcular_heuristica(nova_posicao, pos_objetivo)
            )

            ja_existe = False
            for existente in abertos:
                if existente.posicao == nova_posicao:
                    ja_existe = True
                    if novo_g < existente.g:
                        existente.g = novo_g
                        existente.f = novo_g + existente.h
                        existente.pai = estado_atual
                        heapq.heappush(abertos, existente)
                        logging.debug(f"Atualizado: {nova_posicao} com custo menor g={novo_g}")
                    break

            if not ja_existe:
                heapq.heappush(abertos, estado_vizinho)
                logging.debug(f"Adicionado novo estado: {nova_posicao} com f={estado_vizinho.f}")

    logging.warning("AVISO: Não foi possível encontrar um caminho para o objetivo.")
    return []

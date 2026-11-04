"""
medir_b_m.py - Estima b (fator de ramificacao) e m (profundidade) do Othello 8x8.

Joga 300 partidas com jogadas aleatorias (semente 3) e conta:
  b = media de jogadas legais por posicao (sem contar as posicoes em que o jogador passa)
  m = media de lances por partida (contando os passes)

Uso:  python medir_b_m.py
"""
import math
import random
import statistics
from othello import PASSAR, estado_inicial, acoes, resultado, terminal

SEMENTE = 3
N_PARTIDAS = 300

rng = random.Random(SEMENTE)
jogadas_por_posicao = []     # quantas jogadas legais havia em cada posicao
lances_por_partida = []      # quantos lances teve cada partida

for _ in range(N_PARTIDAS):
    s = estado_inicial(8)
    lances = 0
    while not terminal(s):
        a = acoes(s)
        if a != [PASSAR]:
            jogadas_por_posicao.append(len(a))
        s = resultado(s, rng.choice(a))
        lances += 1
    lances_por_partida.append(lances)

b = statistics.mean(jogadas_por_posicao)
m = statistics.mean(lances_por_partida)

print(f"{N_PARTIDAS} partidas aleatorias (semente {SEMENTE})")
print(f"b = {b:.2f} jogadas legais por posicao (maximo {max(jogadas_por_posicao)})")
print(f"m = {m:.2f} lances por partida (minimo {min(lances_por_partida)}, maximo {max(lances_por_partida)})")
print(f"b^m = {b:.1f}^{m:.0f} = 10^{m * math.log10(b):.1f} nos")
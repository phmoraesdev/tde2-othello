"""
experimento.py - Protocolo experimental (ID2.3).

PROTOCOLO (fixado antes de rodar):
  * Agente principal: alfa-beta, profundidade d=4, EVAL de busca.py,
    ordenacao de jogadas ligada.
  * Aberturas: 50 posicoes DISTINTAS, cada uma obtida com 4 lances
    aleatorios a partir de s0 (semente 7).
  * Cada abertura e jogada DUAS vezes, trocando as cores: o agente A
    joga uma vez de pretas e uma vez de brancas -> 100 partidas por confronto.
  * O agente aleatorio usa a semente 1000 + numero da partida.
  * Unidade de custo: nos visitados por lance (ver busca.py).
  * Um eixo variado por confronto; os outros dois travados.

Uso:  python experimento.py            (todos os confrontos, demora ~30 min)
      python experimento.py rapido     (5 aberturas, so para testar)
Saida: na tela e em resultados/resumo.txt
"""
import math
import os
import random
import statistics
import sys

from agentes import AgenteAleatorio, AgenteAlfaBeta
from othello import PRETAS, estado_inicial, acoes, resultado, terminal, placar

SEMENTE_ABERTURAS = 7
N_ABERTURAS = 50
LANCES_ABERTURA = 4

# Cada confronto: (nome, eixo variado, agente A, agente B).
# Um agente e "aleatorio" ou (profundidade, ordenacao ligada?).
CONFRONTOS = [
    # E1: linha de base. O MESMO agente em d = 1, 2, 3, 4 contra o aleatorio.
    ("E1 d=1 x aleatorio", "nenhum (linha de base)", (1, True), "aleatorio"),
    ("E1 d=2 x aleatorio", "nenhum (linha de base)", (2, True), "aleatorio"),
    ("E1 d=3 x aleatorio", "nenhum (linha de base)", (3, True), "aleatorio"),
    ("E1 d=4 x aleatorio", "nenhum (linha de base)", (4, True), "aleatorio"),
    # E2: eixo VISAO. Agente principal (d=4) contra ele mesmo com d=2.
    ("E2 visao: d=4 x d=2", "profundidade (4 contra 2); EVAL e ordenacao iguais",
     (4, True), (2, True)),
    # E3: eixo EFICIENCIA. Mesma profundidade e mesma EVAL, so muda a ordenacao.
    ("E3 eficiencia: ordenado x natural", "ordenacao (com contra sem); d=4 e EVAL iguais",
     (4, True), (4, False)),
]


def criar_agente(tipo, i_partida):
    if tipo == "aleatorio":
        return AgenteAleatorio(1000 + i_partida)
    prof, ordenar = tipo
    return AgenteAlfaBeta(prof, ordenar=ordenar)


def sortear_aberturas(n_aberturas):
    rng = random.Random(SEMENTE_ABERTURAS)
    aberturas = []
    while len(aberturas) < n_aberturas:
        s = estado_inicial(8)
        for _ in range(LANCES_ABERTURA):
            s = resultado(s, rng.choice(acoes(s)))
        if s not in aberturas:
            aberturas.append(s)
    return aberturas


def jogar_partida(a, b, abertura, a_de_pretas):
    """Joga uma partida completa entre os agentes a e b. Devolve a diferenca
    de pecas do ponto de vista de A e a lista de nos por lance de cada um."""
    if a_de_pretas:
        jogador = {PRETAS: a, -PRETAS: b}
    else:
        jogador = {PRETAS: b, -PRETAS: a}
    nos_a, nos_b = [], []

    s = abertura
    while not terminal(s):
        agente = jogador[s[1]]
        s = resultado(s, agente.jogar(s))
        if agente is a:
            nos_a.append(agente.nos_ultimo_lance)
        else:
            nos_b.append(agente.nos_ultimo_lance)

    pretas, brancas = placar(s)
    dif = (pretas - brancas) if a_de_pretas else (brancas - pretas)
    return dif, nos_a, nos_b


def intervalo_95(v, n):
    """Intervalo de confianca de 95% (Wilson) para a taxa de vitoria v/n.
    E a aproximacao normal corrigida para nao colapsar em 0% ou 100%."""
    z, p = 1.96, v / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centro - meia, centro + meia


def resumir(nome, eixo, nome_a, nome_b, partidas):
    """partidas = lista de (lado de A, dif. de pecas, nos de A, nos de B)."""
    linhas = [f"== {nome} ==  eixo variado: {eixo}",
              f"   A = {nome_a}   B = {nome_b}"]
    for lado in ("pretas", "brancas", "total"):
        difs = [dif for (l, dif, _, _) in partidas if lado == "total" or l == lado]
        v = sum(d > 0 for d in difs)
        e = sum(d == 0 for d in difs)
        d = sum(d < 0 for d in difs)
        lo, hi = intervalo_95(v, len(difs))
        linhas.append(f"   A de {lado:7}: {v:3}V {e:2}E {d:3}D em {len(difs):3}  "
                      f"taxa {100 * v / len(difs):5.1f}% [IC95 {100 * lo:.0f}-{100 * hi:.0f}%]  "
                      f"dif. pecas media {statistics.mean(difs):+.1f}  pior {min(difs):+d}")
    for i, rotulo in ((2, "A"), (3, "B")):
        por_lance = [x for p in partidas for x in p[i]]
        por_partida = [sum(p[i]) for p in partidas]
        if max(por_lance) == 0:
            linhas.append(f"   nos {rotulo}: 0 (nao faz busca)")
            continue
        linhas.append(f"   nos/lance {rotulo}: media {statistics.mean(por_lance):8.0f}  "
                      f"mediana {statistics.median(por_lance):7.0f}  "
                      f"pior caso {max(por_lance):7}   "
                      f"nos/partida: media {statistics.mean(por_partida):9.0f}  "
                      f"pior {max(por_partida):8}")
    return "\n".join(linhas)


def main():
    n_aberturas = 5 if "rapido" in sys.argv else N_ABERTURAS
    aberturas = sortear_aberturas(n_aberturas)

    blocos = [f"Protocolo: {n_aberturas} aberturas distintas ({LANCES_ABERTURA} lances "
              f"aleatorios, semente {SEMENTE_ABERTURAS}), cada uma jogada 2x trocando as "
              f"cores = {2 * n_aberturas} partidas por confronto. Custo em nos visitados."]

    for nome, eixo, tipo_a, tipo_b in CONFRONTOS:
        partidas = []
        for ia, abertura in enumerate(aberturas):
            for a_de_pretas in (True, False):          # mesma abertura, cores trocadas
                i_partida = 2 * ia + (0 if a_de_pretas else 1)
                a = criar_agente(tipo_a, i_partida)
                b = criar_agente(tipo_b, i_partida)
                dif, nos_a, nos_b = jogar_partida(a, b, abertura, a_de_pretas)
                lado = "pretas" if a_de_pretas else "brancas"
                partidas.append((lado, dif, nos_a, nos_b))
        bloco = resumir(nome, eixo, a.nome, b.nome, partidas)
        print(bloco + "\n", flush=True)
        blocos.append(bloco)

    os.makedirs("resultados", exist_ok=True)
    with open("resultados/resumo.txt", "w") as f:
        f.write("\n\n".join(blocos) + "\n")


if __name__ == "__main__":
    main()

"""
verificar.py - Verificacao obrigatoria (ID2.2, Teorema 1 da Aula 7).

Em profundidade COMPLETA (sem corte, sem heuristica), o alfa-beta chamado
na raiz com janela (-inf, +inf) tem que devolver EXATAMENTE o mesmo valor
que o Minimax puro. Testamos:
  (a) o Othello 4x4 a partir da posicao inicial e de posicoes sorteadas;
  (b) finais de Othello 8x8 com poucas casas vazias (o tabuleiro real).
Testamos o alfa-beta com e sem ordenacao de jogadas.

Uso:  python verificar.py
"""
import math
import random
import busca
from othello import estado_inicial, acoes, resultado, terminal, VAZIO

SEMENTE = 42


def posicao_sorteada(rng, n, lances_aleatorios):
    """Joga 'lances_aleatorios' lances ao acaso a partir de s0."""
    s = estado_inicial(n)
    for _ in range(lances_aleatorios):
        if terminal(s):
            break
        s = resultado(s, rng.choice(acoes(s)))
    return s


def final_8x8(rng, vazias):
    """Partida aleatoria no 8x8 ate restarem 'vazias' casas vazias."""
    while True:
        s = estado_inicial(8)
        while not terminal(s) and s[0].count(VAZIO) > vazias:
            s = resultado(s, rng.choice(acoes(s)))
        if not terminal(s):
            return s


def comparar(s):
    busca.zerar_contador()
    v_mm = busca.minimax(s)
    nos_mm = busca.nos_visitados

    busca.zerar_contador()
    v_ab = busca.alfabeta(s, None, -math.inf, math.inf, ordenar=True)
    nos_ab = busca.nos_visitados

    busca.zerar_contador()
    v_ab2 = busca.alfabeta(s, None, -math.inf, math.inf, ordenar=False)
    nos_ab2 = busca.nos_visitados

    assert v_mm == v_ab == v_ab2, f"DIVERGIU em {s}: {v_mm} {v_ab} {v_ab2}"
    return v_mm, v_ab, v_ab2, nos_mm, nos_ab, nos_ab2


def main():
    rng = random.Random(SEMENTE)

    # (a) 4x4: posicao inicial + 49 posicoes distintas sorteadas
    inst_4x4 = [estado_inicial(4)]
    while len(inst_4x4) < 50:
        s = posicao_sorteada(rng, 4, rng.randint(1, 6))
        if not terminal(s) and s not in inst_4x4:
            inst_4x4.append(s)

    # (b) 8x8: 20 finais com 9 casas vazias
    inst_8x8 = [final_8x8(rng, 9) for _ in range(20)]

    for nome, insts in [("Othello 4x4", inst_4x4), ("Finais 8x8 (9 vazias)", inst_8x8)]:
        print(f"\n=== {nome}: {len(insts)} posicoes, cada uma resolvida ATE O FIM ===")
        print(f"{'pos':>4} | {'valor minimax':>13} | {'alfa-beta c/ ord':>16} | {'alfa-beta s/ ord':>16} | "
              f"{'nos minimax':>11} | {'nos ab c/ ord':>13} | {'nos ab s/ ord':>13} | igual?")
        tot_mm = tot_ab = tot_ab2 = 0
        valor_s0 = None
        for i, s in enumerate(insts, start=1):
            v_mm, v_ab, v_ab2, nmm, nab, nab2 = comparar(s)
            if i == 1 and nome.startswith("Othello 4x4"):
                valor_s0 = v_mm
            tot_mm, tot_ab, tot_ab2 = tot_mm + nmm, tot_ab + nab, tot_ab2 + nab2
            igual = "SIM" if v_mm == v_ab == v_ab2 else "NAO"
            print(f"{i:>4} | {v_mm:>13} | {v_ab:>16} | {v_ab2:>16} | "
                  f"{nmm:>11,} | {nab:>13,} | {nab2:>13,} | {igual}")
        if valor_s0 is not None:
            print(f"4x4 a partir de s0: valor = {valor_s0} "
                  f"(= {valor_s0 // 1000} pecas para MAX)")
        print(f"{nome}: {len(insts)} instancias, Minimax == alfa-beta em TODAS")
        print(f"   nos visitados (total)  minimax: {tot_mm:,}   "
              f"alfa-beta c/ ordenacao: {tot_ab:,}   "
              f"alfa-beta s/ ordenacao: {tot_ab2:,}")
        print(f"   o alfa-beta c/ ordenacao visitou {100 * tot_ab / tot_mm:.1f}% "
              f"dos nos do minimax")

    print()
    print(f"alfa-beta verificado em {len(inst_4x4) + len(inst_8x8)} instancias "
          f"(semente {SEMENTE})")


if __name__ == "__main__":
    main()
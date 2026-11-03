"""
jogar.py - Partida ao vivo no terminal, com o contador de nos visivel
(item da apresentacao: "uma partida ao vivo, com o contador de nos na tela").

Uso:
  python jogar.py          agente d=4 (X, pretas) contra o aleatorio (O, brancas)
  python jogar.py 4 2      agente d=4 (X) contra agente d=2 (O)

No tabuleiro, '*' marca as jogadas legais de quem vai jogar.
"""
import sys
from agentes import AgenteAlfaBeta, AgenteAleatorio
from othello import (PRETAS, BRANCAS, PASSAR, estado_inicial, acoes, resultado,
                     terminal, placar, desenhar, nome_casa)


def main():
    d_pretas = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    pretas = AgenteAlfaBeta(d_pretas)
    brancas = AgenteAlfaBeta(int(sys.argv[2])) if len(sys.argv) > 2 else AgenteAleatorio(1)
    jogadores = {PRETAS: pretas, BRANCAS: brancas}

    total = {PRETAS: 0, BRANCAS: 0}
    s = estado_inicial(8)
    while not terminal(s):
        print()
        print(desenhar(s, marcar=[c for c in acoes(s) if c is not PASSAR]))
        agente = jogadores[s[1]]
        a = agente.jogar(s)
        total[s[1]] += agente.nos_ultimo_lance
        cor = "X" if s[1] == PRETAS else "O"
        print(f"{cor} ({agente.nome}) jogou {nome_casa(a)}"
              f"   | nos neste lance: {agente.nos_ultimo_lance:,}"
              f"   | nos acumulados de {cor}: {total[s[1]]:,}")
        s = resultado(s, a)

    print()
    print(desenhar(s))
    p, b = placar(s)
    print("FIM:", "pretas (X) vencem" if p > b else "brancas (O) vencem" if b > p else "empate",
          f"{p} x {b}")
    print(f"nos visitados no total: X = {total[PRETAS]:,}   O = {total[BRANCAS]:,}")


if __name__ == "__main__":
    main()

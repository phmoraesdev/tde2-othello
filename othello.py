"""
Regras do Othello (formalizacao do jogo, ID2.1).

Funciona para qualquer tabuleiro N x N com N par (8 = jogo do trabalho,
4 = instancia pequena usada so na verificacao Minimax = alfa-beta).

Convencoes:
  PRETAS = +1  -> jogador MAX (joga primeiro)
  BRANCAS = -1 -> jogador MIN
  VAZIO = 0

ESTADO = (tabuleiro, jogador_da_vez)
  tabuleiro e uma tupla com N*N inteiros (linha a linha).
  O jogador da vez faz parte do estado: sem ele, JOGADOR(s) nao seria
  funcao do estado (o mesmo tabuleiro pode ser a vez de qualquer um,
  por causa do "passar").
"""

PRETAS, BRANCAS, VAZIO = 1, -1, 0
PASSAR = None          # acao especial: usada so quando nao ha jogada legal

# as 8 direcoes: horizontal, vertical e diagonais
DIRECOES = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def estado_inicial(n=8):
    """s0: as 4 pecas centrais em diagonal, pretas comecam."""
    tab = [VAZIO] * (n * n)
    m = n // 2
    tab[(m - 1) * n + (m - 1)] = BRANCAS
    tab[m * n + m] = BRANCAS
    tab[(m - 1) * n + m] = PRETAS
    tab[m * n + (m - 1)] = PRETAS
    return (tuple(tab), PRETAS)


def tamanho(tab):
    """Lado do tabuleiro (8 para 64 casas, 4 para 16)."""
    return int(len(tab) ** 0.5)


def pecas_viradas(tab, casa, jogador):
    """Lista das pecas do adversario que seriam viradas se 'jogador'
    colocasse uma peca em 'casa'. Lista vazia = jogada ilegal."""
    if tab[casa] != VAZIO:
        return []
    n = tamanho(tab)
    lin, col = divmod(casa, n)
    viradas = []
    for dl, dc in DIRECOES:
        l, c = lin + dl, col + dc
        linha = []                      # pecas do adversario nesta direcao
        while 0 <= l < n and 0 <= c < n and tab[l * n + c] == -jogador:
            linha.append(l * n + c)
            l, c = l + dl, c + dc
        # so vale se houver pelo menos 1 peca do adversario e depois uma nossa
        if linha and 0 <= l < n and 0 <= c < n and tab[l * n + c] == jogador:
            viradas.extend(linha)
    return viradas


def jogadas_legais(tab, jogador):
    """Casas onde 'jogador' pode colocar uma peca (ordem natural 0..N*N-1)."""
    return [casa for casa in range(len(tab)) if pecas_viradas(tab, casa, jogador)]


def acoes(estado):
    """ACOES(s): jogadas legais do jogador da vez.
    Se ele nao tem nenhuma (e o jogo nao acabou), a unica acao e PASSAR."""
    tab, jogador = estado
    lances = jogadas_legais(tab, jogador)
    if lances:
        return lances
    if jogadas_legais(tab, -jogador):
        return [PASSAR]
    return []                           # ninguem joga: estado terminal


def resultado(estado, acao):
    """RESULTADO(s, a): coloca a peca, vira as cercadas e troca a vez."""
    tab, jogador = estado
    if acao is PASSAR:
        return (tab, -jogador)
    novo = list(tab)
    novo[acao] = jogador
    for casa in pecas_viradas(tab, acao, jogador):
        novo[casa] = jogador
    return (tuple(novo), -jogador)


def terminal(estado):
    """TESTE-TERMINAL(s): nenhum dos dois jogadores tem jogada legal
    (inclui o tabuleiro cheio)."""
    tab, jogador = estado
    return not jogadas_legais(tab, jogador) and not jogadas_legais(tab, -jogador)


# Fator que garante que um fim de jogo real sempre vale mais (em modulo)
# que qualquer avaliacao heuristica (|EVAL| < 1000, ver busca.py).
VITORIA = 1000


def utilidade(estado):
    """UTILIDADE(s, MAX): um unico numero, sempre do ponto de vista das
    PRETAS (MAX): 1000 x (pecas pretas - pecas brancas).
    Positivo = MAX venceu, negativo = MIN venceu, zero = empate."""
    tab, _ = estado
    return VITORIA * sum(tab)          # pretas valem +1 e brancas -1


def placar(estado):
    tab, _ = estado
    return tab.count(PRETAS), tab.count(BRANCAS)


# ---------- utilidades de exibicao (nao fazem parte da formalizacao) ----------

def nome_casa(casa, n=8):
    """0 -> 'a1', 63 -> 'h8' (coluna = letra, linha = numero)."""
    if casa is PASSAR:
        return "passa"
    lin, col = divmod(casa, n)
    return "abcdefgh"[col] + str(lin + 1)


def desenhar(estado, marcar=()):
    tab, jogador = estado
    n = tamanho(tab)
    simbolo = {PRETAS: "X", BRANCAS: "O", VAZIO: "."}
    linhas = ["   " + " ".join("abcdefgh"[:n])]
    for l in range(n):
        cel = []
        for c in range(n):
            casa = l * n + c
            cel.append("*" if casa in marcar else simbolo[tab[casa]])
        linhas.append(f"{l + 1:2} " + " ".join(cel))
    p, b = placar(estado)
    vez = "X (pretas)" if jogador == PRETAS else "O (brancas)"
    linhas.append(f"   X={p}  O={b}   vez: {vez}")
    return "\n".join(linhas)

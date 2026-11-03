"""
busca.py - Minimax puro, alfa-beta, funcao de avaliacao e ordenacao (ID2.2).

Unidade de custo: NOS VISITADOS = numero de chamadas da funcao recursiva
(cada chamada examina exatamente um estado). Nao usamos segundos.
"""
import math
from othello import (PRETAS, BRANCAS, PASSAR, acoes, resultado, utilidade,
                     jogadas_legais, tamanho)

# ---------------------------------------------------------------------------
# Contador de nos (a unidade de custo do trabalho)
# ---------------------------------------------------------------------------
nos_visitados = 0


def zerar_contador():
    global nos_visitados
    nos_visitados = 0


# ---------------------------------------------------------------------------
# 1) MINIMAX PURO: sem poda, sem corte de profundidade, sem heuristica.
#    Vai ate o fim do jogo. So serve de referencia de corretude
#    (verificar.py), porque no 8x8 completo ele nunca terminaria.
# ---------------------------------------------------------------------------
def minimax(estado):
    global nos_visitados
    nos_visitados += 1

    lances = acoes(estado)
    if not lances:                          # TESTE-TERMINAL
        return utilidade(estado)

    valores = [minimax(resultado(estado, a)) for a in lances]

    if estado[1] == PRETAS:                 # vez de MAX
        return max(valores)
    else:                                   # vez de MIN
        return min(valores)


# ---------------------------------------------------------------------------
# 2) ALFA-BETA: mesmo valor que o Minimax (Teorema 1), visitando menos nos.
#    alfa = melhor valor que MAX ja garantiu no caminho ate aqui
#    beta = melhor valor que MIN ja garantiu no caminho ate aqui
#    Se alfa >= beta, o resto dos filhos nao pode mudar a decisao: poda.
# ---------------------------------------------------------------------------
def alfabeta(estado, prof=None, alfa=-math.inf, beta=math.inf,
             aval=None, ordenar=True):
    global nos_visitados
    nos_visitados += 1

    lances = acoes(estado)
    if not lances:                          # TESTE-TERMINAL
        return utilidade(estado)
    if prof == 0:                           # corte de profundidade -> heuristica
        return aval(estado)
    if ordenar:
        lances = ordenar_lances(lances, estado[0])

    prox = None if prof is None else prof - 1

    if estado[1] == PRETAS:                 # MAX: VALOR-MAX
        v = -math.inf
        for a in lances:
            v = max(v, alfabeta(resultado(estado, a), prox, alfa, beta, aval, ordenar))
            if v >= beta:                   # MIN nunca deixaria chegar aqui
                return v                    # poda beta
            alfa = max(alfa, v)
        return v
    else:                                   # MIN: VALOR-MIN
        v = math.inf
        for a in lances:
            v = min(v, alfabeta(resultado(estado, a), prox, alfa, beta, aval, ordenar))
            if v <= alfa:                   # MAX nunca deixaria chegar aqui
                return v                    # poda alfa
            beta = min(beta, v)
        return v


def melhor_lance(estado, prof, aval, ordenar=True):
    """Decisao na raiz: devolve (lance escolhido, valor). Em empate de valor
    fica o primeiro lance da lista (desempate deterministico)."""
    global nos_visitados
    nos_visitados += 1                      # a raiz tambem e um no visitado
    lances = acoes(estado)
    if ordenar:
        lances = ordenar_lances(lances, estado[0])
    max_joga = estado[1] == PRETAS

    alfa, beta = -math.inf, math.inf
    escolhido, melhor = lances[0], (-math.inf if max_joga else math.inf)
    for a in lances:
        v = alfabeta(resultado(estado, a), prof - 1, alfa, beta, aval, ordenar)
        if max_joga and v > melhor:
            escolhido, melhor = a, v
            alfa = max(alfa, v)
        elif not max_joga and v < melhor:
            escolhido, melhor = a, v
            beta = min(beta, v)
    return escolhido, melhor


# ---------------------------------------------------------------------------
# 3) ORDENACAO DE JOGADAS (heuristica barata, so olha a casa de destino)
#    cantos primeiro, depois bordas, depois o miolo, e por ultimo as casas
#    vizinhas dos cantos, que costumam entregar o canto ao adversario.
# ---------------------------------------------------------------------------
def prioridade_casa(casa, n):
    l, c = divmod(casa, n)
    borda_l, borda_c = l in (0, n - 1), c in (0, n - 1)
    perto_l, perto_c = l in (1, n - 2), c in (1, n - 2)
    if borda_l and borda_c:
        return 4                            # canto
    if perto_l and perto_c:
        return 0                            # casa "X" (diagonal do canto)
    if (borda_l and perto_c) or (borda_c and perto_l):
        return 1                            # casa "C" (ao lado do canto, na borda)
    if borda_l or borda_c:
        return 3                            # demais casas de borda
    return 2                                # miolo


def ordenar_lances(lances, tab):
    if lances == [PASSAR]:
        return lances
    n = tamanho(tab)
    # sorted e estavel: empates mantem a ordem natural
    return sorted(lances, key=lambda casa: -prioridade_casa(casa, n))


# ---------------------------------------------------------------------------
# 4) FUNCAO DE AVALIACAO (sempre do ponto de vista de MAX = pretas)
#    EVAL = 25 x (cantos)  +  5 x (mobilidade)  +  1 x (pecas)
#    cada termo e (valor das pretas - valor das brancas)
#    Limite: |EVAL| <= 25*4 + 5*33 + 64 = 329 < 1000 = valor minimo de uma
#    vitoria real, entao um fim de jogo sempre domina a heuristica.
# ---------------------------------------------------------------------------
PESO_CANTOS = 25       # canto nunca pode ser virado: vantagem permanente
PESO_MOBILIDADE = 5    # mais opcoes agora = mais controle; poucas = forcado a jogar mal
PESO_PECAS = 1         # o objetivo final, mas instavel no meio do jogo: peso baixo


def avaliar(estado):
    tab, _ = estado
    n = tamanho(tab)
    cantos = [0, n - 1, n * (n - 1), n * n - 1]
    dif_cantos = sum(tab[c] for c in cantos)
    dif_mobilidade = len(jogadas_legais(tab, PRETAS)) - len(jogadas_legais(tab, BRANCAS))
    dif_pecas = sum(tab)
    return (PESO_CANTOS * dif_cantos
            + PESO_MOBILIDADE * dif_mobilidade
            + PESO_PECAS * dif_pecas)

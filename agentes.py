import random
import busca
from othello import acoes

# Sorteia uma jogada legal. 
# Nao busca, entao custa 0 nos por lance
class AgenteAleatorio:
    def __init__(self, semente):
        self.rng = random.Random(semente)
        self.nome = "aleatorio"
        self.nos_ultimo_lance = 0

    def jogar(self, estado):
        self.nos_ultimo_lance = 0
        return self.rng.choice(acoes(estado))

# O agente do trabalho: alfa-beta com profundidade fixa 'prof',
# funcao de avaliacao 'aval' e ordenacao de jogadas ligada ou nao.
class AgenteAlfaBeta:
    def __init__(self, prof, aval=busca.avaliar, ordenar=True):
        self.prof = prof
        self.aval = aval
        self.ordenar = ordenar
        self.nome = f"alfabeta d={prof}" + ("" if ordenar else " sem ordenacao")
        self.nos_ultimo_lance = 0

    def jogar(self, estado):
        busca.zerar_contador()
        lance, _ = busca.melhor_lance(estado, self.prof, self.aval, self.ordenar)
        self.nos_ultimo_lance = busca.nos_visitados
        return lance

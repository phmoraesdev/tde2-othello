# Apresentação

- 1 min	O jogo e por que ele satisfaz as cinco restrições
- 3 min	A formalização: os seis componentes, com b e m estimados
- 3 min	Uma partida ao vivo ou gravada, com o contador de nós visível na tela
- 3 min	A tabela de comparação, na mesma unidade e com a distribuição
- 2 min	O que não funcionou, e as garantias que o seu agente não tem

# Equipe

- Alan Filipe Reginato de França Santos
- Antonio Bernardo Zilio Tomasi
- Gustavo Lona Grespan
- Pedro Henrique Moraes

## 1. Jogo escolhido (`othello.py`)

### Regras

Você coloca uma peça numa casa vazia que **cerque** peças do adversário em linha reta (horizontal, vertical ou diagonal), e elas viram para a sua cor. Quem não tem jogada legal **passa**. Acaba quando
ninguém pode jogar; vence quem tiver mais peças.

**Jogada legal** = casa vazia que vira **pelo menos uma** peça do adversário.

### As cinco verificações
| Pergunta | Resposta |
|---|---|
| Dois jogadores? | Sim: pretas (MAX) e brancas (MIN) |
| Soma zero? | Sim: o resultado é um número só (pretas − brancas); o que um ganha o outro perde |
| Informação perfeita? | Sim: o tabuleiro inteiro está à vista |
| Determinístico? | Sim: não tem dado nem sorteio |
| Horizonte finito? | Sim: cada lance ocupa uma casa vazia para sempre, então são no máximo 60 lances |

## 2. A formalização (`othello.py`)
 
### Estado
É a tupla `(tab, jogador)`. Não tem função própria: é criada no `estado_inicial` e no `resultado`.
- `tab` tem 64 números, um por casa: **+1** = preta, **−1** = branca, **0** = vazia.
- `jogador` é de quem é a vez: **+1** = pretas (MAX), **−1** = brancas (MIN).
- **A vez precisa estar no estado** por causa do PASSAR: o mesmo tabuleiro pode ser a vez de qualquer um dos
  dois. Sem ela, JOGADOR(s) não seria função do estado. Com ela, JOGADOR(s) é só `estado[1]`.
- Uma casa é um número: `casa = linha × 8 + coluna` (a1 = 0, h8 = 63).
```python
return (tuple(tab), PRETAS)        # linha 34: o primeiro estado
tab, jogador = estado              # as funções abrem o estado assim
```
 
### s₀: `estado_inicial()`
Tabuleiro vazio com as 4 peças do centro em diagonal, e vez das pretas. Com `n=4`, cria o 4×4 da verificação.
```python
tab[(m-1)*n + (m-1)] = BRANCAS     # d4      tab[(m-1)*n + m] = PRETAS   # e4
tab[m*n + m]         = BRANCAS     # e5      tab[m*n + (m-1)] = PRETAS   # d5
return (tuple(tab), PRETAS)
```
 
### AÇÕES(s): `acoes()`
Uma jogada é legal se a casa está vazia e vira pelo menos uma peça do adversário. Quem confere isso é a
`pecas_viradas`: em cada uma das 8 direções, ela anda enquanto encontra peças do adversário (`-jogador`). As
peças viram se ela passou por pelo menos uma e parou numa peça **sua**.
```python
while dentro and tab[l*n + c] == -jogador:          # anda sobre peças do adversário
    linha.append(l*n + c)
if linha and dentro and tab[l*n + c] == jogador:    # terminou numa peça minha?
    viradas.extend(linha)                           # então estão cercadas
```
A `acoes` usa isso e tem três casos:
```python
if lances:                         return lances     # tenho jogada
if jogadas_legais(tab, -jogador):  return [PASSAR]   # não tenho, o outro tem: passo
return []                                            # ninguém tem: fim de jogo
```
*Exemplo:* no primeiro lance, X joga em d3. Para baixo, ele passa por d4 (O) e para em d5 (X), então d4 vira.
 
### RESULTADO(s, a): `resultado()`
Coloca a peça, vira as cercadas e troca a vez. Cria um estado **novo**, porque a tupla original não muda.
```python
if acao is PASSAR: return (tab, -jogador)     # passar: só troca a vez
novo = list(tab)
novo[acao] = jogador                          # coloca a peça
for casa in pecas_viradas(tab, acao, jogador):
    novo[casa] = jogador                      # vira as cercadas
return (tuple(novo), -jogador)                # -jogador = vez do outro
```
 
### TESTE-TERMINAL(s): `terminal()`
Acaba quando **nenhum dos dois** tem jogada legal (inclui o tabuleiro cheio). Sempre termina: são no máximo
60 colocações, e dois passes seguidos já são fim de jogo.
```python
return not jogadas_legais(tab, jogador) and not jogadas_legais(tab, -jogador)
```
 
### UTILIDADE(s, MAX): `utilidade()`
Um número só, do ponto de vista de MAX. `sum(tab)` dá pretas − brancas, porque as pretas valem +1 e as
brancas −1. Positivo = MAX ganhou, negativo = MIN ganhou, 0 = empate.
```python
return 1000 * sum(tab)        # ex.: 40 pretas e 24 brancas -> +16.000
```
O **× 1000** garante que uma vitória real (no mínimo 1000) vale mais que qualquer estimativa da função de
avaliação (no máximo 329). Não muda qual jogada é a melhor.
 
**b e m (o tamanho do problema):**
- **b** (fator de ramificação) = jogadas legais por posição, em média: **≈ 8,6**
- **m** (profundidade) = lances por partida: **≈ 60**
- Medidos em 300 partidas aleatórias (semente 3).
- b^m ≈ 8,6^60 = 10^(60 × 0,93) ≈ **10^56 nós**. A 1 bilhão de nós por segundo, seriam ~10^39 anos.


---

## 3. Partida ao vivo com o contador de nós
  
1. Rode **`python jogar.py`**: o agente d=4 (X, pretas) joga contra o aleatório (O, brancas).
 
### A diferença entre os dois agentes
Os dois usam as mesmas regras (`othello.py`). A diferença é **como escolhem a jogada** (`agentes.py`):
 
| | Aleatório (O) | Alfa-beta d=4 (X) |
|---|---|---|
| Como escolhe | Sorteia uma das jogadas legais | Imagina 4 lances à frente (o dele, a resposta, o dele, a resposta) e escolhe o melhor |
| Como julga a posição | Não julga | Com a função de avaliação: cantos, mobilidade e peças |
| Supõe que o adversário... | — | ...também joga bem (Minimax: ele maximiza, o outro minimiza) |
| Nós por lance | 0 (não busca) | centenas (média ~700) |
 
O alfa-beta ganha porque pega os cantos, evita entregar cantos e não fica sem jogadas. O aleatório faz
qualquer coisa. **Quem ganha é o agente, não a cor:** com `python jogar.py 2 4` o d=4 joga de brancas, e as
brancas ganham.
 
2. Rode **`python verificar.py`**
```
   Othello 4x4: 50 instancias, Minimax == alfa-beta em TODAS
      o alfa-beta c/ ordenacao visitou 3.9% dos nos do minimax
   Finais 8x8 (9 vazias): 20 instancias, Minimax == alfa-beta em TODAS
   alfa-beta verificado em 70 instancias (semente 42)
```
   > "Antes de usar o corte de profundidade, verificamos o alfa-beta: em 70 posições jogadas até o fim, ele
   > deu exatamente o mesmo valor que o Minimax puro, e no 4×4 visitou só 3,9% dos nós."
 
### Onde entra o Minimax
No `jogar.py`, **só o alfa-beta joga**: a função `minimax` não é chamada. O alfa-beta **é** o Minimax com
poda (MAX pega o maior, MIN pega o menor), só que para de olhar os galhos que não mudam a decisão. A função
`minimax` pura é usada **só no `verificar.py`**, como referência, para provar que o alfa-beta dá o mesmo valor.
O agente usa o alfa-beta porque escolhe a mesma jogada visitando muito menos nós.
 
---
 
## 4. Tabela de comparação
 

- abra o arquivo **`resultados/resumo.txt`**, que tem a saída completa das 600 partidas;
- se o professor quiser ver rodando, use `python experimento.py rapido`

| Parte da linha | O que significa |
|---|---|
| `== E2 ... ==` e `eixo variado` | Qual confronto é e o que muda entre os dois agentes |
| `A = ...  B = ...` | Os dois agentes. **Os resultados são sempre do ponto de vista de A** |
| `A de pretas` / `A de brancas` | Resultado de A em cada cor (50 partidas cada). Serve para ver que não tem bug de sinal |
| `A de total` | As 100 partidas juntas: **esse é o resultado do confronto** |
| `86V 0E 14D` | Vitórias, empates e derrotas de A |
| `taxa 86.0%` | Porcentagem de vitórias de A |
| `[IC95 78-91%]` | Intervalo de confiança. Se não inclui 50%, a diferença não é sorte |
| `dif. pecas media +28.3  pior -46` | Diferença de peças no final, na média e na pior partida de A |
| `nos/lance: media / mediana / pior caso` | Custo da busca por lance (a **distribuição** que o professor pede) |
| `nos/partida: media / pior` | Total de nós na partida inteira |
| `nos B: 0 (nao faz busca)` | Aparece no E1: o aleatório não faz busca, então custa 0 |
 

> "Para não repetir a mesma partida, sorteamos 50 aberturas e jogamos cada uma com as duas cores. Contra o
> aleatório, o agente d=4 ganhou as 100. Contra a versão d=2, ganhou 86%, e o intervalo não inclui 50%,
> então enxergar mais longe ajuda de verdade, mas custa 20 vezes mais nós. A ordenação não mudou a força,
> foi empate, mas economizou um terço dos nós."
 
---
 
## 5. O que não funcionou e garantias ausentes
  
**1. O que não funcionou**
- d=1 perdeu **15 de 100** para o aleatório: olhar só um lance à frente não basta.
- d=4 ainda perdeu **14 de 100** para d=2: a avaliação erra às vezes.
- O pior lance custou **8× a média** de nós (5.598 contra 699): a profundidade fixa não controla o custo.
**2. O que os dados NÃO provam**
- Que d=4 seja melhor que d=3 só olhando o aleatório (99% contra 100%): o aleatório é fraco demais para separar.
- Que a ordenação deixe o agente mais forte: 52% é empate.
- Que as cores influenciem o agente: no E3 as brancas ganharam 64 de 100, mas isso veio das aberturas.
- Nada sobre os pesos da avaliação: eles nunca foram variados.
**3. Garantias que o agente NÃO tem**
- Não joga perfeito: com corte e avaliação heurística, o valor é só uma **estimativa**.
- Não tem garantia contra um adversário perfeito.
- Não tem limite de nós por lance.
- Não tem quiescência: pode parar a busca no meio de uma troca (efeito horizonte).
- A verificação é um **teste** em 70 posições, não uma prova.
**O que falar:**
> "O agente não é perfeito: com profundidade 1 perde 15% para o aleatório, e com profundidade 4 ainda perdeu
> 14 partidas para a versão d=2. Como cortamos a busca, o valor é só uma estimativa, então não há garantia
> contra jogo perfeito nem limite de custo por lance. E não concluímos o que os dados não mostram: a
> ordenação deixa o agente mais barato, não mais forte."

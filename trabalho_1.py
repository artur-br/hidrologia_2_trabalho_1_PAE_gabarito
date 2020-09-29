#Código para gerar o gabarito do trabalho 1:

#Parâmetros calculados no QGIS:
#área da bacia (A), perímetro da bacia (P), comprimento do rio principal (L), declividade do curso d'agua principal

#Parâmetros a serem calculados aqui:
#tempo de concentração por quatro métodos empíricos (tc), coeficiente de compacidade (Kc), fator de forma (F)

#Função para calcular o tempo de concentração pelos 4 métodos:
def calculo_tempo_de_concentracao (L, S, method, CN = 0, c = 0, n = 0, I = 0):
    """
    :param L: Comprimento do rio principal (km)
    :param S: Declividade do curso d’água principal (m/m)
    :param method: Método para cálculo do tc: 'Kirpich', 'NRCS', 'FAA', 'Onda cinematica'
    :param CN: Curve number (SCS) (adimensional). Utilizado somente no método do NRCS
    :param c: Coeficiente superficial do Método Racional (adimensional). Utilizado somente no método FAA
    :param n: Rugosidade de Manning (adimensional). Utilizado somente no método da onda cinemática
    :param I: Intensidade da precipitação (mm/h). Utilizado somente no método da onda cinemática.
    :return: Tempo de concentração calculado pelo método escolhido (tc) (min)
    """

    from unicodedata import normalize
    method = normalize('NFKD', method).encode('ASCII', 'ignore').decode('ASCII').lower()

    if method == "kirpich":
        tc = 3.989 * (L ** 0.77) * (S ** (-0.385))

    elif method == "nrcs":
        if 0 < CN <= 100:
            tc = 3.42 * (L ** 0.8) * (((1000 / CN) - 9) ** 0.7) * (S ** -0.5)
        else:
            raise ValueError("Digite um valor válido de CN")

    elif method == "faa":
        if 0 < c < 1:
            tc = 22.73 * (1.1 - c) * (L ** 0.5) * (S ** -0.333)
        else:
            raise ValueError("Digite um valor válido de c")

    elif method == "onda cinematica":
        if I > 0 and n > 0:
            tc = 447 * ((n * L) ** 0.6) * (I ** -0.4) * (S ** -0.3)
        else:
            raise ValueError("Digite um valor válido de I e n")
    else:
        raise ValueError('Método inválido. Os métodos utilizáveis são: Kirpich, NRCS, FAA, Onda cinemática.')

    return tc

##Função para calular o coeficiente de compacidade
def calculo_Kc(P, A):
    """
    :param P: Perímetro da bacia (km)
    :param A: Área da bacia (km2)
    :return Kc: Coeficiente de compacidade (adimensional)
    """
    from math import pi
    Kc = 0.28 * (P / (A ** 0.5))
    #Kc = P / (2 * pi * ((A / pi) ** 1/2))

    return Kc

##Função para calcular o coeficiente de forma
def calculo_F (largura_media, comprimento_eixo):
    """
    :param largura_media: Largura média da bacia (m)
    :param comprimento_eixo: Comprimento do eixo da bacia (m). Distância medida da foz ao ponto mais longínquo da área.
    :return F: Fator de forma (adimensional)
    """
    F = largura_media / comprimento_eixo

    return F

def calculo_S(L, cota_alta, cota_baixa, method):
    """
    :param L: Comprimento do rio principal
    :param cota_alta: Cota mais alta
    :param cota_baixa: Cota mais baixa
    :param method: Método de cálculo, pode ser "extreme" ou "10-85"
    :return: 
    """
    if method == "10-85":
        S = (cota_alta - cota_baixa)/(0.75 * L)

    elif method == "extreme":
        S = (cota_alta - cota_baixa) / L

    return S

def calculo_media_ponderada(*args):
    """
    :param args: Entra com um argumento com duas listas. A primeira com as variáveis (CN, c ou n) e a segunda com
    as áreas respectivas de cada variável
    :return: retorna a média ponderada
    """
    denominador = sum(args[1])
    numerador = 0
    for i in range(len(args[0])):
        numerador += args[0][i] * args[1][i]
    media_ponderada = numerador / denominador
    return media_ponderada


##Função para calcular os parâmetros da taxa de infiltração:
from pyeasyga import pyeasyga
import random
import math


def create_individual(data):
    """
    Função para criar um indivíduo com os parâmetros na ordem [fo, fc, k].
    O fo é limitado inferiormente pelo menor valor do F_obs (dado) e limitado superiormente pelo valor máximo do F_obs.
    O fc é limitado inferiormente por 0.01 (valor arbitrário maior que zero) e o fo, já que o fc < fo
    O k é limitado entre 0.01 e 1
    :param data: Dicionário de dados da questão com o tempo e o F_obs
    :return: Indivíduo com 3 parâmetros sorteados aleatoriamente entre dois limites [fo, fc, k]
    """
    F_sorted = sorted(data['F_obs'])
    fo = random.uniform(F_sorted[1], F_sorted[-1])
    fc = random.uniform(0.01, fo)
    k = random.uniform(0.01, 1)
    individual = [fo, fc, k]
    return(individual)

def mutate(individual):
    """
    Esta função realiza a mutação de um indivíduo. A chance de mutação é dada quando declaramos o
    pyeasyga.GeneticAlgorithm.
    :param individual: Recebe um indivíduo criado pela função create_individual com os parâmetros [fo, fc, k]
    :return: Não há retorno, mas ocorre uma modificação em um elemento do indivíduo (um novo sorteio)
    """
    mutation_index = random.randrange(len(individual))
    if mutation_index == 0:
        individual[mutation_index] = random.uniform(individual[1]*0.5, individual[0]*1.5)
    elif mutation_index == 1:
        individual[mutation_index] = random.uniform(0.01, individual[0])
    elif mutation_index == 2:
        individual[mutation_index] = random.uniform(0.01, 1)

def cross_over(parent_1, parent_2):
    """
    Esta função realiza o cross over de dois indivíduos, os combinando, e, produzindo dois novos indivíduos. A chance
    de cross over é dada quando declaramos o pyeasyga.GeneticAlgorithm
    :param parent_1: O parente 1 é um indivíduo que será utilizado para o cross over
    :param parent_2: O parente 2 é um indivíduo que será utilizado para o cross over
    :return child_1, child_2: Dois novos indivíduos são gerados a partir da combinação dos dois parentes
    """
    child_1 = [parent_1[0], parent_1[1], parent_2[2]]
    child_2 = [parent_1[0], parent_2[1], parent_2[2]]
    return (child_1, child_2)


def fitness(individual, data):
    """
    Função aptidão que calcula o erro quadrático entre o F_calculado com os parâmetros dado por um indivíduo e o
    F_obs dado pela questão
    :param individual: Indivíduo com três elementos [fo, fc, k] gerado pela função create_individual
    :param data: Dicionário com o tempo e a infiltração acumulada observada (dados na questão)
    :return quadratic error: Retorna o erro quadrático comparando o F_calc com os parâmetros aleatórios do indivíduo
    com o F_obs dado pela questão
    """
    quadratic_error = 0
    for i in range(1, len(data['F_obs'])):
        F_calc = (individual[1] * data['time'][i]) + ((individual[0] - individual[1]) / individual[2]) * \
                 (1 - math.exp(-individual[2] * data['time'][i]))
        #F_calc = individual[1] + (individual[0] - individual[1]) * math.exp(-individual[2] * data["time"][i])
        quadratic_error += (data['F_obs'][i] - F_calc) ** 2
    return(quadratic_error)


def run_ga():
    """
    Executa a instância ga 10x para assegurar que será obtido um valor razoável para os parâmetros
    :return results: Results é uma lista com os resultados. O primeiro elemento é o erro quadrático e o segundo elemento
    é uma lista com os valores dos parâmetros na ordem [fo, fc, k]. A função executa 10x o algorítmo genético e o
    usuário seleciona qual o conjunto de parâmetros que deseja.
    """
    results = []
    for i in range(10):
        ga.run()
        results.append(ga.best_individual())
    for i in range(len(results)):
        print(i, results[i][0])
    return(results)

##########################################################################################################################
#Exemplo de aplicação
##########################################################################################################################

L = 21.4
S = calculo_S(L*1000, 584.881, 523.571, "10-85")
CN = 66.2
c = 0.205
n = 0.033
I = [5, 30]
P = 70.4
A = 101.6

calculo_tempo_de_concentracao(L, S, "Kirpich")
calculo_tempo_de_concentracao(L, S, "NRCS", CN =CN)
calculo_tempo_de_concentracao(L, S, "FAA", c=c)
calculo_tempo_de_concentracao(L, S, "Onda Cinematica", n=n, I=I[0])
calculo_tempo_de_concentracao(L, S, "Onda Cinematica", n=n, I=I[1])

calculo_Kc(P, A)
calculo_F(11.601, 15.010)

#curva H

data = {'time': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
        'F_obs': [72.2, 72.2, 68.8, 68.8, 61.9, 61.9, 55.0, 51.6, 41.3, 30.9, 30.9, 30.9]}

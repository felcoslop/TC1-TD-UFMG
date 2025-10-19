import numpy as np
from typing import Tuple

class FuncoesObjetivo:
    # Classe que calcula as funções objetivo f1 e f2 e verifica se as restrições estão sendo respeitadas
    
    def __init__(self, monitoramento):
        # Pega os dados do problema da classe principal
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
    
    def calcular_f1(self, x_ij: np.ndarray, h_ik: np.ndarray, y_jk: np.ndarray) -> float:
        # f1 = soma de todas as distâncias dos ativos até suas respectivas equipes de manutenção
        # x_ij é 1 se ativo i está na base j, 0 caso contrário
        # h_ik é 1 se ativo i está na equipe k, 0 caso contrário
        # y_jk é 1 se equipe k está na base j, 0 caso contrário
        
        # Calcula distância total considerando que cada ativo deve estar próximo de sua equipe
        # A distância é calculada entre o ativo e a base onde sua equipe está alocada
        distancia_total = 0.0
        
        for i in range(self.n_ativos):
            for k in range(self.s_equipes):
                if h_ik[i, k] == 1:  # Se ativo i está na equipe k
                    # Encontra a base onde a equipe k está alocada
                    for j in range(self.m_bases):
                        if y_jk[j, k] == 1:  # Se equipe k está na base j
                            distancia_total += self.distancias[i, j]
                            break
        
        return distancia_total
    
    def calcular_f2(self, h_ik: np.ndarray, y_jk: np.ndarray = None) -> float:
        # f2 = número de equipes que estão sendo usadas (S)
        # h_ik é 1 se ativo i está na equipe k, 0 caso contrário
        # y_jk é 1 se equipe k está na base j, 0 caso contrário
        
        # Conta equipes que têm pelo menos um ativo atribuído
        ativos_por_equipe = np.sum(h_ik, axis=0)
        equipes_utilizadas = np.sum(ativos_por_equipe > 0)
        
        return float(equipes_utilizadas)
    
    def calcular_violacao(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> float:
        """
        Calcula a medida quantitativa de violação das restrições.
        Retorna 0 se a solução é viável, caso contrário retorna a soma das violações ao quadrado.
        """
        violacao_total = 0.0
        
        # Restrição 1: cada equipe tem que estar em exatamente uma base (se estiver sendo usada)
        for k in range(self.s_equipes):
            soma_equipe = np.sum(y_jk[:, k])
            ativos_equipe = np.sum(h_ik[:, k])
            
            # Equipe não pode estar em mais de uma base
            if soma_equipe > 1:
                violacao_total += (soma_equipe - 1)**2
            
            # Se tem ativos, tem que estar em exatamente uma base
            if ativos_equipe > 0 and soma_equipe != 1:
                violacao_total += (abs(soma_equipe - 1))**2
            
            # Se está numa base, tem que ter ativos
            if soma_equipe == 1 and ativos_equipe == 0:
                violacao_total += 1.0
        
        # Restrição 2: cada ativo tem que estar em exatamente uma base
        for i in range(self.n_ativos):
            soma_bases = np.sum(x_ij[i, :])
            if soma_bases != 1:
                violacao_total += (soma_bases - 1)**2
        
        # Restrição 3: ativo só pode estar numa base se a base tiver pelo menos uma equipe
        for i in range(self.n_ativos):
            for j in range(self.m_bases):
                if x_ij[i, j] == 1:  # se ativo i está na base j
                    if np.sum(y_jk[j, :]) == 0:  # base j não tem nenhuma equipe
                        violacao_total += 1.0
        
        # Restrição 4: cada ativo tem que estar em exatamente uma equipe
        for i in range(self.n_ativos):
            soma_equipes = np.sum(h_ik[i, :])
            if soma_equipes != 1:
                violacao_total += (soma_equipes - 1)**2
        
        # Restrição 5: ativo só pode estar numa equipe se a equipe estiver na base do ativo
        for i in range(self.n_ativos):
            for k in range(self.s_equipes):
                if h_ik[i, k] == 1:  # se ativo i está na equipe k
                    # Encontra a base onde o ativo i está alocado
                    base_ativo = np.where(x_ij[i, :] == 1)[0]
                    if len(base_ativo) > 0:
                        base_id = base_ativo[0]
                        # Verifica se a equipe k está na mesma base onde o ativo i está alocado
                        if y_jk[base_id, k] != 1:  # equipe k não está na base do ativo
                            violacao_total += 1.0
        
        # Restrição 6: cada equipe tem que ter pelo menos eta*n/s ativos (se estiver sendo usada)
        for k in range(self.s_equipes):
            ativos_equipe = np.sum(h_ik[:, k])
            if ativos_equipe > 0:  # só verifica se a equipe tem ativos
                minimo_ativos = self.eta * self.n_ativos / self.s_equipes
                if ativos_equipe < minimo_ativos:
                    violacao_total += (minimo_ativos - ativos_equipe)**2
        
        return violacao_total
    
    def verificar_restricoes(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> bool:
        """
        Verifica se a solução respeita todas as restrições (retorna True/False).
        """
        return self.calcular_violacao(x_ij, y_jk, h_ik) == 0.0

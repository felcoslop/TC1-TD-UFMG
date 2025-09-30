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
    
    def calcular_f1(self, x_ij: np.ndarray) -> float:
        # f1 = soma de todas as distâncias dos ativos até suas bases
        # x_ij é 1 se ativo i está na base j, 0 caso contrário
        return np.sum(self.distancias * x_ij)
    
    def calcular_f2(self, h_ik: np.ndarray, y_jk: np.ndarray = None) -> float:
        # f2 = número de equipes que estão sendo usadas (S)
        # h_ik é 1 se ativo i está na equipe k, 0 caso contrário
        ativos_por_equipe = np.sum(h_ik, axis=0)
        equipes_utilizadas = np.sum(ativos_por_equipe > 0)
        return float(equipes_utilizadas)
    
    def verificar_restricoes(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> bool:
        # Verifica se a solução respeita todas as 6 restrições do problema
        
        # Restrição 1: cada equipe tem que estar em exatamente uma base (se estiver sendo usada)
        for k in range(self.s_equipes):
            soma_equipe = np.sum(y_jk[:, k])
            if soma_equipe > 1:  # equipe não pode estar em mais de uma base
                return False
            ativos_equipe = np.sum(h_ik[:, k])
            if ativos_equipe > 0 and soma_equipe != 1:  # se tem ativos, tem que estar numa base
                return False
            if soma_equipe == 1 and ativos_equipe == 0:  # se está numa base, tem que ter ativos
                return False
        
        # Restrição 2: cada ativo tem que estar em exatamente uma base
        for i in range(self.n_ativos):
            if np.sum(x_ij[i, :]) != 1:
                return False
        
        # Restrição 3: ativo só pode estar numa base se a base tiver pelo menos uma equipe
        for i in range(self.n_ativos):
            for j in range(self.m_bases):
                if x_ij[i, j] == 1:  # se ativo i está na base j
                    if np.sum(y_jk[j, :]) == 0:  # base j não tem nenhuma equipe
                        return False
        
        # Restrição 4: cada ativo tem que estar em exatamente uma equipe
        for i in range(self.n_ativos):
            if np.sum(h_ik[i, :]) != 1:
                return False
        
        # Restrição 5: ativo só pode estar numa equipe se a equipe estiver na base do ativo
        for i in range(self.n_ativos):
            for k in range(self.s_equipes):
                if h_ik[i, k] == 1:  # se ativo i está na equipe k
                    base_ativo = np.where(x_ij[i, :] == 1)[0]
                    if len(base_ativo) > 0:
                        base_id = base_ativo[0]
                        if y_jk[base_id, k] != 1:  # equipe k não está na base do ativo
                            return False
        
        # Restrição 6: cada equipe tem que ter pelo menos eta*n/s ativos (se estiver sendo usada)
        for k in range(self.s_equipes):
            ativos_equipe = np.sum(h_ik[:, k])
            if ativos_equipe > 0:  # só verifica se a equipe tem ativos
                minimo_ativos = self.eta * self.n_ativos / self.s_equipes
                if ativos_equipe < minimo_ativos:
                    return False
        
        return True

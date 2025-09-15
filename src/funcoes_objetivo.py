"""
Módulo de funções objetivo e verificação de restrições
para o problema de monitoramento de ativos.
"""

import numpy as np
from typing import Tuple

class FuncoesObjetivo:
    """
    Classe responsável pelas funções objetivo e verificação de restrições.
    """
    
    def __init__(self, monitoramento):
        """
        Inicializa as funções objetivo.
        
        Args:
            monitoramento: Instância da classe principal
        """
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
    
    def calcular_f1(self, x_ij: np.ndarray) -> float:
        """Calcula f1: Minimização da distância total."""
        return np.sum(self.distancias * x_ij)
    
    def calcular_f2(self, h_ik: np.ndarray, y_jk: np.ndarray = None) -> float:
        """
        Calcula f2: Minimização da diferença entre equipes.
        
        Conforme especificação do enunciado:
        f2 = max_k(Σ_i h_ik) - min_k(Σ_i h_ik)
        """
        ativos_por_equipe = np.sum(h_ik, axis=0)
        # Remove equipes vazias (sem ativos)
        equipes_com_ativos = ativos_por_equipe[ativos_por_equipe > 0]
        
        if len(equipes_com_ativos) == 0:
            return 0.0
        
        # Calcula diferença entre equipe com mais ativos e equipe com menos ativos
        diferenca = np.max(equipes_com_ativos) - np.min(equipes_com_ativos)
        return float(diferenca)
    
    def verificar_restricoes(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> bool:
        """Verifica se a solução atende todas as restrições."""
        # Restrição 1: Cada equipe em exatamente uma base
        for k in range(self.s_equipes):
            if np.sum(y_jk[:, k]) > 1:
                return False
        
        # Restrição 2: Cada ativo em exatamente uma base
        for i in range(self.n_ativos):
            if np.sum(x_ij[i, :]) != 1:
                return False
        
        # Restrição 3: Ativo só pode ser atribuído a base com equipe
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0]
            if len(base_ativo) > 0:
                base_id = base_ativo[0]
                if np.sum(y_jk[base_id, :]) == 0:
                    return False
        
        # Restrição 4: Cada ativo em exatamente uma equipe
        for i in range(self.n_ativos):
            if np.sum(h_ik[i, :]) != 1:
                return False
        
        # Restrição 5: Ativo só pode ser atribuído a equipe da sua base
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0]
            if len(base_ativo) > 0:
                base_id = base_ativo[0]
                equipes_base = np.where(y_jk[base_id, :] == 1)[0]
                equipe_ativo = np.where(h_ik[i, :] == 1)[0]
                if len(equipe_ativo) > 0 and equipe_ativo[0] not in equipes_base:
                    return False
        
        # Restrição 6: Equilíbrio mínimo de ativos por equipe
        # Cada equipe deve ter pelo menos η·n/s ativos
        for k in range(self.s_equipes):
            if np.sum(y_jk[:, k]) > 0:  # Se a equipe k está alocada
                ativos_equipe = np.sum(h_ik[:, k])
                if ativos_equipe < self.eta * self.n_ativos / self.s_equipes:
                    return False
        
        return True

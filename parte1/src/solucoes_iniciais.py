import numpy as np
from typing import List, Tuple

class GeradorSolucoes:
    # Classe que gera soluções iniciais para o problema usando heurísticas
    
    def __init__(self, monitoramento):
        # Pega os dados do problema da classe principal
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
    
    def gerar_solucao_inicial(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Heurística construtiva para gerar solução inicial com randomização.
        
        Returns:
            x_ij: Atribuição de ativos às bases
            y_jk: Alocação de equipes às bases  
            h_ik: Atribuição de ativos às equipes
        """
        # Inicializa variáveis
        x_ij = np.zeros((self.n_ativos, self.m_bases), dtype=int)
        y_jk = np.zeros((self.m_bases, self.s_equipes), dtype=int)
        h_ik = np.zeros((self.n_ativos, self.s_equipes), dtype=int)
        
        # Passo 1: Aloca TODAS as equipes as bases para minimizar f1
        # Distribui equipes entre as bases mais centrais
        bases_ordenadas = self._ordenar_bases_por_centralidade()
        
        # Usa TODAS as 8 equipes para melhorar f1 (menor distancia)
        for k in range(self.s_equipes):
            # Distribui equipes entre as bases mais centrais
            # Permite multiplas equipes na mesma base se necessario
            if np.random.random() < 0.5:  # 50% nas bases mais centrais
                base_escolhida = bases_ordenadas[k % min(4, len(bases_ordenadas))]
            else:  # 50% distribuidas
                base_escolhida = bases_ordenadas[k % len(bases_ordenadas)]
            y_jk[base_escolhida, k] = 1
        
        # Passo 2: Atribui ativos as bases MAIS PROXIMAS (para minimizar f1)
        for i in range(self.n_ativos):
            # Encontra bases com equipes
            bases_com_equipes = np.where(np.sum(y_jk, axis=1) > 0)[0]
            
            if len(bases_com_equipes) > 0:
                # SEMPRE escolhe a base mais proxima para minimizar f1
                distancias_validas = self.distancias[i, bases_com_equipes]
                base_mais_proxima = bases_com_equipes[np.argmin(distancias_validas)]
                x_ij[i, base_mais_proxima] = 1
        
        # Passo 3: Atribui ativos às equipes (com balanceamento melhorado)
        h_ik = self._balancear_atribuicao_equipes(x_ij, y_jk)
        
        return x_ij, y_jk, h_ik
    
    def _ordenar_bases_por_centralidade(self) -> List[int]:
        """Ordena bases por centralidade (menor distância média aos ativos)."""
        distancias_medias = []
        for j in range(self.m_bases):
            dist_media = np.mean(self.distancias[:, j])
            distancias_medias.append((j, dist_media))
        
        distancias_medias.sort(key=lambda x: x[1])
        return [base_id for base_id, _ in distancias_medias]
    
    def _balancear_atribuicao_equipes(self, x_ij: np.ndarray, y_jk: np.ndarray) -> np.ndarray:
        """Balanceia atribuição de ativos às equipes."""
        h_ik = np.zeros((self.n_ativos, self.s_equipes), dtype=int)
        
        # Para cada ativo, encontra a equipe da base onde está alocado
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0]
            if len(base_ativo) > 0:
                base_id = base_ativo[0]
                equipes_base = np.where(y_jk[base_id, :] == 1)[0]
                if len(equipes_base) > 0:
                    # Escolhe a equipe com menos ativos
                    ativos_por_equipe = np.sum(h_ik, axis=0)
                    equipe_escolhida = equipes_base[np.argmin(ativos_por_equipe[equipes_base])]
                    h_ik[i, equipe_escolhida] = 1
        
        return h_ik
    
    def _balancear_atribuicao_equipes_melhorado(self, x_ij: np.ndarray, y_jk: np.ndarray) -> np.ndarray:
        """Balanceia atribuição de ativos às equipes com melhor distribuição."""
        h_ik = np.zeros((self.n_ativos, self.s_equipes), dtype=int)
        
        # Coleta todos os ativos por base
        ativos_por_base = {}
        for i in range(self.n_ativos):
            base_ativo = np.where(x_ij[i, :] == 1)[0]
            if len(base_ativo) > 0:
                base_id = base_ativo[0]
                if base_id not in ativos_por_base:
                    ativos_por_base[base_id] = []
                ativos_por_base[base_id].append(i)
        
        # Distribui ativos entre equipes de cada base
        for base_id, ativos in ativos_por_base.items():
            equipes_base = np.where(y_jk[base_id, :] == 1)[0]
            
            if len(equipes_base) > 0:
                # Distribui ativos de forma mais balanceada
                ativos_por_equipe = len(ativos) // len(equipes_base)
                resto = len(ativos) % len(equipes_base)
                
                ativo_idx = 0
                for k_idx, k in enumerate(equipes_base):
                    # Calcula quantos ativos esta equipe deve receber
                    n_ativos_equipe = ativos_por_equipe + (1 if k_idx < resto else 0)
                    
                    # Atribui ativos à equipe
                    for _ in range(n_ativos_equipe):
                        if ativo_idx < len(ativos):
                            h_ik[ativos[ativo_idx], k] = 1
                            ativo_idx += 1
        
        return h_ik

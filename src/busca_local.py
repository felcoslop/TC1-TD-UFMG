"""
Módulo de estruturas de vizinhança e busca local
para o problema de monitoramento de ativos.
"""

import numpy as np
from typing import List, Tuple

class BuscaLocal:
    """
    Classe responsável pelas estruturas de vizinhança e busca local.
    """
    
    def __init__(self, monitoramento):
        """
        Inicializa a busca local.
        
        Args:
            monitoramento: Instância da classe principal
        """
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
        self.funcoes_objetivo = monitoramento.funcoes_objetivo
    
    def vizinhanca_1_troca_ativo_base(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> List[Tuple]:
        """Vizinhança 1: Troca ativo de base."""
        vizinhos = []
        
        for i in range(self.n_ativos):
            base_atual = np.where(x_ij[i, :] == 1)[0][0]
            
            # Tenta mover para outras bases com equipes
            for j in range(self.m_bases):
                if j != base_atual and np.sum(y_jk[j, :]) > 0:
                    x_novo = x_ij.copy()
                    x_novo[i, base_atual] = 0
                    x_novo[i, j] = 1
                    
                    # Atualiza h_ik correspondente
                    h_novo = h_ik.copy()
                    equipe_antiga = np.where(h_ik[i, :] == 1)[0][0]
                    h_novo[i, equipe_antiga] = 0
                    
                    # Encontra equipe da nova base
                    equipes_nova_base = np.where(y_jk[j, :] == 1)[0]
                    if len(equipes_nova_base) > 0:
                        h_novo[i, equipes_nova_base[0]] = 1
                        vizinhos.append((x_novo, y_jk, h_novo))
        
        return vizinhos
    
    def vizinhanca_2_troca_equipe_base(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> List[Tuple]:
        """Vizinhança 2: Troca equipe de base."""
        vizinhos = []
        
        for k in range(self.s_equipes):
            base_atual = np.where(y_jk[:, k] == 1)[0]
            if len(base_atual) > 0:
                base_atual = base_atual[0]
                
                # Tenta mover para outras bases
                for j in range(self.m_bases):
                    if j != base_atual and np.sum(y_jk[j, :]) == 0:
                        y_novo = y_jk.copy()
                        y_novo[base_atual, k] = 0
                        y_novo[j, k] = 1
                        
                        # Atualiza h_ik para manter consistência
                        h_novo = h_ik.copy()
                        ativos_equipe = np.where(h_ik[:, k] == 1)[0]
                        
                        # Move ativos da equipe para a nova base
                        for i in ativos_equipe:
                            x_ij[i, base_atual] = 0
                            x_ij[i, j] = 1
                        
                        vizinhos.append((x_ij, y_novo, h_novo))
        
        return vizinhos
    
    def vizinhanca_3_troca_ativo_equipe(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> List[Tuple]:
        """Vizinhança 3: Troca ativo entre equipes da mesma base."""
        vizinhos = []
        
        for i in range(self.n_ativos):
            equipe_atual = np.where(h_ik[i, :] == 1)[0][0]
            base_ativo = np.where(x_ij[i, :] == 1)[0][0]
            
            # Encontra outras equipes na mesma base
            equipes_base = np.where(y_jk[base_ativo, :] == 1)[0]
            
            for k in equipes_base:
                if k != equipe_atual:
                    h_novo = h_ik.copy()
                    h_novo[i, equipe_atual] = 0
                    h_novo[i, k] = 1
                    vizinhos.append((x_ij, y_jk, h_novo))
        
        return vizinhos
    
    def busca_local(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, 
                    funcao_objetivo: str = 'f1') -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Busca local para refinamento da solução."""
        melhor_solucao = (x_ij.copy(), y_jk.copy(), h_ik.copy())
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        melhorou = True
        while melhorou:
            melhorou = False
            
            # Testa todas as vizinhanças
            vizinhancas = [
                self.vizinhanca_1_troca_ativo_base(x_ij, y_jk, h_ik),
                self.vizinhanca_2_troca_equipe_base(x_ij, y_jk, h_ik),
                self.vizinhanca_3_troca_ativo_equipe(x_ij, y_jk, h_ik)
            ]
            
            for vizinhos in vizinhancas:
                for x_viz, y_viz, h_viz in vizinhos:
                    if self.funcoes_objetivo.verificar_restricoes(x_viz, y_viz, h_viz):
                        if funcao_objetivo == 'f1':
                            valor_viz = self.funcoes_objetivo.calcular_f1(x_viz)
                        else:
                            valor_viz = self.funcoes_objetivo.calcular_f2(h_viz, y_jk)
                        
                        if valor_viz < melhor_valor:
                            melhor_solucao = (x_viz.copy(), y_viz.copy(), h_viz.copy())
                            melhor_valor = valor_viz
                            x_ij, y_jk, h_ik = x_viz, y_viz, h_viz
                            melhorou = True
                            break
                if melhorou:
                    break
        
        return melhor_solucao[0], melhor_solucao[1], melhor_solucao[2], melhor_valor
    
    def shake(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Operador de perturbação para VNS."""
        x_shake = x_ij.copy()
        y_shake = y_jk.copy()
        h_shake = h_ik.copy()
        
        # Perturbação: move alguns ativos aleatoriamente
        n_perturbacoes = min(10, self.n_ativos // 10)
        ativos_perturbar = np.random.choice(self.n_ativos, n_perturbacoes, replace=False)
        
        for i in ativos_perturbar:
            # Remove da base atual
            base_atual = np.where(x_shake[i, :] == 1)[0][0]
            x_shake[i, base_atual] = 0
            
            # Escolhe nova base aleatoriamente (com equipe)
            bases_validas = np.where(np.sum(y_shake, axis=1) > 0)[0]
            if len(bases_validas) > 0:
                nova_base = np.random.choice(bases_validas)
                x_shake[i, nova_base] = 1
                
                # Atualiza h_ik
                equipe_antiga = np.where(h_shake[i, :] == 1)[0][0]
                h_shake[i, equipe_antiga] = 0
                
                equipes_nova_base = np.where(y_shake[nova_base, :] == 1)[0]
                if len(equipes_nova_base) > 0:
                    h_shake[i, equipes_nova_base[0]] = 1
        
        return x_shake, y_shake, h_shake
    
    def shake_simples(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Shake melhorado - move mais ativos e adiciona diversificação."""
        x_shake = x_ij.copy()
        y_shake = y_jk.copy()
        h_shake = h_ik.copy()
        
        # Move mais ativos para maior diversificação
        n_perturbacoes = min(20, self.n_ativos // 10)  # Aumentado de 5 para 20
        ativos_perturbar = np.random.choice(self.n_ativos, n_perturbacoes, replace=False)
        
        for i in ativos_perturbar:
            # Remove da base atual
            base_atual = np.where(x_shake[i, :] == 1)[0][0]
            x_shake[i, base_atual] = 0
            
            # Escolhe nova base aleatoriamente (com equipe)
            bases_validas = np.where(np.sum(y_shake, axis=1) > 0)[0]
            if len(bases_validas) > 0:
                nova_base = np.random.choice(bases_validas)
                x_shake[i, nova_base] = 1
                
                # Atualiza h_ik
                equipe_antiga = np.where(h_shake[i, :] == 1)[0][0]
                h_shake[i, equipe_antiga] = 0
                
                equipes_nova_base = np.where(y_shake[nova_base, :] == 1)[0]
                if len(equipes_nova_base) > 0:
                    h_shake[i, equipes_nova_base[0]] = 1
        
        # Adiciona perturbação nas equipes (troca ativos entre equipes da mesma base)
        for _ in range(min(10, self.n_ativos // 20)):
            # Escolhe uma base aleatória com múltiplas equipes
            bases_com_multiplas_equipes = []
            for j in range(self.m_bases):
                equipes_base = np.where(y_shake[j, :] == 1)[0]
                if len(equipes_base) > 1:
                    bases_com_multiplas_equipes.append(j)
            
            if bases_com_multiplas_equipes:
                base_escolhida = np.random.choice(bases_com_multiplas_equipes)
                equipes_base = np.where(y_shake[base_escolhida, :] == 1)[0]
                
                # Escolhe dois ativos aleatórios da base
                ativos_base = np.where(x_shake[:, base_escolhida] == 1)[0]
                if len(ativos_base) >= 2:
                    ativos_trocar = np.random.choice(ativos_base, 2, replace=False)
                    
                    # Troca as equipes dos ativos
                    equipe1 = np.where(h_shake[ativos_trocar[0], :] == 1)[0][0]
                    equipe2 = np.where(h_shake[ativos_trocar[1], :] == 1)[0][0]
                    
                    if equipe1 != equipe2:
                        h_shake[ativos_trocar[0], equipe1] = 0
                        h_shake[ativos_trocar[0], equipe2] = 1
                        h_shake[ativos_trocar[1], equipe2] = 0
                        h_shake[ativos_trocar[1], equipe1] = 1
        
        return x_shake, y_shake, h_shake
    
    def shake_adaptativo(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, 
                         intensidade: float = 0.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Shake adaptativo com intensidade variável."""
        x_shake = x_ij.copy()
        y_shake = y_jk.copy()
        h_shake = h_ik.copy()
        
        # Calcula número de perturbações baseado na intensidade (mais balanceado)
        if intensidade >= 0.8:  # Para alta intensidade
            n_perturbacoes = max(30, int(self.n_ativos * intensidade * 0.3))  # Mais agressivo
            n_perturbacoes = min(n_perturbacoes, 60)  # Máximo de 60 perturbações
        elif intensidade > 0.5:  # Para média intensidade
            n_perturbacoes = max(15, int(self.n_ativos * intensidade * 0.2))  # Moderado
            n_perturbacoes = min(n_perturbacoes, 40)  # Máximo de 40 perturbações
        else:
            n_perturbacoes = max(5, int(self.n_ativos * intensidade * 0.1))  # Conservador
            n_perturbacoes = min(n_perturbacoes, 20)  # Máximo de 20 perturbações
        
        ativos_perturbar = np.random.choice(self.n_ativos, n_perturbacoes, replace=False)
        
        for i in ativos_perturbar:
            # Remove da base atual
            base_atual = np.where(x_shake[i, :] == 1)[0][0]
            x_shake[i, base_atual] = 0
            h_shake[i, :] = 0  # Remove atribuição de equipe
            
            # Escolhe nova base baseada na distância (só bases próximas)
            bases_validas = np.where(np.sum(y_shake, axis=1) > 0)[0]
            bases_validas = bases_validas[bases_validas != base_atual]
            
            if len(bases_validas) > 0:
                # Pega apenas as 3 bases mais próximas
                distancias_validas = self.distancias[i, bases_validas]
                indices_ordenados = np.argsort(distancias_validas)
                bases_proximas = bases_validas[indices_ordenados[:min(3, len(bases_validas))]]
                
                nova_base = np.random.choice(bases_proximas)
                x_shake[i, nova_base] = 1
                
                # Atribui a uma equipe da nova base
                equipes_na_nova_base = np.where(y_shake[nova_base, :] == 1)[0]
                if len(equipes_na_nova_base) > 0:
                    h_shake[i, equipes_na_nova_base[0]] = 1
        
        # Perturbação mais agressiva: move equipes para bases vazias (só para F2)
        if intensidade > 0.7 and np.random.random() < 0.5:  # Mais frequente
            equipes_ativas = np.where(np.sum(y_shake, axis=0) > 0)[0]
            bases_vazias = np.where(np.sum(y_shake, axis=1) == 0)[0]
            
            if len(equipes_ativas) > 0 and len(bases_vazias) > 0:
                equipe_escolhida = np.random.choice(equipes_ativas)
                base_atual = np.where(y_shake[:, equipe_escolhida] == 1)[0][0]
                nova_base = np.random.choice(bases_vazias)
                
                # Move a equipe
                y_shake[base_atual, equipe_escolhida] = 0
                y_shake[nova_base, equipe_escolhida] = 1
                
                # Move todos os ativos da equipe para a nova base
                ativos_equipe = np.where(h_shake[:, equipe_escolhida] == 1)[0]
                for ativo in ativos_equipe:
                    x_shake[ativo, base_atual] = 0
                    x_shake[ativo, nova_base] = 1
        
        return x_shake, y_shake, h_shake
    
    def busca_local_simples(self, x_ij: np.ndarray, y_jk: np.ndarray, h_ik: np.ndarray, 
                            funcao_objetivo: str = 'f1') -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Busca local melhorada - testa mais trocas e inclui trocas de equipes."""
        melhor_solucao = (x_ij.copy(), y_jk.copy(), h_ik.copy())
        
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        # Testa trocas de ativos de forma mais eficiente
        n_testes = min(30, self.n_ativos // 10)  # Mais conservador
        ativos_teste = np.random.choice(self.n_ativos, n_testes, replace=False)
        
        for i in ativos_teste:
            base_atual = np.where(x_ij[i, :] == 1)[0][0]
            
            # Testa apenas as 3 bases mais próximas
            bases_validas = np.where(np.sum(y_jk, axis=1) > 0)[0]
            bases_proximas = bases_validas[np.argsort(self.distancias[i, bases_validas])[:min(3, len(bases_validas))]]
            
            for j in bases_proximas:
                if j != base_atual:
                    x_teste = x_ij.copy()
                    x_teste[i, base_atual] = 0
                    x_teste[i, j] = 1
                    
                    h_teste = h_ik.copy()
                    equipe_antiga = np.where(h_ik[i, :] == 1)[0][0]
                    h_teste[i, equipe_antiga] = 0
                    
                    equipes_nova_base = np.where(y_jk[j, :] == 1)[0]
                    if len(equipes_nova_base) > 0:
                        h_teste[i, equipes_nova_base[0]] = 1
                        
                        if self.funcoes_objetivo.verificar_restricoes(x_teste, y_jk, h_teste):
                            if funcao_objetivo == 'f1':
                                valor_teste = self.funcoes_objetivo.calcular_f1(x_teste)
                            else:
                                valor_teste = self.funcoes_objetivo.calcular_f2(h_teste, y_jk)
                            
                            if valor_teste < melhor_valor:
                                melhor_solucao = (x_teste.copy(), y_jk.copy(), h_teste.copy())
                                melhor_valor = valor_teste
                                x_ij, y_jk, h_ik = x_teste, y_jk, h_teste
                                return x_ij, y_jk, h_ik, melhor_valor  # Retorna imediatamente quando encontra melhoria
        
        # Adiciona busca local para trocas de equipes (importante para f2)
        if funcao_objetivo == 'f2':
            for _ in range(10):  # Testa algumas trocas de equipes
                # Escolhe uma base com múltiplas equipes
                bases_com_multiplas_equipes = []
                for j in range(self.m_bases):
                    equipes_base = np.where(y_jk[j, :] == 1)[0]
                    if len(equipes_base) > 1:
                        bases_com_multiplas_equipes.append(j)
                
                if bases_com_multiplas_equipes:
                    base_escolhida = np.random.choice(bases_com_multiplas_equipes)
                    equipes_base = np.where(y_jk[base_escolhida, :] == 1)[0]
                    
                    # Escolhe dois ativos aleatórios da base
                    ativos_base = np.where(x_ij[:, base_escolhida] == 1)[0]
                    if len(ativos_base) >= 2:
                        ativos_trocar = np.random.choice(ativos_base, 2, replace=False)
                        
                        h_teste = h_ik.copy()
                        equipe1 = np.where(h_ik[ativos_trocar[0], :] == 1)[0][0]
                        equipe2 = np.where(h_ik[ativos_trocar[1], :] == 1)[0][0]
                        
                        if equipe1 != equipe2:
                            h_teste[ativos_trocar[0], equipe1] = 0
                            h_teste[ativos_trocar[0], equipe2] = 1
                            h_teste[ativos_trocar[1], equipe2] = 0
                            h_teste[ativos_trocar[1], equipe1] = 1
                            
                            if self.funcoes_objetivo.verificar_restricoes(x_ij, y_jk, h_teste):
                                valor_teste = self.funcoes_objetivo.calcular_f2(h_teste, y_jk)
                                
                                if valor_teste < melhor_valor:
                                    melhor_solucao = (x_ij.copy(), y_jk.copy(), h_teste.copy())
                                    melhor_valor = valor_teste
                                    h_ik = h_teste
                                    break
        
        return melhor_solucao[0], melhor_solucao[1], melhor_solucao[2], melhor_valor

"""
Módulo de algoritmos VNS e otimização
para o problema de monitoramento de ativos.
"""

import numpy as np
from typing import Dict, Tuple

class AlgoritmoVNS:
    """
    Classe responsável pelos algoritmos VNS e otimização.
    """
    
    def __init__(self, monitoramento):
        """
        Inicializa o algoritmo VNS.
        
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
        self.busca_local = monitoramento.busca_local
        self.gerador_solucoes = monitoramento.gerador_solucoes
    
    def vns(self, funcao_objetivo: str = 'f1', max_iter: int = 500) -> Dict:
        """
        Algoritmo VNS (Variable Neighborhood Search) melhorado.
        
        Args:
            funcao_objetivo: 'f1' ou 'f2'
            max_iter: Número máximo de iterações
            
        Returns:
            Dicionário com resultados
        """
        print(f"  Iniciando VNS para {funcao_objetivo}...")
        
        # Define seed aleatória para diversificação
        np.random.seed(None)
        
        # Solução inicial
        x_ij, y_jk, h_ik = self.gerador_solucoes.gerar_solucao_inicial()
        
        # Calcula valor inicial sem busca local
        if funcao_objetivo == 'f1':
            melhor_valor = self.funcoes_objetivo.calcular_f1(x_ij)
        else:
            melhor_valor = self.funcoes_objetivo.calcular_f2(h_ik, y_jk)
        
        print(f"    Valor inicial: {melhor_valor:.2f}")
        
        # PULA busca local inicial para permitir mais diversificação
        # if funcao_objetivo == 'f2':
        #     x_ij, y_jk, h_ik, melhor_valor = self.busca_local.busca_local_simples(x_ij, y_jk, h_ik, funcao_objetivo)
        # else:
        #     x_ij, y_jk, h_ik, melhor_valor = self.busca_local.busca_local_simples(x_ij, y_jk, h_ik, funcao_objetivo)
        print(f"    Valor inicial mantido: {melhor_valor:.2f}")
        
        historico = [melhor_valor]
        iteracoes_sem_melhoria = 0
        
        for iteracao in range(max_iter):
            if iteracao % 10 == 0:  # Mostra a cada 10 iterações
                print(f"    Iteração {iteracao}/{max_iter} - Valor atual: {melhor_valor:.2f}")
            
            # Shake mais diversificado para ambas as funções
            if funcao_objetivo == 'f2':
                # Para F2, usa shake adaptativo mais agressivo
                intensidade_shake = min(1.0, 0.6 + (iteracoes_sem_melhoria * 0.1))  # Mais agressivo para F2
                x_shake, y_shake, h_shake = self.busca_local.shake_adaptativo(x_ij, y_jk, h_ik, intensidade_shake)
            else:
                intensidade_shake = min(1.0, 0.8 + (iteracoes_sem_melhoria * 0.05))  # Mais agressivo para F1 também
                x_shake, y_shake, h_shake = self.busca_local.shake_adaptativo(x_ij, y_jk, h_ik, intensidade_shake)
            
            # Calcula valor após shake (antes da busca local)
            if funcao_objetivo == 'f1':
                valor_shake = self.funcoes_objetivo.calcular_f1(x_shake)
            else:
                valor_shake = self.funcoes_objetivo.calcular_f2(h_shake, y_jk)
            
            # Debug: verifica se o shake realmente mudou algo
            if iteracao < 5:
                mudancas = np.sum(x_ij != x_shake)
                print(f"      Debug - Mudanças no shake: {mudancas} ativos movidos")
            
            # Busca local menos agressiva para F2 para permitir diversificação
            if funcao_objetivo == 'f2':
                # Para F2, usa busca local simples para permitir mais diversificação
                x_viz, y_viz, h_viz, valor_viz = self.busca_local.busca_local_simples(x_shake, y_shake, h_shake, funcao_objetivo)
            else:
                x_viz, y_viz, h_viz, valor_viz = self.busca_local.busca_local_simples(x_shake, y_shake, h_shake, funcao_objetivo)
            
            # Debug: mostra valores para entender o que está acontecendo
            if iteracao < 5:  # Só nas primeiras 5 iterações
                print(f"      Debug - Valor shake: {valor_shake:.2f}, Após busca local: {valor_viz:.2f}, Melhor: {melhor_valor:.2f}")
            
            # Aceita se melhor
            if valor_viz < melhor_valor:
                x_ij, y_jk, h_ik = x_viz, y_viz, h_viz
                melhor_valor = valor_viz
                iteracoes_sem_melhoria = 0
                print(f"    ✓ Melhoria encontrada: {valor_viz:.2f}")
            else:
                iteracoes_sem_melhoria += 1
            
            historico.append(melhor_valor)
            
            # Sem parada precoce - roda todas as iterações para busca exaustiva
            # if iteracoes_sem_melhoria > 150 and iteracao > 300:
            #     print(f"    Parada precoce - sem melhoria há {iteracoes_sem_melhoria} iterações")
            #     break
        
        print(f"  VNS concluído - Melhor valor: {melhor_valor:.2f}")
        return {
            'x_ij': x_ij,
            'y_jk': y_jk,
            'h_ik': h_ik,
            'valor_objetivo': melhor_valor,
            'historico': historico,
            'funcao_objetivo': funcao_objetivo
        }
    
    def otimizacao_mono_objetivo(self, n_execucoes: int = 5) -> Dict:
        """
        Executa otimização mono-objetivo para f1 e f2.
        
        Args:
            n_execucoes: Número de execuções para cada função
            
        Returns:
            Resultados das otimizações
        """
        resultados = {}
        
        for funcao in ['f1', 'f2']:
            print(f"\n{'='*50}")
            print(f"OTIMIZANDO {funcao.upper()}")
            print(f"{'='*50}")
            
            execucoes = []
            for execucao in range(n_execucoes):
                print(f"\nExecução {execucao + 1}/{n_execucoes} de {funcao.upper()}:")
                resultado = self.vns(funcao, max_iter=500)  # Aumentado para melhor diversificação
                execucoes.append(resultado)
                print(f"  Resultado: {resultado['valor_objetivo']:.2f}")
            
            # Estatísticas
            valores = [r['valor_objetivo'] for r in execucoes]
            resultados[funcao] = {
                'execucoes': execucoes,
                'min': np.min(valores),
                'max': np.max(valores),
                'std': np.std(valores),
                'media': np.mean(valores)
            }
            
            print(f"\nEstatísticas {funcao.upper()}:")
            print(f"  Mínimo: {resultados[funcao]['min']:.2f}")
            print(f"  Máximo: {resultados[funcao]['max']:.2f}")
            print(f"  Média: {resultados[funcao]['media']:.2f}")
            print(f"  Desvio: {resultados[funcao]['std']:.2f}")
        
        return resultados

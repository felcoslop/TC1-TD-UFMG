import numpy as np
from typing import Dict, Tuple

class AlgoritmoVNS:
    # Classe que implementa o algoritmo VNS (Variable Neighborhood Search) para otimização
    
    def __init__(self, monitoramento):
        # Pega os dados do problema e as classes necessárias
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
        self.distancias = monitoramento.distancias
        self.funcoes_objetivo = monitoramento.funcoes_objetivo
        self.busca_local = monitoramento.busca_local
        self.gerador_solucoes = monitoramento.gerador_solucoes
    
    def vns(self, funcao_objetivo: str = 'f1', max_iter: int = 1000, max_iter_sem_melhoria: int = 50) -> Dict:
        """
        GVNS (General Variable Neighborhood Search) - Algoritmo 6 dos slides.
        Usa VND para busca local e Tournament Selection para comparação.
        
        Args:
            funcao_objetivo: 'f1' ou 'f2'
            max_iter: Numero maximo de iteracoes
            max_iter_sem_melhoria: Criterio de parada inteligente (iteracoes sem melhoria)
            
        Returns:
            Dicionario com resultados
        """
        print(f"  Iniciando GVNS para {funcao_objetivo}...", flush=True)
        
        # Define seed aleatoria para diversificacao
        np.random.seed(None)
        
        # Solucao inicial
        x_ij, y_jk, h_ik = self.gerador_solucoes.gerar_solucao_inicial()
        
        # Aplica VND na solucao inicial
        print(f"    Aplicando VND inicial...", flush=True)
        x_ij, y_jk, h_ik, melhor_valor = self.busca_local.variable_neighborhood_descent(
            x_ij, y_jk, h_ik, funcao_objetivo, verbose=True)
        
        print(f"    Valor inicial (apos VND): {melhor_valor:.2f}", flush=True)
        
        historico = [melhor_valor]
        iteracoes_sem_melhoria = 0
        
        # k_max_shake: numero de estruturas de vizinhanca para shake
        k_max_shake = 3  # Diferentes intensidades de shake
        
        for iteracao in range(max_iter):
            # Mostra progresso
            if iteracao % 10 == 0 or iteracao < 5:
                print(f"    Iter {iteracao}/{max_iter} | Valor: {melhor_valor:.2f} | Sem melhoria: {iteracoes_sem_melhoria}", flush=True)
            
            # Loop k: itera pelas estruturas de shake
            k = 1
            verbose_vnd = (iteracao < 3)  # Mostra VND apenas nas primeiras 3 iterações
            
            while k <= k_max_shake:
                # x' = Shake(x, k) - intensidade aumenta com k
                intensidade_shake = 0.2 + (k / k_max_shake) * 0.6  # 0.2 a 0.8
                
                if verbose_vnd:
                    print(f"      Shake k={k}, intensidade={intensidade_shake:.2f}", flush=True)
                
                x_shake, y_shake, h_shake = self.busca_local.shake_adaptativo(
                    x_ij, y_jk, h_ik, intensidade_shake)
                
                # x'' = VND(x') - busca local usando VND
                x_viz, y_viz, h_viz, valor_viz = self.busca_local.variable_neighborhood_descent(
                    x_shake, y_shake, h_shake, funcao_objetivo, verbose=verbose_vnd)
                
                # NeighborhoodChange: usa Tournament Selection para comparar
                sol_atual = (x_ij, y_jk, h_ik)
                sol_viz = (x_viz, y_viz, h_viz)
                sol_escolhida, aceita = self.busca_local.tournament_selection(
                    sol_atual, sol_viz, funcao_objetivo)
                
                if aceita:
                    # Aceita nova solucao e reinicia k
                    x_ij, y_jk, h_ik = sol_escolhida
                    melhor_valor = valor_viz
                    k = 1  # Reinicia
                    iteracoes_sem_melhoria = 0
                    print(f"    >>> Melhoria! Novo valor: {valor_viz:.2f}", flush=True)
                else:
                    # Incrementa k para proxima vizinhanca
                    k += 1
            
            # Registra iteracao sem melhoria global (após loop k completo)
            if k > k_max_shake:
                iteracoes_sem_melhoria += 1
            
            historico.append(melhor_valor)
            
            # Criterio de parada inteligente: para cedo se muitas iteracoes sem melhoria
            if iteracoes_sem_melhoria >= max_iter_sem_melhoria:
                print(f"    Parada antecipada: {iteracoes_sem_melhoria} iteracoes sem melhoria", flush=True)
                break
        
        print(f"  GVNS concluido - Melhor valor: {melhor_valor:.2f}", flush=True)
        
        # Verifica quantas equipes estao sendo usadas
        equipes_usadas = np.sum(np.sum(h_ik, axis=0) > 0)
        print(f"  Equipes utilizadas: {equipes_usadas}/{self.s_equipes}", flush=True)
        
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
                resultado = self.vns(funcao, max_iter=500, max_iter_sem_melhoria=5)
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

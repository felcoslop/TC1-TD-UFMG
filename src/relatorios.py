import numpy as np
from typing import Dict

class GeradorRelatorios:
    # Classe que gera relatórios detalhados dos resultados da otimização
    
    def __init__(self, monitoramento):
        # Pega os dados do problema da classe principal
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
    
    def gerar_relatorio_mono_objetivo(self, resultados: Dict) -> str:
        # Gera relatório completo com todas as informações para o LaTeX
        
        # Calcula estatísticas detalhadas
        f1_valores = [r['valor_objetivo'] for r in resultados['f1']['execucoes']]
        f2_valores = [r['valor_objetivo'] for r in resultados['f2']['execucoes']]
        
        # Encontra as melhores soluções
        melhor_f1 = min(resultados['f1']['execucoes'], key=lambda x: x['valor_objetivo'])
        melhor_f2 = min(resultados['f2']['execucoes'], key=lambda x: x['valor_objetivo'])
        
        # Analisa distribuição de ativos por equipe na melhor solução f2
        ativos_por_equipe_f2 = np.sum(melhor_f2['h_ik'], axis=0)
        equipes_utilizadas_f2 = np.sum(ativos_por_equipe_f2 > 0)
        
        # Analisa bases utilizadas na melhor solução f1
        bases_utilizadas_f1 = np.sum(np.sum(melhor_f1['y_jk'], axis=1) > 0)
        bases_utilizadas_f2 = np.sum(np.sum(melhor_f2['y_jk'], axis=1) > 0)
        
        relatorio = f"""
========================================
ENTREGA #1: MODELAGEM E OTIMIZAÇÃO MONO-OBJETIVO
========================================

i. FORMULAÇÃO MATEMÁTICA:

(a) Parâmetros do problema:
- n = {self.n_ativos} (número de ativos)
- m = {self.m_bases} (número de bases disponíveis)
- s = {self.s_equipes} (número máximo de equipes)
- η = {self.eta} (percentual mínimo de ativos por equipe)
- d_ij = distância entre ativo i e base j (calculada a partir das coordenadas)

(b) Variáveis de decisão:
- x_ij ∈ {{0,1}}: 1 se ativo i for atribuído à base j, 0 caso contrário
- y_jk ∈ {{0,1}}: 1 se base j for ocupada pela equipe k, 0 caso contrário
- h_ik ∈ {{0,1}}: 1 se ativo i for mantido pela equipe k, 0 caso contrário

(c) Função objetivo f1:
f1 = Σᵢ₌₁ⁿ Σⱼ₌₁ᵐ d_ij x_ij
Objetivo: minimizar distância total entre ativos e suas respectivas bases

(d) Função objetivo f2:
f2 = S
Objetivo: minimizar número de equipes empregadas
Conflito: f1 e f2 são conflitantes - soluções que minimizam f1 tendem a maximizar f2

(e) Restrições:
1. Σⱼ₌₁ᵐ y_jk = 1, ∀k ∈ {{1, ..., s}} (cada equipe em exatamente uma base)
2. Σⱼ₌₁ᵐ x_ij = 1, ∀i ∈ {{1, ..., n}} (cada ativo em exatamente uma base)
3. x_ij ≤ y_jk, ∀i ∈ {{1, ..., n}}, ∀j ∈ {{1, ..., m}}, ∀k ∈ {{1, ..., s}} (ativo só em base com equipe)
4. Σₖ₌₁ˢ h_ik = 1, ∀i ∈ {{1, ..., n}} (cada ativo em exatamente uma equipe)
5. h_ik ≤ (x_ij + y_jk)/2, ∀i ∈ {{1, ..., n}}, ∀j ∈ {{1, ..., m}}, ∀k ∈ {{1, ..., s}} (ativo só em equipe da sua base)
6. Σᵢ₌₁ⁿ h_ik ≥ η · n/s, ∀k ∈ {{1, ..., s}} (equilíbrio mínimo de ativos por equipe)

ii. ALGORITMO DE SOLUÇÃO:

(a) Metaheurística: VNS (Variable Neighborhood Search)
- Explora diferentes estruturas de vizinhança
- Combina busca local com perturbações (shake)
- Adapta intensidade de perturbação baseada no progresso

(b) Modelagem computacional:
- x_ij: array numpy (n_ativos × m_bases) com valores 0 ou 1
- y_jk: array numpy (m_bases × s_equipes) com valores 0 ou 1
- h_ik: array numpy (n_ativos × s_equipes) com valores 0 ou 1

(c) Estruturas de vizinhança:
1. Troca ativo de base: move ativo i da base atual para outra base com equipe
2. Troca equipe de base: move equipe k de uma base para outra base vazia
3. Troca ativo entre equipes: troca ativos entre equipes da mesma base

(d) Heurística construtiva:
1. Ordena bases por centralidade (menor distância média aos ativos)
2. Aloca equipes nas bases mais centrais
3. Atribui cada ativo à base mais próxima que tenha equipe
4. Distribui ativos entre equipes de forma balanceada

(e) Estratégia de refinamento:
- Busca local especializada para cada função objetivo
- Para f1: foca em reduzir distâncias
- Para f2: consolida equipes removendo as desnecessárias

iii. RESULTADOS DA OTIMIZAÇÃO MONO-OBJETIVO:

(a) Execuções realizadas: 5 execuções para cada função objetivo

(b) Estatísticas das 5 execuções:

Função f1 (Minimização da Distância Total):
- Mínimo: {resultados['f1']['min']:.2f} km
- Máximo: {resultados['f1']['max']:.2f} km
- Média: {resultados['f1']['media']:.2f} km
- Desvio Padrão: {resultados['f1']['std']:.2f} km

Função f2 (Minimização do Número de Equipes):
- Mínimo: {resultados['f2']['min']:.0f} equipes
- Máximo: {resultados['f2']['max']:.0f} equipes
- Média: {resultados['f2']['media']:.2f} equipes
- Desvio Padrão: {resultados['f2']['std']:.2f} equipes

(c) Curvas de convergência:
- Arquivo: resultados/graficos/analise_convergencia_completa.png
- Mostra evolução de f1 e f2 ao longo das iterações para as 5 execuções

(d) Melhores soluções encontradas:

Melhor solução f1:
- Valor da função: {melhor_f1['valor_objetivo']:.2f} km
- Bases utilizadas: {bases_utilizadas_f1}
- Equipes utilizadas: {np.sum(np.sum(melhor_f1['h_ik'], axis=0) > 0)}
- Arquivo: resultados/graficos/melhor_solucao_f1.png

Melhor solução f2:
- Valor da função: {melhor_f2['valor_objetivo']:.0f} equipes
- Bases utilizadas: {bases_utilizadas_f2}
- Equipes utilizadas: {equipes_utilizadas_f2}
- Distribuição de ativos por equipe: {ativos_por_equipe_f2[ativos_por_equipe_f2 > 0]}
- Arquivo: resultados/graficos/melhor_solucao_f2.png

ANÁLISE DE CONFLITO:
- f1 mínimo = {resultados['f1']['min']:.2f} km (usa {bases_utilizadas_f1} bases)
- f2 mínimo = {resultados['f2']['min']:.0f} equipes (usa {bases_utilizadas_f2} bases)
- Confirma conflito: soluções que minimizam f1 usam mais bases/equipes
- Soluções que minimizam f2 concentram ativos em menos bases/equipes

========================================
        """
        
        return relatorio

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de relatórios e análise
para o problema de monitoramento de ativos.
"""

from typing import Dict

class GeradorRelatorios:
    """
    Classe responsável pela geração de relatórios e análise.
    """
    
    def __init__(self, monitoramento):
        """
        Inicializa o gerador de relatórios.
        
        Args:
            monitoramento: Instância da classe principal
        """
        self.monitoramento = monitoramento
        self.n_ativos = monitoramento.n_ativos
        self.m_bases = monitoramento.m_bases
        self.s_equipes = monitoramento.s_equipes
        self.eta = monitoramento.eta
    
    def gerar_relatorio_mono_objetivo(self, resultados: Dict) -> str:
        """Gera relatório da otimização mono-objetivo."""
        relatorio = f"""
        ========================================
        MODELAGEM E OTIMIZAÇÃO MONO-OBJETIVO
        ========================================
        
        PROBLEMA:
        - Ativos: {self.n_ativos}
        - Bases: {self.m_bases}
        - Equipes máximas: {self.s_equipes}
        - η (percentual mínimo): {self.eta}
        
        MODELAGEM MATEMÁTICA:
        
        Variáveis:
        - x_ij ∈ {{0,1}}: Ativo i atribuído à base j
        - y_jk ∈ {{0,1}}: Base j ocupada pela equipe k  
        - h_ik ∈ {{0,1}}: Ativo i mantido pela equipe k
        
        Funções Objetivo:
        - f1 = Σᵢ Σⱼ dᵢⱼ xᵢⱼ (minimizar distância total)
        - f2 = max_k(Σᵢ hᵢₖ) - min_k(Σᵢ hᵢₖ) (minimizar diferença entre equipes)
        
        Restrições:
        1. Σⱼ yⱼₖ = 1, ∀k (cada equipe em exatamente uma base)
        2. Σⱼ xᵢⱼ = 1, ∀i (cada ativo em exatamente uma base)
        3. xᵢⱼ ≤ yⱼₖ, ∀i,j,k (ativo só em base com equipe)
        4. Σₖ hᵢₖ = 1, ∀i (cada ativo em exatamente uma equipe)
        5. hᵢₖ ≤ (xᵢⱼ + yⱼₖ)/2, ∀i,j,k (ativo só em equipe da sua base)
        6. Σᵢ hᵢₖ ≥ η·n/s, ∀k (equilíbrio mínimo)
        
        ALGORITMO VNS:
        
        Estruturas de Vizinhança:
        1. Troca ativo de base
        2. Troca equipe de base  
        3. Troca ativo entre equipes da mesma base
        
        Heurística Construtiva:
        1. Aloca equipes às bases mais centrais
        2. Atribui ativos às bases mais próximas com equipes
        3. Balanceia atribuição de ativos às equipes
        
        RESULTADOS:
        
        Função f1 (Distância Total):
        - Mínimo: {resultados['f1']['min']:.2f}
        - Máximo: {resultados['f1']['max']:.2f}
        - Média: {resultados['f1']['media']:.2f}
        - Desvio Padrão: {resultados['f1']['std']:.2f}
        
        Função f2 (Diferença entre Equipes):
        - Mínimo: {resultados['f2']['min']:.2f}
        - Máximo: {resultados['f2']['max']:.2f}
        - Média: {resultados['f2']['media']:.2f}
        - Desvio Padrão: {resultados['f2']['std']:.2f}
        
        ========================================
        """
        
        return relatorio

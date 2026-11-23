# Sensibilidade aproximada (data = ano) excluindo 2020/2021; contagens (n, reconhecidas) da Tabela 6.
# Recuperado de outra conversa (claude.ai) desta mesma pesquisa. Versão exata, com datas, usa post.txt + org.py.
import numpy as np
from scipy.stats import mannwhitneyu
d={2014:(3,0),2015:(1,1),2016:(2,0),2017:(3,0),2018:(3,2),2019:(2,1),2020:(21,5),2021:(7,2),2022:(4,3),2023:(7,4),2024:(18,10),2025:(15,6),2026:(8,4)}
def run(ex=()):
    A=[];B=[]
    for y,(n,a) in d.items():
        if y in ex: continue
        A+= [y]*a; B+=[y]*(n-a)
    r=mannwhitneyu(A,B,alternative='greater')
    print(ex,len(A),len(B),round(r.statistic/(len(A)*len(B)),3),round(r.pvalue,3))
run(); run((2020,)); run((2020,2021))

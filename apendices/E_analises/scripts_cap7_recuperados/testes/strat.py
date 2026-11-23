"""RECONSTRUÇÃO de strat.py (o arquivo original não foi conservado).

Reproduz o código que consta da conversa "Hipóteses rivais para padrão confirmatório"
(claude.ai, 19/11/2026): estratos por remoção (V2), reclamante profissional (V4) e meio
digital (V5), verificação prévia sem o desfecho e Mann-Whitney estratificado exato, com
ponderação por pares e p por permutação dentro dos estratos.

Diferenças em relação ao original:
- o original lia o DataFrame `p` de /tmp/w/lag2.py, que não foi recuperado; aqui `p` é
  montado de post.txt, como em org.py;
- o original repetia o Passo 2 com a data de autuação (coluna `aut`, do Corte Aberta);
  essa parte foi omitida, porque as datas de autuação não estão depositadas;
- caminhos relativos no lugar de /tmp/w/.
Uso (de dentro desta pasta): python3 strat.py
"""
import pandas as pd, numpy as np
from scipy.stats import rankdata
p=pd.DataFrame([t.split() for t in open('post.txt').read().strip().split(';')],columns=['rcl','data','v13','org'])
p['rcl']=p.rcl.astype(int); p['dt']=pd.to_datetime(p.data,dayfirst=True); p['A']=(p.v13=='R').astype(int)
m2={};m4={}
for t in open('v24.txt').read().strip().split(';'):
    r,a,b=t.split(); m2[int(r)]=a.split(','); m4[int(r)]=b.split(',')
m5={int(t.split()[0]):t.split()[1].split(',') for t in open('v5.txt').read().strip().split(';')}
assert set(p.rcl)==set(m2)==set(m5)
p['REM']=p.rcl.map(lambda r:'remoção' if 'b' in m2[r] else 'sem remoção')
p['PROF']=p.rcl.map(lambda r:'ND' if m4[r]==['ND'] else ('profissional' if ({'a','b'}&set(m4[r])) else 'outro'))
p['DIG']=p.rcl.map(lambda r:'ND' if m5[r]==['ND'] else ('digital' if ({'c','d','e','f'}&set(m5[r])) else 'não digital'))
p['per']=np.where(p.dt.dt.year<=2021,'até 2021','2022-26')
# passo 1: sem desfecho
print('=== Passo 1 (sem desfecho) ===')
for v,lev in [('REM','remoção'),('PROF','profissional'),('DIG','digital')]:
    t=pd.crosstab(p[v],p.per)[['até 2021','2022-26']]
    x=p[p[v]==lev].dt.astype('int64'); y=p[(p[v]!=lev)&(p[v]!='ND')].dt.astype('int64')
    ps=np.mean([(a>b)+0.5*(a==b) for a in x for b in y])
    print(v); print(t); print(' PS datas (indicador=1 posterior):',round(ps,3),' |PS-0.5|=',round(abs(ps-0.5),3))
def ustats(df,col):
    r=rankdata(df[col].values.astype('int64')); x=(df.A==1).values; m=int(x.sum()); k=len(x)-m
    r2=(2*r).astype(int); W2=int(r2[x].sum())
    dp=[dict() for _ in range(m+1)]; dp[0][0]=1
    for v in r2:
        for j in range(m,0,-1):
            for s,c in dp[j-1].items(): dp[j][s+v]=dp[j].get(s+v,0)+c
    tot=sum(dp[m].values())
    # distribution of 2U = W2 - m(m+1)
    dist={s-m*(m+1):c/tot for s,c in dp[m].items()}
    return W2-m*(m+1), m*k, dist
def conv(a,b):
    out={}
    for x,px in a.items():
        for y,py in b.items(): out[x+y]=out.get(x+y,0)+px*py
    return out
def strat_test(df,keys,col='dt'):
    rows=[];D={0:1.0};U2=0;P=0
    for g,s in df.groupby(keys):
        u2,pairs,dist=ustats(s,col)
        rows.append((g,len(s),int(s.A.sum()),pairs,round(u2/2/pairs,3) if pairs else None))
        if pairs: D=conv(D,dist); U2+=u2; P+=pairs
    p_=sum(v for k,v in D.items() if k>=U2-1e-9)
    return round(U2/2/P,3),round(p_,4),P,rows
print('\n=== Passo 2 ===')
for col in ['dt']:
    print('\n### data:',col)
    for keys in ['REM','PROF','DIG',['REM','PROF'],['REM','DIG'],['PROF','DIG']]:
        ps,pv,P,rows=strat_test(p,keys,col)
        print(keys,'PS',ps,'p',pv,'pares',P,'efeito retido',round((ps-0.5)/(0.613-0.5),2))
        for r in rows: print('    ',r)

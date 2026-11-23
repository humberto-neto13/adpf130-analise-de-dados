import pandas as pd, numpy as np
from scipy.stats import rankdata
rows=[t.split() for t in open('post.txt').read().strip().split(';')]
p=pd.DataFrame(rows,columns=['rcl','data','v13','org']); p['dt']=pd.to_datetime(p.data,dayfirst=True); p['A']=(p.v13=='R').astype(int)
print(len(p),p.A.sum())
def ustats(df):
    r=rankdata(df.dt.values.astype('int64')); x=(df.A==1).values; m=int(x.sum()); k=len(x)-m
    r2=(2*r).astype(int); W2=int(r2[x].sum())
    dp=[dict() for _ in range(m+1)]; dp[0][0]=1
    for v in r2:
        for j in range(m,0,-1):
            for s,c in dp[j-1].items(): dp[j][s+v]=dp[j].get(s+v,0)+c
    tot=sum(dp[m].values()); return W2-m*(m+1),m*k,{s-m*(m+1):c/tot for s,c in dp[m].items()}
def conv(a,b):
    o={}
    for x,px in a.items():
        for y,py in b.items(): o[x+y]=o.get(x+y,0)+px*py
    return o
D={0:1.0};U=0;P=0
for g,s in p.groupby('org'):
    u2,pr,dist=ustats(s); pv=sum(v for k,v in dist.items() if k>=u2-1e-9) if pr else None
    print(g,len(s),s.A.sum(),pr,round(u2/2/pr,3) if pr else None, round(pv,4) if pv is not None else None)
    if pr: D=conv(D,dist);U+=u2;P+=pr
print('estrat',round(U/2/P,3),round(sum(v for k,v in D.items() if k>=U-1e-9),4),P)
p['per']=np.where(p.dt.dt.year<=2021,'ate2021','2022+')
print(pd.crosstab(p.org,p.per)); print(p.groupby(['org','per']).A.agg(['sum','size']))

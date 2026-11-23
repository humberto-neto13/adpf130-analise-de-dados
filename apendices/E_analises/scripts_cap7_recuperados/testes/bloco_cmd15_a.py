exec(open('./org.py').read().split("D={0:1.0}")[0].replace("print(len(p)","(len(p)"))
rel={int(t.split()[0]):t.split()[1] for t in open('./relp.txt').read().strip().split(';')}
p['rcl']=p.rcl.astype(int); p['rel']=p.rcl.map(rel)
venc={28747,29158,31130,43110,43220,52089,57785,58048,59482,63264,65017,66246,70705}
def run(extra,label):
    q=p.copy(); vs=venc|extra
    q['A']=np.where(q.rcl.isin(vs),1-q.A,q.A)
    D={0:1.0};U=0;P=0;rows=[]
    for g,s in q.groupby('rel'):
        u2,pr,dist=ustats(s)
        rows.append((g,len(s),int(s.A.sum()),pr,round(u2/2/pr,2) if pr else None))
        if pr: D=conv(D,dist);U+=u2;P+=pr
    pv=sum(v for k,v in D.items() if k>=U-1e-9)
    print(label,'PS',round(U/2/P,3),'p',round(pv,4),'pares',P)
    o=pd.DataFrame(rows,columns=['rel','n','voto_ader','pares','PS']).sort_values('pares',ascending=False); print(o.to_string(index=False))
    q2=q[q.dt.dt.year!=2020]; D={0:1.0};U=0;P=0
    for g,s in q2.groupby('rel'):
        u2,pr,dist=ustats(s)
        if pr: D=conv(D,dist);U+=u2;P+=pr
    print('  sem 2020 PS',round(U/2/P,3),'p',round(sum(v for k,v in D.items() if k>=U-1e-9),4))
run(set(),'A) vencido no acórdão prevalente')
run({45682,46059},'B) + vencido no 1º acórdão (45682, 46059)')

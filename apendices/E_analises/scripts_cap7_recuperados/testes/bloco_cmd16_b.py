exec(open('./org.py').read().split("D={0:1.0}")[0].replace("print(len(p)","(len(p)"))
rel={int(t.split()[0]):t.split()[1] for t in open('./relp.txt').read().strip().split(';')}
p['rcl']=p.rcl.astype(int); p['rel']=p.rcl.map(rel)
venc={28747,29158,31130,43110,43220,52089,57785,58048,59482,63264,65017,66246,70705}
for extra,lab in [(set(),'A'),({45682,46059},'B')]:
    q=p.copy(); q['A']=np.where(q.rcl.isin(venc|extra),1-q.A,q.A)
    for excl in [['Moraes'],['Toffoli'],['Moraes','Toffoli']]:
        s0=q[~q.rel.isin(excl)]; D={0:1.0};U=0;P=0
        for g,s in s0.groupby('rel'):
            u2,pr,dist=ustats(s)
            if pr: D=conv(D,dist);U+=u2;P+=pr
        print(lab,'sem',excl,'PS',round(U/2/P,3),'p',round(sum(v for k,v in D.items() if k>=U-1e-9),3),'pares',P)

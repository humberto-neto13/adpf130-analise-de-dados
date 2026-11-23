exec(open('./org.py').read().split("D={0:1.0}")[0].replace("print(len(p)","(len(p)"))
rel={int(t.split()[0]):t.split()[1] for t in open('./relp.txt').read().strip().split(';')}
p['rel']=p.rcl.astype(int).map(rel); assert p.rel.notna().all()
out=[]
for g,s in p.groupby('rel'):
    u2,pr,dist=ustats(s)
    out.append((g,s.dt.dt.year.min(),s.dt.dt.year.max(),len(s),int(s.A.sum()),pr,round(u2/2/pr,2) if pr else None))
o=pd.DataFrame(out,columns=['rel','de','ate','n','13A','pares','PS']).sort_values('pares',ascending=False)
o['%pares']=(100*o.pares/o.pares.sum()).round(0); print(o.to_string(index=False)); print(o.pares.sum())

exec(open('./org.py').read().split("D={0:1.0}")[0].replace("print(len(p)","(len(p)"))
rel={int(t.split()[0]):t.split()[1] for t in open('./relp.txt').read().strip().split(';')}
p['rcl']=p.rcl.astype(int); p['rel']=p.rcl.map(rel)
venc={28747,29158,31130,43110,43220,52089,57785,58048,59482,63264,65017,66246,70705,45682,46059}
p['A']=np.where(p.rcl.isin(venc),1-p.A,p.A)
seat={'Teori':'Teori/Moraes','Moraes':'Teori/Moraes','Celso':'Celso/NunesM','NunesM':'Celso/NunesM','MarcoA':'MarcoA/Mendonça','Mendonça':'MarcoA/Mendonça','Lewand':'Lewand/Zanin','Zanin':'Lewand/Zanin','Rosa':'Rosa/Dino','Dino':'Rosa/Dino'}
p['cad']=p.rel.map(lambda r:seat.get(r,r))
def test(df,key,show=False):
    D={0:1.0};U=0;P=0;rows=[]
    for g,s in df.groupby(key):
        u2,pr,dist=ustats(s); rows.append((g,len(s),int(s.A.sum()),pr,round(u2/2/pr,2) if pr else None))
        if pr: D=conv(D,dist);U+=u2;P+=pr
    if show: print(pd.DataFrame(rows,columns=['estrato','n','voto_ader','pares','PS']).sort_values('pares',ascending=False).to_string(index=False))
    return round(U/2/P,3),round(sum(v for k,v in D.items() if k>=U-1e-9),4),P
print('relator',test(p,'rel'))
print('cadeira',test(p,'cad',True))
print('cadeira sem 2020',test(p[p.dt.dt.year!=2020],'cad'))
print('cadeira sem Teori/Moraes',test(p[p.cad!='Teori/Moraes'],'cad'))
print('cadeira sem Toffoli',test(p[p.cad!='Toffoli'],'cad'))
print('cadeira sem ambos',test(p[~p.cad.isin(['Teori/Moraes','Toffoli'])],'cad'))

exec(open('./org.py').read().split("D={0:1.0}")[0].replace("print(len(p)","(len(p)"))
m4={};m5={}
for t in open('v24.txt').read().strip().split(';'):
    r,a,b=t.split(); m4[int(r)]=set(b.split(','))
for t in open('v5.txt').read().strip().split(';'):
    r,a=t.split(); m5[int(r)]=set(a.split(','))
p['rcl']=p.rcl.astype(int)
def rec(s): return 'a empresa' if 'a' in s else ('b individual' if 'b' in s else ('c não profissional' if 'c' in s else 'outros/ND'))
def meio(s):
    if s=={'ND'}: return 'ND'
    if s&{'d','e','f'}: return 'digital não jornalístico (d,e,f)'
    if s<= {'a','b','c'}: return 'clássico (a,b,c)'
    return 'outro (g)'
p['rec']=p.rcl.map(lambda r:rec(m4[r])); p['meio']=p.rcl.map(lambda r:meio(m5[r]))
p['per']=np.where(p.dt.dt.year<=2021,'até 2021','2022+')
for col in ['rec','meio']:
    print('\n',col)
    for g,s in p.groupby(col):
        u2,pr,dist=ustats(s); pv=sum(v for k,v in dist.items() if k>=u2-1e-9) if pr else None
        a1=s[s.per=='até 2021'].A; a2=s[s.per=='2022+'].A
        print(f"{g:35s} n={len(s):3d} 13A={s.A.sum():2d} PS={round(u2/2/pr,2) if pr else '-'} p={round(pv,3) if pv is not None else '-'}  ate2021 {a1.sum()}/{len(a1)}  2022+ {a2.sum()}/{len(a2)}")

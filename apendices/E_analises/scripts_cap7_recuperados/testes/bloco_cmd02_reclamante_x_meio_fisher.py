src=open('./strat.py').read()
exec(src.split("# passo 1")[0])
import pandas as pd
t=pd.crosstab(p.PROF,p.DIG,margins=True); print(t)
from scipy.stats import fisher_exact
s=p[(p.PROF!='ND')&(p.DIG!='ND')]
tt=pd.crosstab(s.PROF=='profissional',s.DIG=='digital'); print(tt); print(fisher_exact(tt.values))

"""Notebook entry points for the same fixed revision runners used by the CLI."""
import subprocess,sys
from revision_common import ROOT

COMMANDS={'a2':('revision_synthetic.py','a2'),'multi':('revision_synthetic.py','multi'),
          'a10':('revision_synthetic.py','a10'),'ou':('revision_synthetic.py','ou'),
          'comparison':('revision_comparison.py',),'product10':('revision_products.py','10'),
          'product50':('revision_products.py','50'),**{'alanine_'+s:('revision_alanine.py',s) for s in ('cost','variability','iid')}}

def ensure_stages(*names):
    for name in names:
        script,*args=COMMANDS[name]
        subprocess.run([sys.executable,'-u','-B',str(ROOT/'supplementary'/script),*args],cwd=ROOT,check=True)

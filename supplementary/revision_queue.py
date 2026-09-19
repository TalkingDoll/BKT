"""Run fixed repetitions concurrently and reserve isolated stages for cost measurements."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed

ROOT=Path(__file__).resolve().parents[1]
STAGES=[('a10','revision_synthetic.py','a10'),('ou','revision_synthetic.py','ou'),
        ('a2','revision_synthetic.py','a2'),('multi','revision_synthetic.py','multi'),
        ('comparison','revision_comparison.py'),('alanine_cost','revision_alanine.py','cost'),
        ('alanine_variability','revision_alanine.py','variability'),('alanine_iid','revision_alanine.py','iid'),
        ('alanine_rbf','revision_alanine.py','rbf'),('product10','revision_products.py','10'),
        ('product50','revision_products.py','50')]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait-for-active-store',action='store_true')
    parser.add_argument('--start-at',choices=[s[0] for s in STAGES],default='a10')
    parser.add_argument('--repetition-processes',type=int,choices=range(1,9),default=4)
    parser.add_argument('--product-processes',type=int,choices=(1,2),default=2)
    args=parser.parse_args()
    lock=ROOT/'outputs/data/session.lock'
    if args.wait_for_active_store:
        print('Waiting for the current archive session to finish before starting the revision queue.',flush=True)
        while lock.exists():time.sleep(10)
    elif lock.exists():raise RuntimeError('Another experiment owns the archive session.')
    for name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):
        os.environ[name]='1'
    from experiment_store import managed_outputs
    from revision_common import OUT,write_json,row_count,record_execution
    from revision_synthetic import collect
    with managed_outputs('double_well','ou','alanine'):
        OUT.mkdir(exist_ok=True,parents=True)
        manifest=dict(started_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,
                      hardware=platform.uname()._asdict(),processor=platform.processor(),logical_cpus=os.cpu_count(),
                      threads=1,product_coordinate_workers=8,repetition_processes=args.repetition_processes,
                      product_processes=args.product_processes,quick=False,stages=[],
                      scheduling='Each repeated synthetic case has one BLAS thread. Comparison and alanine cost stages run alone. Concurrent repetition timings are descriptive, not sampler comparisons.')
        manifest['implementation_sha256']={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [ROOT/'BKT_experiments.ipynb',*sorted((ROOT/'supplementary').glob('revision_*.py'))]}
        write_json(OUT/'execution_manifest.json',manifest)
        selected=STAGES[[s[0] for s in STAGES].index(args.start_at):]
        # Complete isolated measurements before any concurrent seed processes.
        selected=[s for s in selected if s[0] in ('comparison','alanine_cost')]+[s for s in selected if s[0] not in ('comparison','alanine_cost')]
        def execute(name,script,arguments,seed=None):
            child_name=name if seed is None else f'{name}_seed{seed}'
            log=OUT/(child_name+'.log');started=time.perf_counter()
            command=[sys.executable,'-u','-B',str(ROOT/'supplementary'/script),*arguments]
            if seed is not None:command+=['--seed-index',str(seed)]
            with log.open('a',encoding='utf-8') as output:
                result=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
            return dict(stage=name,seed_index=seed,exit_code=result.returncode,wall_seconds=time.perf_counter()-started,
                        finished_utc=datetime.now(timezone.utc).isoformat(),log=str(log.relative_to(ROOT)).replace('\\','/'))
        for name,script,*arguments in selected:
            print('STAGE START',name,flush=True);start=time.perf_counter()
            concurrent=name in ('a10','a2','multi','product10','product50')
            workers=(args.product_processes if name.startswith('product') else args.repetition_processes) if concurrent else 1
            if concurrent:
                folder='products' if name.startswith('product') else name;before=row_count(folder);results=[]
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    from revision_common import PRODUCT_SEED_INDICES
                    indices=PRODUCT_SEED_INDICES if name.startswith('product') else range(10)
                    futures=[executor.submit(execute,name,script,arguments,seed) for seed in indices]
                    for future in as_completed(futures):
                        result=future.result();results.append(result);print('SEED END',json.dumps(result),flush=True)
                collect(folder)
                record_execution(name,time.perf_counter()-start,before,row_count(folder),repetition_processes=workers,
                                 blas_threads_per_process=1,coordinate_workers_per_process=8 if name.startswith('product') else 1,
                                 children=sorted(results,key=lambda r:r['seed_index']),
                                 timing_interpretation='Elapsed stage wall time with independent prescribed seeds running concurrently; not a sampler timing comparison')
            else:results=[execute(name,script,arguments)]
            row=dict(stage=name,exit_code=int(any(r['exit_code']!=0 for r in results)),wall_seconds=time.perf_counter()-start,
                     finished_utc=datetime.now(timezone.utc).isoformat(),repetition_processes=workers,children=results)
            manifest['stages'].append(row);write_json(OUT/'execution_manifest.json',manifest)
            print('STAGE END',json.dumps(row),flush=True)
        manifest['complete']=all(r['exit_code']==0 for r in manifest['stages'])
        manifest['complete_definition']='All runner processes finished without programming errors; individual numerical runs may be incomplete or failed and remain in the data.'
        write_json(OUT/'execution_manifest.json',manifest)
    print('REVISION QUEUE FINISHED',flush=True)

if __name__=='__main__':main()

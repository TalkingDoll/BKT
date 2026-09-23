"""Publish complete, fixed-protocol revision results into the retained data model."""
from __future__ import annotations
import argparse,copy,hashlib,json,statistics
from collections import defaultdict
import numpy as np
from revision_common import ROOT,OUT,api,current_records,write_json,load_run,save_run,array_sha,summarize,PRODUCT_SEED_INDICES
from revision_synthetic import collect

def aggregate(values):
    a=np.asarray(list(values),dtype=float)
    if a.ndim==1:return summarize(a.tolist())
    return dict(values=a.tolist(),mean=a.mean(0).tolist(),std=a.std(0,ddof=1).tolist(),
                median=np.median(a,axis=0).tolist(),n=len(a))

def grouped(rows,keys):
    result=defaultdict(list)
    for row in rows:result[tuple(row.get(k) for k in keys)].append(row)
    return result

def source_rows(folder):
    rows=collect(folder)
    if not rows:raise ValueError('Missing prescribed task: '+folder)
    return sorted(rows,key=lambda r:r['id'])


def refresh_sidecars(a2,comparison):
    """Verify the current saved arrays and input identities."""
    verified=json.loads((OUT/'verification.json').read_text())
    for name,rows,task in [('admissible_source',a2,'a2'),('data_comparison',comparison,'comparison')]:
        write_json(ROOT/'outputs'/name/'validation_checks.json',dict(
            protocol='revision-B1-B4-v1',source_x2_variance=.3,unique_runs=len(rows),
            complete_source_indices=list(range(10)),
            scope='Saved full/filtered distances and masks recomputed by revision_verify; this is not a refit or sampler rerun.',
            saved_array_audit=next(v for v in verified['tasks'] if v['task']==task),
            maximum_metric_difference_across_revision=verified['max_absolute_metric_difference']))
    cfg=json.loads((ROOT/'outputs/admissible_source/config.json').read_text())
    from run_admissible_source import new_source
    ns=api();source_checks=[];pot=ns['Potential']('A',d=2,beta=0.)
    for seed in [*range(500,510),*range(700,710)]:
        original=ns['source_A'](pot,2000,np.random.default_rng(seed))
        current=new_source(cfg,seed)
        assert np.array_equal(original[:,0],current[:,0])
        source_checks.append(dict(seed=seed,first_coordinate_bitwise_equal=True))
    write_json(ROOT/'outputs/admissible_source/probe_checks.json',dict(
        protocol='revision-B1-B4-v1',status='passed',source_checks=source_checks,
        scope='First-coordinate source equality for all ten S and I designs.'))
    for beta in cfg['betas']:
        part=[r for r in a2 if r['beta']==beta]
        write_json(ROOT/f'outputs/admissible_source/metadata_beta{beta:g}.json',dict(
            beta=beta,protocol='revision-B1-B4-v1',source_indices=list(range(10)),unique_runs=len(part),
            threads_per_process=1,timing_record='outputs/revision/a2_execution.json',
            timing_scope='Joint stage wall time across coupling values; no new per-beta cost is inferred',
            q_tail_coefficient=1/(2*.3)-1-beta/2))
    folder=ROOT/'outputs/data_comparison';provenance=json.loads((folder/'input_provenance.json').read_text())
    for r in provenance:
        r.update(source_matches_main=True,scope='Current ten-seed input hashes; no load-time measurement is implied')
    write_json(folder/'input_probe.json',provenance)
    write_json(folder/'numerical_provenance.json',dict(
        protocol='revision-B1-B4-v1',config=json.loads((folder/'config.json').read_text()),
        execution_record='outputs/revision/comparison_execution.json',
        per_realisation_records='outputs/revision/comparison_runs.json'))
    from diagnose_data_comparison_endpoints import main as endpoint_diagnostics
    endpoint_diagnostics()

def enrich_metrics(folder,rows):
    ns=api();targets={};result=[]
    for row in rows:
        row=copy.deepcopy(row)
        if row.get('T') is not None and row.get('dt') is not None:
            row['integrated_steps']=int(round(row['T']/row['dt']))
            row['effective_horizon']=row['integrated_steps']*row['dt']
        if row['status']=='ok':
            name=row['system']
            if name not in targets:
                if name.startswith('A10'):pot=ns['Potential']('A',d=10,beta=float(name.split('beta')[1]))
                else:pot=ns['Potential'](name[2:])
                targets[name]=(pot,ns['stationary_samples'](pot,1000 if pot.d==10 else 2000,np.random.default_rng(7)))
            pot,target=targets[name];_,arrays=load_run(folder,row['id']);x=arrays['final']
            measured=ns['particle_metrics'](x,target)
            if abs(measured['sw']-row['sw2'])>1e-12:raise AssertionError('Saved endpoint metric mismatch: '+row['id'])
            row.update(measured,finite=True)
            row['mass']=ns['well_masses'](x,pot).tolist() if pot.d==2 else float((x[:,0]<0).mean())
        else:row.update(sw=None,finite=False)
        result.append(row)
    return result

def method_summary(rows):
    rows=sorted(rows,key=lambda r:r['seed'])
    s=summarize(r.get('sw',r.get('sw2')) for r in rows)
    return dict(s,rows=rows,sw=s['values'],all_finite=s['nonfinite_count']==0)

def publish_regular(primary,folder):
    rows=enrich_metrics(folder,source_rows(folder))
    write_json(OUT/(folder+'_enriched.json'),rows)
    for name,part in grouped(rows,['system']).items():
        name=name[0];case=copy.deepcopy(primary[name]);case['seeds']=10
        case.pop('seconds',None)
        case['source_sw_scope']='First prescribed source cloud, seed 500; not an average over realisations'
        if (OUT/f'{folder}_execution.json').exists():case['timing_record']=f'outputs/revision/{folder}_execution.json'
        else:case.pop('timing_record',None)
        case['selection_rule']=2 if folder=='a10' else None
        case['revision']='B1 independent mode selection and B2 ten fixed realisations' if folder=='a10' else 'B2 ten fixed realisations'
        selected=case['selected_n'];rank=case['r']
        defaults=[r for r in part if r.get('dictionary_size_parameter') is None]
        for method,key in [('RBF','rbf'),('Legendre','poly')]:
            main=[r for r in defaults if r['method']==method and r['n_pairs']==selected and r['r_requested']==rank]
            assert {r['seed'] for r in main}==set(range(10)),(name,method,'missing seed')
            previous=case[key];case[key]=method_summary(main)
            case[key]['rscan']={str(r['r_requested']):r for r in defaults if r['method']==method and r['seed']==0 and r['n_pairs']==selected}
            if name=='B_poly9' and method=='Legendre':
                case[key]['above_ten_reference_mean']=sum(r['sw2'] is not None and r['sw2']>10*case['reference']['metrics']['sw']['mean'] for r in main)
                case[key]['table_statistic']='Median and count above ten times the reference mean; all ten values retained'
        case['sample_size']={str(n):sorted([r for r in defaults if r['method']=='RBF' and r['n_pairs']==n and r['r_requested']==rank],key=lambda r:r['seed']) for n in (10000,100000,200000)}
        for budget,values in case['sample_size'].items():assert {r['seed'] for r in values}==set(range(10)),(name,budget)
        if folder=='a10':
            case['legendre_sample_size']={str(n):method_summary([r for r in defaults if r['method']=='Legendre' and r['n_pairs']==n and r['r_requested']==rank]) for n in (10000,100000,200000)}
            for budget,values in case['legendre_sample_size'].items():assert {r['seed'] for r in values['rows']}==set(range(10)),(name,'Legendre',budget)
        if name=='B_quartic4':assert {r['seed'] for r in defaults if r['method']=='Legendre' and r['r_requested']==32}==set(range(10))
        fd=[r for r in defaults if r['method']=='FD' and r['r_requested']==rank]
        if fd:
            assert {r['seed'] for r in fd}==set(range(10))
            case['fd']=method_summary(fd);case['fd']['sw']=case['fd']['mean']
        if folder=='multi':case['fd_rscan']={str(r['r_requested']):r for r in defaults if r['method']=='FD' and r['seed']==0}
        primary[name]=case
    return rows

def publish_a2(primary=None):
    from run_admissible_source import new_source,specifications,run_id
    rows=source_rows('a2');cfg=json.loads((OUT/'a2_config.json').read_text());cfg['output_directory']='outputs/admissible_source'
    expected={run_id(r) for b in cfg['betas'] for r in specifications(cfg,b)}
    assert {r['id'] for r in rows}==expected
    old=current_records()['outputs/admissible_source/summary.json'];folder=ROOT/'outputs/admissible_source';allrows=[]
    for row in rows:
        beta,seed=row['beta'],row['seed'];source=new_source(cfg,500+seed);independent=new_source(cfg,700+seed)
        assert array_sha(source)==row['source_sha256'],row['id']
        initial=f'source_beta{beta:g}_seed{seed}.npz';endpoint='endpoint_'+row['id']+'.npz'
        _,arrays=load_run('a2',row['id']);coeff=arrays['coefficients'];x=arrays['final']
        np.savez_compressed(folder/initial,initial=source,independent_coefficients=independent)
        np.savez_compressed(folder/endpoint,**arrays)
        row=dict(row,run_id=row['id'],events=row['diagnostics'],checkpoint_records=row['checkpoints'],
                 source_x2_variance=.3,coefficient_seed=(700 if row['regime']=='I' else 500)+seed,
                 coefficient_sample_count=2000,extra_coefficient_samples=2000 if row['regime']=='I' else 0,
                 initial_file=initial,endpoint_file=endpoint,endpoint_sha256=array_sha(x),coefficients_sha256=array_sha(coeff),
                 coefficient_source_sha256=array_sha(independent if row['regime']=='I' else source),
                 reference_mean=row['reference']['mean'],reference_std=row['reference']['std'])
        allrows.append(row)
    keys=['beta','method','regime','n_pairs','r_requested','dt'];groups=[]
    for key,part in grouped(allrows,keys).items():
        summary=summarize(r['sw2'] for r in part)
        groups.append(dict(zip(keys,key),**{**summary,'sw2_mean':summary['mean'],'sw2_std':summary['std'],
            'r_used':sorted({r['r_used'] for r in part}),'roles':sorted({v for r in part for v in r['roles']}),
            'failures':sum(r['status']!='ok' for r in part)}))
    execution=json.loads((OUT/'a2_execution.json').read_text())
    metadata=dict(complete=True,fd_label='FD-201',revision='B2 and B4',
                  worker_processes=execution.get('repetition_processes',1),threads_per_worker=1,
                  timing_interpretation='Descriptive instrumented wall time; independent repetitions may run concurrently, with one BLAS thread per process')
    result=dict(config=cfg,runs=allrows,groups=groups,references=old['references'],metadata=metadata)
    for name,data in [('config',cfg),('runs',allrows),('summary',result)]:write_json(folder/(name+'.json'),data)
    for beta in cfg['betas']:write_json(folder/f'runs_beta{beta:g}.json',[r for r in allrows if r['beta']==beta])
    write_json(ROOT/'configs/retained/admissible_source/config.json',cfg)
    write_json(ROOT/'supplementary/admissible_source_config.json',cfg)
    update_index=primary is None
    if primary is None:primary=json.loads((ROOT/'outputs/results.json').read_text())
    for beta in cfg['betas']:
        name=f'A2_beta{beta}';case=dict(reference=copy.deepcopy(primary[name]['reference']),M=2000,r=64,dt=.05,
            seeds=10,selected_n=200000,source_x2_variance=.3,purpose='Current admissible-source B2/B4 result index')
        part=[dict(r,sw=r['sw2']) for r in allrows if r['beta']==beta]
        for label,key in [('FD','fd'),('RBF','rbf'),('Legendre','poly')]:
            main=[r for r in part if r['method']==label and 'main' in r['roles']]
            case[key]=method_summary(main)
            scan={str(r['r_requested']):r for r in part if r['method']==label and 'rank_scan' in r['roles']}
            if label=='FD':case['fd']['sw']=case['fd']['mean'];case['fd_rscan']=scan
            else:case[key]['rscan']=scan
        case['sample_size']={str(n):[r for r in part if 'sample_size' in r['roles'] and r['n_pairs']==n] for n in cfg['sample_size_budgets']}
        primary[name]=case
    if update_index:write_json(ROOT/'outputs/results.json',primary)
    return allrows

def publish_comparison():
    rows=source_rows('comparison');old=current_records()['outputs/data_comparison/summary.json']
    cfg=json.loads((OUT/'comparison_config.json').read_text());cfg['output_directory']='outputs/data_comparison'
    cfg['resume_policy']='Reuse saved prescribed rows by run identity under the fixed numerical configuration. Cost measurements include fresh fitting and transport.'
    revision_cfg=dict(cfg,output_directory='outputs/revision/comparison')
    write_json(OUT/'comparison_config.json',revision_cfg)
    assert {(r['beta'],r['seed'],r['method']) for r in rows}=={(b,s,m) for b in (0.,.5) for s in range(10) for m in ('A','D')}
    folder=ROOT/'outputs/data_comparison';a2=json.loads((ROOT/'outputs/admissible_source/runs.json').read_text());provenance=[]
    for row in rows:
        beta,seed=row['beta'],row['seed'];_,arrays=load_run('comparison',row['id'])
        from run_admissible_source import new_source
        initial=new_source(cfg,500+seed)
        assert array_sha(initial)==row['source_sha256'],row['id']
        source_file=folder/f'source_beta{beta:g}_seed{seed}.npz'
        if row['method']=='A':np.savez_compressed(source_file,initial=initial)
        row['endpoint_file']='endpoint_'+row['id']+'.npz'
        if 'final' in arrays:
            np.savez_compressed(folder/row['endpoint_file'],final=arrays['final']);row['endpoint_sha256']=array_sha(arrays['final'])
        with np.load(folder/f'evaluation_beta{beta:g}.npz') as z:row['directions_sha256']=array_sha(z['directions'])
        row.update(training_seed=100+seed,source_seed=500+seed,particles=2000,training_pairs_available=200000,
                   shared_horizon=row.get('T'),effective_horizon=row.get('T'))
        if row['status']=='ok':
            expected_times=np.unique(np.r_[np.arange(0.,row['T'],.5),row['T']])
            actual_times=np.asarray([c['time'] for c in row['checkpoint_records']])
            assert actual_times.shape==expected_times.shape and np.max(abs(actual_times-expected_times))<=1e-12,row['id']
            assert row['fit_seconds']>0 and row['sample_seconds']>0,row['id']
            assert abs(row['total_seconds']-row['fit_seconds']-row['sample_seconds'])<1e-10,row['id']
        if row['method']=='A':
            main=next(r for r in a2 if r['beta']==beta and r['seed']==seed and r['method']=='RBF' and 'main' in r['roles'])
            if row['status']=='ok' and main['status']=='ok':
                row['bkt_parity_absolute_error']=abs(row['sw2']-main['sw2'])
                for key in ('source_sha256','target_sha256','training_x_sha256','training_y_sha256'):assert row[key]==main[key],(row['id'],key)
                with np.load(ROOT/'outputs/admissible_source'/main['endpoint_file']) as z:
                    row['bkt_endpoint_max_absolute_error']=float(np.max(abs(arrays['final']-z['final'])))
                assert len(row['checkpoint_records'])==len(main['checkpoint_records'])
                row['bkt_checkpoint_max_absolute_error']=max(abs(a['sw2']-b['sw2']) for a,b in zip(row['checkpoint_records'],main['checkpoint_records']))
            provenance.append({k:v for k,v in row.items() if k in ('beta','seed','source_sha256','target_sha256','training_x_sha256','training_y_sha256','directions_sha256')})
    from run_data_comparison import summarize as comparison_summary
    result=comparison_summary(rows,old['references'],cfg);result.update(runs=rows,timing_provenance=dict(per_run_status='measured',threads=1),metadata=json.loads((OUT/'comparison_execution.json').read_text()))
    for item in result['rows']:
        part=[r for r in rows if r['beta']==item['beta'] and r['method']==item['method']]
        for key in ('sw2','fit_seconds','sample_seconds','total_seconds'):item[key+'_summary']=summarize(r.get(key) for r in part)
    write_json(OUT/'comparison_summary.json',dict(result,config=revision_cfg))
    for name,data in [('summary',result),('runs',rows),('config',cfg),('input_provenance',provenance)]:write_json(folder/(name+'.json'),data)
    write_json(ROOT/'configs/retained/data_comparison/config.json',cfg)
    write_json(ROOT/'supplementary/data_comparison_config.json',cfg)
    return rows

def publish_ou():
    rows=source_rows('ou');base=current_records()
    assert {r['rank'] for r in rows if r['system']=='OU1'}=={r['r'] for r in base['outputs/ou_results.json']['rank_scan']}|{40}
    for coupling,name in [(0.,'ou_hd_uncoupled_results.json'),(.15,'ou_hd_results.json')]:
        part=sorted([r for r in rows if r['system']=='OU10' and r['coupling']==coupling],key=lambda r:r['seed'])
        assert {r['seed'] for r in part}==set(range(700,710))
        result=copy.deepcopy(base['outputs/'+name]);result['config']['source_seeds']=list(range(700,710));result['rows']=part
        result.pop('elapsed_seconds',None)
        result['timing_record']='outputs/revision/ou_execution.json'
        result['time_summary']=[]
        for index,t in enumerate(result['config']['times']):
            metrics={key:aggregate(r['metrics'][index][key] for r in part) for key in part[0]['metrics'][index] if key!='time'}
            result['time_summary'].append(dict(time=t,metrics=metrics))
        result['revision']='B2 ten fixed source clouds; B4 path masks'
        write_json(ROOT/'outputs'/name,result)
    return rows

def publish_products():
    rows=source_rows('products');base=current_records()
    with np.load(ROOT/'outputs/product_plot_data.npz') as z:plot={k:z[k] for k in z.files}
    for d in (10,50):
        result=copy.deepcopy(base[f'outputs/product_{d}_results.json'])
        result['config'].pop('source_seed',None);result['config'].pop('training_seed',None)
        result['config'].update(realisations=10,source_seed_base=1,training_seed_base=1001,
            seed_indices=list(PRODUCT_SEED_INDICES),source_seeds=[1+s for s in PRODUCT_SEED_INDICES],
            training_seeds=[1001+s for s in PRODUCT_SEED_INDICES],representative_source_seed=1)
        result['config'].pop('source_target_dependence',None)
        result['config'].pop('seed_correction',None)
        result['config']['seed_protocol']='Source seeds are 1+s with indices 0--5 and 7--10; every source seed differs from target seed 7.'
        steps=int(round(result['config']['T']/result['config']['dt']))
        result['config'].update(integrated_steps=steps,effective_horizon=steps*result['config']['dt'])
        result['methods']={}
        for label,name in [('FD','exact'),('RBF','estimated'),('Legendre','legendre')]:
            part=sorted([r for r in rows if r['dimension']==d and r['method']==label],key=lambda r:r['seed'])
            assert {r['seed'] for r in part}==set(PRODUCT_SEED_INDICES)
            metrics={key:aggregate(r['metrics'][key] for r in part) for key in part[0]['metrics']}
            result['methods'][name]=dict(rows=part,metrics=metrics,**{key:v['mean'] for key,v in metrics.items()})
            prefix=f'pdw_{d}_{name}';plot[prefix+'_marginal_w2']=np.asarray(metrics['marginal_w2']['mean'])
            plot[prefix+'_marginal_w2_std']=np.asarray(metrics['marginal_w2']['std'])
            _,a=load_run('products',part[0]['id'])
            plot[prefix+'_transported_x1']=a['final'][:,0]
            for key in ('source_x1','target_x1'):plot[prefix+'_'+key]=a[key]
        result['figure_protocol']='First prescribed realisation in histograms; ten-realisation mean and sample SD for marginal W2'
        write_json(ROOT/f'outputs/product_{d}_results.json',result)
    np.savez_compressed(ROOT/'outputs/product_plot_data.npz',**plot)
    return rows

def publish_alanine():
    """Label existing rotation checkpoints without modifying any cloud."""
    from revision_alanine import label_rotation_endpoint
    rows=source_rows('alanine')
    for row in rows:
        if row.get('task')!='B3b_rotation':continue
        previous=copy.deepcopy(row);label_rotation_endpoint(row)
        if row!=previous:
            _,arrays=load_run('alanine',row['id'])
            save_run('alanine',row['id'],row,arrays)
    return source_rows('alanine')


def main():
    primary=copy.deepcopy(current_records()['outputs/results.json'])
    a2=publish_a2(primary);multi=publish_regular(primary,'multi');high=publish_regular(primary,'a10')
    primary['_config'].update(version='revision-B1-B4-v1',seeds=[10,10,10],selection_rule=2)
    primary['_config'].pop('code',None)
    primary['_config'].pop('source_snapshot',None)
    write_json(ROOT/'outputs/results.json',primary)
    comparison=publish_comparison();ou=publish_ou();products=publish_products()
    refresh_sidecars(a2,comparison)
    from revision_report import build_revision_results
    data=dict(a2=a2,multi=multi,a10=high,comparison=comparison,ou=ou,products=products,alanine=publish_alanine())
    summary=build_revision_results(data)
    from experiment_records import export_public
    export_public(data,summary)
    from manuscript_results import write_tables,write_report
    write_tables();write_report()
    manifest_path=ROOT/'configs/retained/manifest.json';manifest=json.loads(manifest_path.read_text())
    write_json(ROOT/'configs/retained/revision.json',json.loads((OUT/'configuration.json').read_text()))
    manifest['files']['configs/retained/revision.json']=dict(archive='double_well.zip',member='outputs/revision/configuration.json')
    manifest['description']='Configuration snapshots from local experiment archives, published with UTF-8/LF serialization. Snapshot and original archive-member byte hashes are recorded separately; their parsed JSON contents agree.'
    for name,record in manifest['files'].items():
        path=ROOT/name;path.write_text(path.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
        member=ROOT/record['member']
        assert json.loads(path.read_text())==json.loads(member.read_text()),name
        record['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        record['archive_member_sha256']=hashlib.sha256(member.read_bytes()).hexdigest()
    write_json(manifest_path,manifest)
    print('Published complete revision results and the unified report.',flush=True)

if __name__=='__main__':
    from experiment_store import managed_outputs
    from threadpoolctl import threadpool_limits
    with managed_outputs('double_well','ou','alanine'),threadpool_limits(limits=1):main()

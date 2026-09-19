"""Revision statistics, reproduction audit and the single manuscript report section."""
from __future__ import annotations
import copy,json,statistics
from collections import defaultdict
import numpy as np
from revision_common import ROOT,OUT,baseline_records,write_json,summarize,load_run,PRODUCT_SEED_INDICES

def group(rows,fields):
    groups=defaultdict(list)
    for row in rows:groups[tuple(row.get(k) for k in fields)].append(row)
    return groups

def fmt(v):
    if v is None:return 'unavailable'
    if isinstance(v,dict):return fmt(v.get('mean'))+(' +/- '+fmt(v['std']) if v.get('std') is not None else '')
    if isinstance(v,(int,np.integer)):return str(v)
    return f'{v:.6g}' if isinstance(v,(float,np.floating)) else str(v)

def table(lines,headers,rows):
    lines+=['','| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']
    lines+=['| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in rows];lines.append('')

def configuration_label(task,c):
    names={'B_quartic4':'2D four-well product','B_poly9':'2D nine wells',
           'A10_beta0.0':'10D double well product, beta=0','A10_beta0.5':'10D double well, beta=0.5',
           'product10':'10D double-well product','product50':'50D double-well product','OU1':'1D OU','OU10':'10D OU'}
    name=names.get(c.get('system'),'2D double well' if task in ('a2','comparison') else task)
    parts=[name]
    if c.get('beta') is not None:parts.append('beta='+fmt(c['beta']))
    if c.get('coupling') is not None:parts.append('gamma='+fmt(c['coupling']))
    if c.get('method') is not None:
        parts.append({'RBF':'Koopman (RBF)','Legendre':'Koopman (Legendre)','A':'BKT','B':'Drift + Langevin','D':'KDE flow'}.get(c['method'],c['method']))
    for field,label in [('regime','regime'),('n_pairs','n'),('r_requested','r'),('rank','r'),('dt','h')]:
        if c.get(field) is not None:parts.append(label+'='+fmt(c[field]))
    if c.get('dictionary_size_parameter') is not None:
        parts.append(('centres per coordinate=' if c['method']=='RBF' else 'degree=')+fmt(c['dictionary_size_parameter']))
    return '; '.join(parts)

def build_revision_results(data):
    base=baseline_records();statistics_rows=[];parity=[];paired=[];changes=[]
    expected=dict(a2=320,a10=142,multi=134,products=60,comparison=60,alanine=42,
                  ou=20+len({r['r'] for r in base['outputs/ou_results.json']['rank_scan']}|{40}))
    for task,count in expected.items():assert len(data[task])==count,(task,len(data[task]),count)
    # The nine-well r=8 entry is both the metastable rank and an FD scan rank.
    # Count each prescribed configuration once: 72 four-well + 62 nine-well rows.
    multi_ids=set()
    for system,wells in [('B_quartic4',4),('B_poly9',9)]:
        for seed in range(10):
            for method in ('rbf','poly'):
                for budget in ((10000,100000,200000) if method=='rbf' else (200000,)):
                    multi_ids.add(f'{system}_{method}_n{budget}_r64_size0_seed{seed}')
            if seed==0:
                for method in ('rbf','poly'):
                    for rank in {16,32,64,96,wells-1}-{64}:
                        multi_ids.add(f'{system}_{method}_n200000_r{rank}_size0_seed0')
            elif wells==4:
                multi_ids.add(f'{system}_poly_n200000_r32_size0_seed{seed}')
            for rank in ({8,16,32,64,128,wells-1} if seed==0 else {64}):
                multi_ids.add(f'{system}_FD_r{rank}_seed{seed}')
    assert {r['id'] for r in data['multi']}==multi_ids,'Unexpected multiwell configuration set'
    fields={
        'a2':['beta','method','regime','n_pairs','r_requested','dt'],
        'a10':['system','method','n_pairs','r_requested','dictionary_size_parameter'],
        'multi':['system','method','n_pairs','r_requested'],
        'ou':['system','coupling','rank'], 'products':['system','method'],
        'comparison':['beta','method']}
    for task,keys in fields.items():
        for key,part in group(data[task],keys).items():
            part=sorted(part,key=lambda r:r.get('seed',0));s=summarize(r.get('sw2') for r in part)
            row=dict(task=task,configuration=dict(zip(keys,key)),ids=[r['id'] for r in part],seeds=[r.get('seed') for r in part],sw2=s)
            for field in ('fit_seconds','sample_seconds','sampling_seconds','total_seconds'):
                if any(field in r for r in part):row[field]=summarize(r.get(field) for r in part)
            diagnostics={}
            for field in ('floor','nonpositive','cap','projection','affected'):
                for suffix in ('_particle_fraction','_particle_coordinate_fraction'):
                    k=field+suffix
                    if any(k in r.get('diagnostics',{}) for r in part):diagnostics[k]=summarize(r.get('diagnostics',{}).get(k) for r in part)
            if diagnostics:
                diagnostics['unaffected_sw2']=summarize(r.get('diagnostics',{}).get('unaffected_sw2') for r in part)
                row['path_diagnostics']=diagnostics
            reference=part[0].get('reference')
            if reference and isinstance(reference,dict) and 'mean' in reference:
                row['reference']=reference;row['above_ten_reference_mean']=sum(r.get('sw2') is not None and r['sw2']>10*reference['mean'] for r in part)
            statistics_rows.append(row)
        for row in data[task]:
            check=row.get('parity') or row.get('paired_legacy')
            if check:parity.append(dict(task=task,id=row['id'],check=check))
            if check and check.get('new_endpoint_parity'):
                parity.append(dict(task=task+'_new_endpoint',id=row['id'],check=check['new_endpoint_parity']))
            if task=='comparison' and row.get('method')=='A' and 'bkt_endpoint_max_absolute_error' in row:
                errors={key:row[key] for key in ('bkt_parity_absolute_error','bkt_endpoint_max_absolute_error','bkt_checkpoint_max_absolute_error')}
                parity.append(dict(task='comparison_main_consistency',id=row['id'],check=dict(errors,passes_1e12=max(errors.values())<=1e-12)))
            if task=='a10' and row.get('paired_legacy'):
                paired.append(dict(id=row['id'],system=row['system'],method=row['method'],seed=row['seed'],n_pairs=row['n_pairs'],
                                   rank=row['r_requested'],size=row.get('dictionary_size_parameter'),**row['paired_legacy']))
    # Check archived scalar values as well as cache-level endpoint comparisons.
    for task in ('a10','multi'):
        for r in data[task]:
            if not r.get('paired_legacy'):continue
            old=base['outputs/results.json'][r['system']];previous=None
            if r.get('dictionary_size_parameter') is not None:
                previous=next((o for o in base['outputs/a10_sweep.json']['rows'] if o['dictionary']=={'RBF':'rbf','Legendre':'poly'}[r['method']] and o['size']==r['dictionary_size_parameter'] and o['r_requested']==r['r_requested']),None)
            else:
                part=old['rbf' if r['method']=='RBF' else 'poly']
                if r['n_pairs']==old['selected_n'] and r['r_requested']==old['r']:
                    previous=next((o for o in part['rows'] if o['seed']==r['seed']),None)
                elif r['method']=='RBF' and r['r_requested']==old['r']:
                    previous=next((o for o in old['sample_size'][str(r['n_pairs'])] if o['seed']==r['seed']),None)
                elif r['seed']==0 and r['n_pairs']==old['selected_n']:previous=part.get('rscan',{}).get(str(r['r_requested']))
            if previous:
                difference=abs(r['paired_legacy']['old_sw2']-previous['sw'])
                parity.append(dict(task=task,id=r['id'],check=dict(archived_scalar_sw2=previous['sw'],reproduced_legacy_sw2=r['paired_legacy']['old_sw2'],scalar_absolute_difference=difference,passes_1e12=difference<=1e-12)))
    for r in data['products']:
        if r['seed']==0:
            name={'FD':'exact','RBF':'estimated','Legendre':'legendre'}[r['method']]
            old=base[f"outputs/product_{r['dimension']}_results.json"]['methods'][name]
            for metric,value in old.items():
                if metric in r['metrics'] and isinstance(value,(float,int,list)):
                    diff=float(np.max(abs(np.asarray(value)-r['metrics'][metric])))
                    parity.append(dict(task='products',id=r['id'],metric=metric,check=dict(scalar_absolute_difference=diff,passes_1e12=diff<=1e-12)))
    product_randomness=[]
    for dimension in (10,50):
        for seed in (*PRODUCT_SEED_INDICES,6):
            row,arrays=load_run('products',f'product{dimension}_exact_seed{seed}')
            source,target=arrays['source_x1'],arrays['target_x1']
            same_order=bool(np.array_equal(np.argsort(source),np.argsort(target)))
            assert same_order==(seed==6)
            product_randomness.append(dict(dimension=dimension,seed_index=seed,
                included_in_current_summary=seed in PRODUCT_SEED_INDICES,
                source_seed=row['source_seed'],target_seed=row['target_seed'],
                first_coordinate_rank_order_identical=same_order,
                scope='Both coordinate samplers invert their CDFs using M consecutive uniform draws. The historical index 6 reused seed 7 in source and target; it is excluded. All ten current indices use distinct source and target seeds.'))
    alanine=data['alanine'];rotations=[];cost_summaries=[]
    required={f'rotation_fit{i}_eval{j}_seed{s}' for i in range(3) for j in range(3) if i!=j for s in (1101,1102,1103)}
    assert required<={r['id'] for r in alanine},'Incomplete alanine role rotations'
    assert {f'cost_{m}_seed{s}' for m in ('BKT','LAWGD','KDE') for s in (1101,1102,1103)}<={r['id'] for r in alanine}
    assert {f'iid_seed{s}' for s in (1101,1102,1103)}<={r['id'] for r in alanine}
    assert {f'rbf_collapse_seed{s}' for s in (301,302,303)}|{f'rbf_control_seed{s}' for s in range(901,906)} <= {r['id'] for r in alanine}
    for method in ('BKT','LAWGD','KDE'):
        part=sorted([r for r in alanine if r.get('task')=='B3a_cost' and r['method']==method],key=lambda r:r['seed'])
        complete=all(r['status']=='ok' and r['checkpoints'][-1]['s']==8 for r in part)
        cost_summaries.append(dict(method=method,seeds=[r['seed'] for r in part],all_completed=complete,
            wall_seconds=summarize(r['wall_seconds'] if complete else None for r in part),cpu_seconds=summarize(r['cpu_seconds'] if complete else None for r in part),
            first_hit_wall_seconds=summarize(r['late_time'].get('first_hit_wall_seconds') for r in part),
            first_hit_s=summarize(r['late_time'].get('first_hit_s') for r in part)))
    for key,part in sorted(group([r for r in alanine if r.get('task')=='B3b_rotation'],['fit_trajectory','evaluation_trajectory']).items()):
        complete=all(r['status']=='ok' and r['checkpoints'][-1]['s']==8 for r in part)
        row=dict(fit_trajectory=key[0],evaluation_trajectory=key[1],completed=sum(r['status']=='ok' for r in part),lambda1=part[0]['lambda1'],ids=[r['id'] for r in part])
        for field in ('sw2','mass_tv','local_width_ratio'):row[field]=summarize(r['endpoint'][field] if complete else None for r in part)
        for field in ('sw2','mass_tv'):row['reference_'+field]=summarize(r['reference'][field] for r in part)
        rotations.append(row)
    across={key:summarize(r[key]['mean'] for r in rotations) for key in ('sw2','mass_tv','local_width_ratio','reference_sw2','reference_mass_tv')}
    across['lambda1']=summarize(r['lambda1'] for r in rotations)
    controls={}
    for design,part in [('iid',[r for r in alanine if r.get('task')=='B3c_iid']),
                        ('sobol',[r for r in alanine if r.get('task')=='B3a_cost' and r['method']=='BKT'])]:
        controls[design]={key:summarize(r['checkpoints'][-1][key] if r['status']=='ok' and r['checkpoints'][-1]['s']==8 else None for r in sorted(part,key=lambda r:r['seed']))
                          for key in ('sw2','mass_tv')}
    for r in alanine:
        if r.get('parity'):parity.append(dict(task='alanine',id=r['id'],check=r['parity']))
    from alanine_convergence import inputs as alanine_inputs,load_results as alanine_saved,case_id as alanine_case_id,SPEC as alanine_specification
    original_spectrum,_=alanine_inputs();_,refitted=load_run('alanine','spectrum_fit0')
    original_alanine,original_clouds=alanine_saved()
    for r in alanine:
        if r.get('task')!='B3b_rotation' or (r['fit_trajectory'],r['evaluation_trajectory'])!=(0,2):continue
        _,arrays=load_run('alanine',r['id']);clouds=arrays['clouds']
        previous=original_clouds[alanine_case_id(256,'BKT',r['seed'])+'_clouds'][:len(clouds)]
        oldrow=next(v for v in original_alanine['runs'] if v['method']=='BKT' and v['seed']==r['seed'])
        cloud_error=float(np.max(np.abs(clouds-previous)))
        endpoint_error=float(np.max(np.abs(clouds[-1]-previous[-1])))
        metric_error=max(abs(a['sw2']-b['sw2']) for a,b in zip(r['checkpoints'],oldrow['checkpoints']))
        complete=r['status']=='ok' and r['checkpoints'][-1]['s']==8
        check=dict(endpoint_bitwise_equal=bool(np.array_equal(clouds,previous)),
            endpoint_max_absolute_difference=endpoint_error,max_checkpoint_cloud_difference=cloud_error,
            max_checkpoint_sw2_difference=metric_error,
            requested_horizon_completed=complete,passes_1e12=complete and max(cloud_error,metric_error)<=1e-12,
            scope='Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.')
        parity.append(dict(task='alanine_original_assignment_refit',id=r['id'],check=check))
    eigenvalue_difference=np.abs(refitted['lam']-original_spectrum['lam'])
    parity.append(dict(task='alanine_single_thread_refit',id='spectrum_fit0',check=dict(
        maximum_eigenvalue_absolute_difference=float(eigenvalue_difference.max()),
        maximum_eigenvalue_relative_difference=float(np.max(eigenvalue_difference/np.abs(original_spectrum['lam']))),
        eigenvalues_above_absolute_tolerance=int(np.count_nonzero(eigenvalue_difference>1e-12)),
        lambda1_absolute_difference=float(eigenvalue_difference[0]),
        passes_1e12=bool(eigenvalue_difference.max()<=1e-12),
        scope='Requested single-thread refit versus archived spectrum. Cost transports retain archived eigenpairs; role rotations use the refit. Eigenvector signs are not compared as numerical errors.')))
    # Every changed numeric leaf in the numerical entries, retaining named lookup paths.
    def compare(old,new,path):
        if isinstance(old,dict) and isinstance(new,dict):
            for k in sorted(old.keys()&new.keys()):
                if k in ('configuration','config','rows','runs','values','checkpoints','diagnostics','parity','paired_legacy','potential','seconds','sampling_seconds','elapsed_seconds'):continue
                compare(old[k],new[k],path+'/'+k)
        elif isinstance(old,(float,int)) and not isinstance(old,bool) and isinstance(new,(float,int)) and old!=new:
            changes.append(dict(entry=path,old=old,new=new))
        elif isinstance(old,(float,int)) and not isinstance(old,bool) and new is None:
            changes.append(dict(entry=path,old=old,new=None))
        elif isinstance(old,list) and isinstance(new,list) and all(isinstance(v,(int,float)) for v in old+new):
            if old!=new:changes.append(dict(entry=path,old=old,new=new))
    for name in ('results.json','ou_hd_results.json','ou_hd_uncoupled_results.json','product_10_results.json','product_50_results.json'):
        before=base['outputs/'+name];after=json.loads((ROOT/'outputs'/name).read_text())
        if name=='results.json':
            # The old A2 entries are legacy-source parity inputs, not manuscript table values.
            before={k:v for k,v in before.items() if not k.startswith('A2_')}
            after={k:v for k,v in after.items() if not k.startswith('A2_')}
        compare(before,after,name)
    primary=json.loads((ROOT/'outputs/results.json').read_text())
    old_nine=base['outputs/results.json']['B_poly9']['poly'];new_nine=primary['B_poly9']['poly']
    changes.insert(0,dict(entry='B_poly9 / Legendre / displayed table statistic',
        old=fmt(old_nine)+f" (mean +/- sample SD; {len(old_nine['rows'])} realisations)",
        new=f"median {fmt(new_nine['median'])}; {new_nine['above_ten_reference_mean']}/10 above ten times the reference mean"))
    for name in ('B_quartic4','B_poly9','A10_beta0.0'):
        old_case=base['outputs/results.json'][name]
        old_fd=old_case.get('fd',old_case.get('fd_rscan',{}).get(str(old_case['r']),{}))
        changes.insert(1,dict(entry=name+' / FD / displayed table statistic',
            old=fmt(old_fd['sw'])+' (one source cloud)',new=fmt(primary[name]['fd'])+' (ten source clouds)'))
    for dimension in (10,50):
        old_product=base[f'outputs/product_{dimension}_results.json']
        new_product=json.loads((ROOT/f'outputs/product_{dimension}_results.json').read_text())
        for method in ('exact','estimated','legendre'):
            changes.insert(1,dict(entry=f'product_{dimension} / {method} / displayed table statistic',
                old=fmt(old_product['methods'][method]['sw'])+' (one source cloud)',
                new=fmt(new_product['methods'][method]['metrics']['sw'])+' (ten source clouds)'))
    for name in ('B_quartic4','B_poly9','A10_beta0.0','A10_beta0.5'):
        for budget,oldrows in base['outputs/results.json'][name]['sample_size'].items():
            compare(summarize(r['sw'] for r in oldrows),summarize(r['sw'] for r in primary[name]['sample_size'][budget]),f'results.json/{name}/sample_size/{budget}')
    for name in ('ou_hd_results.json','ou_hd_uncoupled_results.json'):
        new=json.loads((ROOT/'outputs'/name).read_text())
        for oldrow,newrow in zip(base['outputs/'+name]['time_summary'],new['time_summary']):
            assert oldrow['time']==newrow['time']
            compare(oldrow['metrics'],newrow['metrics'],name+f"/time={oldrow['time']}")
    for study in ('admissible_source','data_comparison'):
        old=base['outputs/'+study+'/summary.json'];new=json.loads((ROOT/'outputs'/study/'summary.json').read_text())
        keys=['beta','method','regime','n_pairs','r_requested','dt'] if study=='admissible_source' else ['beta','method']
        field='groups' if study=='admissible_source' else 'rows'
        lookup={tuple(r.get(k) for k in keys):r for r in old[field]}
        for r in new[field]:
            key=tuple(r.get(k) for k in keys)
            if key in lookup:compare(lookup[key],r,study+'/'+str(dict(zip(keys,key))))
    oldscan=base['outputs/a10_sweep.json']['rows'];newscan=json.loads((ROOT/'outputs/a10_sweep.json').read_text())['rows']
    for r in newscan:
        old=next(o for o in oldscan if (o['dictionary'],o['size'],o['r_requested'])==(r['dictionary'],r['size'],r['r_requested']))
        compare(old,r,'a10_sweep/'+str((r['dictionary'],r['size'],r['r_requested'])))
    timings={p.stem:json.loads(p.read_text()) for p in sorted(OUT.glob('*_execution.json')) if not p.name.startswith('followup_')}
    hardware_path=OUT/'hardware.json'
    hardware=json.loads(hardware_path.read_text(encoding='utf-8-sig')) if hardware_path.exists() else None
    configuration=dict(required_tasks=['B1','B2','B3','B4'],optional_B5_run=False,expected_run_counts=expected,
        synthetic_seed_indices=list(range(10)),training_seed_base=100,source_seed_base=500,independent_coefficient_seed_base=700,
        selection_seed_base=900,selection_samples=100000,target_seed=7,projections=64,projection_seed=0,reference_repetitions=10,
        density_floor=.001,speed_cap=20.,ou10_source_seeds=list(range(700,710)),
        product_seed_indices=list(PRODUCT_SEED_INDICES),product_source_seeds=[1+s for s in PRODUCT_SEED_INDICES],
        product_training_seeds=[1001+s for s in PRODUCT_SEED_INDICES],product_coordinate_workers=8,
        product_excluded_seed_index=6,product_replacement_seed_index=10,
        alanine_degree=28,alanine_rank=256,alanine_cutoff=1e-12,alanine_smoothing=.1,alanine_horizon=8,
        alanine_seeds=[1101,1102,1103],alanine_fit_threads=1,alanine_projection_directions=32,
        alanine_projection_seed=2026,alanine_reference_pairs_per_assignment=3,alanine_rotation_processes=4,quick=False,
        alanine_transport=copy.deepcopy(alanine_specification),
        synthetic_notebook_settings=copy.deepcopy(primary['_config']),
        ou10_protocols={str(c):json.loads((ROOT/'outputs'/name).read_text())['config']
            for c,name in [(0.,'ou_hd_uncoupled_results.json'),(.15,'ou_hd_results.json')]},
        product_protocols={str(d):json.loads((ROOT/f'outputs/product_{d}_results.json').read_text())['config'] for d in (10,50)},
        product_spectral_settings=dict(fd_grid_points=1401,rbf_centres=80,rbf_centre_bounds=[-2.8,2.8],
            rbf_width=.14,whitening_tolerance=1e-10,legendre_degree=32,legendre_chunk=5000,fit_rank_limit=24),
        a2=json.loads((OUT/'a2_config.json').read_text()),comparison=json.loads((ROOT/'outputs/data_comparison/config.json').read_text()))
    write_json(OUT/'configuration.json',configuration)
    verification_path=OUT/'verification.json'
    verification=json.loads(verification_path.read_text()) if verification_path.exists() else None
    retained_alanine_path=OUT/'retained_alanine_verification.json'
    retained_alanine=json.loads(retained_alanine_path.read_text()) if retained_alanine_path.exists() else None
    result=dict(statistics=statistics_rows,b1_pairs=paired,alanine_rows=alanine,alanine_rotations=rotations,alanine_across_pairs=across,alanine_cost_summaries=cost_summaries,alanine_source_controls=controls,
                saved_array_verification=verification,retained_alanine_verification=retained_alanine,
                product_randomness_checks=product_randomness,
                hardware=hardware,configuration=configuration,
                reproduction_checks=parity,reproduction_discrepancies=[r for r in parity if not r['check'].get('passes_1e12',True)],
                manuscript_numbers_old_to_new=changes,execution=timings,
                notes=['B5 was not run.','Rank scans use the first source seed; the four-well Legendre r=32 instability additionally has ten realisations.',
                       'The listed B2 OU extension concerns the 10D experiment. The original 1D rank, time and particle-count curves retain their single-cloud design; B4 adds the requested r=40 path diagnostics.',
                       'Products preserve eight independent coordinate workers and one BLAS thread; their timings are descriptive.',
                       'The product correction excludes index s=6, whose source seed 7 coincided with the fixed target seed. Current summaries use s=0--5,7--10, including the new source seed 11 and training seed 1011. Original index-6 records remain historical audit inputs and are absent from current aggregates. Every active source seed differs from target seed 7; first-coordinate rank-order checks are recorded.',
                       'Independent synthetic repetitions may run in four processes (two for products). The equal-data and alanine cost stages run alone. Concurrent timing records are not sampler-speed comparisons.',
                       'The three alanine spectra are fitted sequentially. After fitting, the eighteen independent role-rotation transports may run in four single-BLAS-thread processes; those transport timings are descriptive.',
                       'The generic 64-direction, seed-0 metric and ten-pair reference rule applies to the synthetic empirical-target tests. Alanine preserves its archived 32 directions (seed 2026) in the four-dimensional periodic embedding and the three paired reference designs; analytic OU uses the Gaussian reference. These existing exceptions were not silently changed.',
                       'Product and rotated-OU safeguards act on one-dimensional factors: their ratio floors are factor-wise, and the reported particle fraction is the union over coordinates.',
                       'Fixed-step notebook transports retain int(round(T/h)) full steps. Requested and effective horizons can therefore differ by at most half a step. In the 10D/50D products, requested T=10.685414859800558 gives 534 steps of h=0.02 and effective time 10.68. The main 2D and equal-data horizons are already rounded to the step grid; adaptive alanine runs target s=8 exactly.',
                       'Product projections occur only at completed steps. Boxed 2D/10D double wells project the trial arguments of RK stages 2--4 and each completed endpoint; stage 1 uses the stored state, and the initial source is not pre-projected. Full-plane multiwells and OU have no such projection.',
                       'The prescribed 10D source retains harmonic-coordinate variance 0.5. At positive coupling its full-space density ratio is unbounded; B1 fixes independence of the selected modes, while this source/domain limitation remains.',
                       'All adaptive RHS evaluations are observed, including rejected and dense-output stages. Torus wrapping is not a boundary projection.',
                       'Safeguard fractions monitor evaluated numerical stages, not exact continuous-time hitting probabilities. Projection counts refer to explicit clipping and do not certify containment in a theoretical admissible region.',
                       'Six ordered trajectory pairs share three fits and three evaluation trajectories; their sample SD is descriptive, not an independent-data standard error.',
                       'Role rotations jointly change the fitted spectrum, training-derived source and basin partition, and evaluation trajectory. Their spread does not isolate spectral estimation error alone.',
                       'The latest manuscript source is not present in this checkout. Numerical changes are indexed by experiment and stored entry; exact section/table placement requires the current manuscript.'])
    if (OUT/'followup_execution.json').exists():
        from revision_followup import build_results
        result['followup']=build_results(data['products'])
        result['manuscript_numbers_old_to_new'].extend(result['followup']['product_old_to_new'])
    write_json(OUT/'summary.json',result)
    return result

def append_revision(lines):
    path=OUT/'summary.json'
    if path.exists():result=json.loads(path.read_text())
    else:
        from manuscript_results import read_json
        try:result=read_json('revision/summary.json')
        except (FileNotFoundError,KeyError):return
    lines+=['','## Revision experiments','','The fixed B1--B4 protocol retains all prescribed realisations, including failures, with the explicitly requested product correction: index 6 is excluded for source/target seed dependence and index 10 replaces it. No outcome-based seed selection or hyperparameter search is used. Complete arrays, configuration snapshots and execution records are archived under `outputs/revision/` in `double_well.zip`; per-realisation numerical records are also published in `outputs/revision_results.json`. All standard deviations below are sample standard deviations.','',
            '### B1. Independent selection of the 10D modes','',
            'Candidates satisfy the original generator/lag disagreement condition. Selection uses 100000 independent source points with seed 900+s. Velocity coefficients remain empirical moments of the transported source (seed 500+s). The table is paired within the original seed; it is not an independent replication. Old denotes the legacy selection rule. The additional Legendre training budgets have newly evaluated legacy-rule baselines; only configurations present in the original archive have archived-scalar reproduction checks. Full selected index sets are in the JSON.']
    table(lines,['System','Dictionary','n','r','Size','Seed','Old SW2','New SW2','Shared modes','Jaccard'],[
        [r['system'],r['method'],r['n_pairs'],r['rank'],r['size'] or 'default',r['seed'],fmt(r['old_sw2']),fmt(r['new_sw2']),r['overlap_count'],fmt(r['jaccard'])] for r in result['b1_pairs']])
    lines+=['### B2. Ten prescribed realisations','','The JSON gives all ten values, mean, sample SD and median for each repeated cell. The nine-well Legendre table entry uses the median and exceedance count; its mean and SD remain in the JSON. Rank scans remain on source seed 0, except for the additional four-well Legendre r=32 repetitions. A single run has no sample SD. Original reference samples, ten-pair reference statistics and projection directions are unchanged.']
    stats=result['statistics']
    selected=[r for r in stats if r['sw2']['n']==10]
    table(lines,['Experiment / configuration','SW2 mean +/- SD','Median','Above 10 x reference mean','Failed/nonfinite'],[
        [configuration_label(r['task'],r['configuration']),
         'Use median / count' if r['configuration'].get('system')=='B_poly9' and r['configuration'].get('method')=='Legendre' else fmt(r['sw2']),
         fmt(r['sw2']['median']),r.get('above_ten_reference_mean','--'),r['sw2']['nonfinite_count']] for r in selected])
    table(lines,['Equal-data configuration','Fit seconds','Sampling seconds','Total seconds'],[
        [configuration_label(r['task'],r['configuration']),fmt(r['fit_seconds']),fmt(r['sample_seconds']),fmt(r['total_seconds'])] for r in stats if r['task']=='comparison'])
    lines+=['### B3. Alanine cost and estimation variability','','All new costs use one BLAS thread. Spectrum fitting includes the Gram and Dirichlet matrices and eigendecomposition for J=3249. BKT/LAWGD cost repetitions reuse the archived eigenpairs while fitting cost is independently re-measured. Initial moments are timed separately. Input generation and metric callbacks are excluded from transport timings. KDE compilation time is recorded separately in its diagnostics and is also excluded from transport timings.']
    ar=result['alanine_rows']
    table(lines,['Estimation','Fit wall seconds','Fit CPU seconds','Threads'],[[r['id'],fmt(r.get('fit_seconds')),fmt(r.get('fit_cpu_seconds')),1] for r in ar if r.get('task') in ('B3a_fit','B3b_fit')])
    table(lines,['Method','Seed','Status','Moments wall / CPU s','Transport wall / CPU s','RHS evaluations','Late SW2 level','First within-band s / wall s'],[
        [r['method'],r['seed'],r['status'],fmt(r.get('coefficient_wall_seconds'))+' / '+fmt(r.get('coefficient_cpu_seconds')),
         fmt(r['wall_seconds'])+' / '+fmt(r['cpu_seconds']),r['events']['nfev'],fmt(r['late_time'].get('late_error')),
         fmt(r['late_time'].get('first_hit_s'))+' / '+fmt(r['late_time'].get('first_hit_wall_seconds'))] for r in ar if r.get('task')=='B3a_cost'])
    lines+=['The late level is the time average of checkpoint SW2 on s in [6,8], computed by the trapezoid rule. The first hit is the first prescribed checkpoint within one reference SD of that method\'s own level. Levels differ between methods, so these hit times are not a common-accuracy comparison.','']
    table(lines,['Method','Transport wall seconds','Transport CPU seconds','First within-band wall seconds'],[
        [r['method'],fmt(r['wall_seconds']),fmt(r['cpu_seconds']),fmt(r['first_hit_wall_seconds'])] for r in result['alanine_cost_summaries']])
    lines+=['Trajectory-pair tables number trajectories 1--3; stored IDs and JSON indices use 0--2.','']
    table(lines,['Fit / evaluation trajectory','lambda1','SW2','Mass TV','Reference SW2','Reference TV','Local-width ratio','Completed'],[
        [f"{r['fit_trajectory']+1} / {r['evaluation_trajectory']+1}",fmt(r['lambda1']),fmt(r['sw2']),fmt(r['mass_tv']),fmt(r['reference_sw2']),fmt(r['reference_mass_tv']),fmt(r['local_width_ratio']),f"{r['completed']}/3"] for r in result['alanine_rotations']])
    table(lines,['Statistic across six ordered pairs','Mean +/- SD'],[[k,fmt(v)] for k,v in result['alanine_across_pairs'].items()])
    lines+=['Terminal statistics across all six pairs require all eighteen requested endpoints; incomplete pairs are not omitted from the aggregation. For an incomplete rotation the JSON endpoint is null, while last_checkpoint_score and last_checkpoint_s retain the available checkpoint. The analogous filtered distance is retained as last_checkpoint_unaffected_sw2; it is not a terminal error.','']
    incomplete=[r for r in ar if r.get('task') in ('B3a_cost','B3b_rotation','B3c_iid') and r['status']!='ok']
    if incomplete:
        table(lines,['Incomplete integration','Last accepted s','Last saved s','RHS evaluations','Reason'],[
            [r['id'],fmt(r.get('completed_s')),fmt(r['checkpoints'][-1]['s']),r['events']['nfev'],r.get('failure')]
            for r in incomplete])
    table(lines,['IID control seed','Status','Last saved s','SW2 at s=8','Mass TV at s=8'],[
        [r['seed'],r['status'],r['checkpoints'][-1]['s'],
         fmt(r['checkpoints'][-1]['sw2'] if r['status']=='ok' and r['checkpoints'][-1]['s']==8 else None),
         fmt(r['checkpoints'][-1]['mass_tv'] if r['status']=='ok' and r['checkpoints'][-1]['s']==8 else None)]
        for r in ar if r.get('task')=='B3c_iid'])
    table(lines,['Source design, original trajectory assignment','SW2 at s=8','Mass TV at s=8'],[
        [name,fmt(values['sw2']),fmt(values['mass_tv'])] for name,values in result['alanine_source_controls'].items()])
    lines+=['### B4. Safeguards per particle path','','A particle is counted once if any evaluated stage meets a safeguard. Product rows also record particle-coordinate fractions in the JSON. Caps apply to the Euclidean velocity norm in coupled transport, and to individual coordinate equations for products and rotated OU. Alanine path diagnostics cover BKT, LAWGD and the retained RBF tests. For empirical targets, the filtered distance renormalizes the unaffected cloud and compares it to the complete original target cloud by exact empirical quantile integration for unequal sample counts. Analytic OU cases retain their original Gaussian-reference metric. It is a conditional diagnostic, not the sampler\'s unconditional accuracy. An empty unaffected cloud has no distance.',
        'For incomplete alanine integrations, mask fractions cover the attempted RHS evaluations, but terminal full/filtered distances are unavailable. Any raw last-checkpoint distance is retained with its checkpoint time and is not substituted for the requested endpoint.']
    table(lines,['Experiment / configuration','Floor','Nonpositive','Speed cap','Projection','Any','Full SW2','Unaffected SW2'],[
        [configuration_label(r['task'],r['configuration']),*[fmt(r['path_diagnostics'].get(k+'_particle_fraction')) for k in ('floor','nonpositive','cap','projection','affected')],fmt(r['sw2']),fmt(r['path_diagnostics']['unaffected_sw2'])] for r in stats if 'path_diagnostics' in r])
    table(lines,['Product configuration: particle-coordinate fractions','Floor','Nonpositive','Speed cap','Projection','Any'],[
        [configuration_label(r['task'],r['configuration']),*[fmt(r['path_diagnostics'].get(k+'_particle_coordinate_fraction')) for k in ('floor','nonpositive','cap','projection','affected')]]
        for r in stats if r['task']=='products'])
    table(lines,['Alanine case','Seed','Status','Floor','Nonpositive','Speed cap','Projection','Any','Full cloud SW2','Unaffected SW2'],[
        [r['id'],r['seed'],r['status'],*[fmt((r.get('diagnostics') or r.get('events',{})).get(k+'_particle_fraction')) for k in ('floor','nonpositive','cap','projection','affected')],
         fmt(r['checkpoints'][-1]['sw2'] if r['status']=='ok' and r.get('checkpoints') else None),
         fmt((r.get('diagnostics') or r.get('events',{})).get('unaffected_sw2') if r['status']=='ok' else None)]
        for r in ar if ('diagnostics' in r or 'affected_particle_fraction' in r.get('events',{}))])
    lines+=['### Reproduction and protocol notes','',f"{len(result['reproduction_checks'])} endpoint/scalar checks were recorded; {len(result['reproduction_discrepancies'])} did not satisfy the requested reproduction check (tolerance 1e-12, with missing completed endpoints also flagged). B1 deliberately changes the mode set; its new endpoint is not expected to equal the legacy endpoint."]
    if result.get('saved_array_verification'):
        verified=result['saved_array_verification']
        lines+=['',f"The separate saved-array audit recomputed {sum(r['checked_endpoint_distances'] for r in verified['tasks'])} endpoint distances and checked {verified['checked_masks']} masks, including their unions and reported fractions. The maximum absolute difference in the full or filtered distances was {verified['max_absolute_metric_difference']:.3g}."]
    if result.get('retained_alanine_verification'):
        retained=result['retained_alanine_verification']['convergence']
        lines+=['',f"The unchanged alanine figure data were separately verified at all {retained['checkpoints']} stored checkpoints over {retained['runs']} curves; the maximum saved-metric difference was {retained['maximum_metric_error']:.3g}. Their stored and current numerical-code fingerprints are reported separately because the B4 observations change the source code. Solver reproduction is covered by the checks above."]
    if result.get('hardware'):
        hardware=result['hardware'];processor=hardware['processor']
        lines+=['',f"Hardware: {processor['Name']}, {processor['NumberOfCores']} physical cores, {processor['NumberOfLogicalProcessors']} logical processors, {hardware['memory']['TotalPhysicalMemory']/1024**3:.1f} GiB RAM. All numerical stages use one BLAS thread. Products retain eight coordinate workers per repetition. The queue may run four independent synthetic repetitions or two product repetitions concurrently; the equal-data comparison and alanine cost measurements run alone. Concurrent timings are descriptive. Stage wall times include the task's input/metric work but exclude the final archive repacking. Only the dedicated equal-data and alanine cost runs give freshly measured sampler costs; other elapsed fields may include cache access."]
    if result['reproduction_discrepancies']:table(lines,['Task','Run','Check'],[[r['task'],r['id'],str(r['check'])] for r in result['reproduction_discrepancies']])
    lines+=['',*['- '+v for v in result['notes']], '',
        'Double-well and multiwell repetitions use training seed 100+s and source seed 500+s, with target seed 7 fixed. Exceptions are analytic FD (no learned trajectory), analytic OU (source seeds 700--709 in 10D), separable products (training 1001+s, source 1+s), matched OU paths (its retained SeedSequence convention), and alanine (the explicitly recorded MD assignments and designs). Thus the blanket seed statement does not apply to every experiment.']
    labels={'a10_execution':'B1/B2/B4: 10D double wells','a2_execution':'B2/B4: 2D double wells',
            'multi_execution':'B2/B4: four and nine wells','ou_execution':'B2/B4: OU',
            'comparison_execution':'B2: equal-data comparison','product10_execution':'B2/B4: 10D product',
            'product50_execution':'B2/B4: 50D product','alanine_cost_execution':'B3(a)/B4: alanine costs',
            'alanine_variability_execution':'B3(b)/B4: trajectory rotations','alanine_iid_execution':'B3(c)/B4: iid control',
            'alanine_rbf_execution':'B4: retained alanine RBF cases'}
    table(lines,['Task execution','Wall seconds'],[[labels.get(k,k),fmt(v['wall_seconds'])] for k,v in result['execution'].items()])
    lines+=['Shared numerical work is timed once under its joint task label. B1, B2 and B4 use some of the same transports, so their execution times cannot be added as independent costs. Cache-only resumes retain the original measured work and are listed separately in the execution history.','']
    if result.get('followup'):
        from revision_followup import append_report
        append_report(lines,result['followup'])
    lines+=['### Manuscript numbers: old -> new','','Entries identify the exact stored numerical quantity. All repeated table values, sample-size summaries, coefficient comparisons, costs, threshold counts, product diagnostics, OU time summaries and the 10D dictionary/rank scan must be taken from the updated report/JSON. Entries beginning with Product seed correction compare the previous group-B ten-realisation result with the corrected ten-realisation result; other entries compare the original pre-revision baseline with the current result. The latest manuscript source was not available in this checkout for a literal cross-reference audit.']
    table(lines,['Numerical entry','Old','New'],[[r['entry'],fmt(r['old']),fmt(r['new'])] for r in result['manuscript_numbers_old_to_new']])

"""Revision statistics, reproduction audit and the single manuscript report section."""
from __future__ import annotations
import copy,json,statistics
from collections import defaultdict
import numpy as np
from revision_common import ROOT,OUT,current_records,write_json,summarize,load_run,PRODUCT_SEED_INDICES

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
           'A10_beta0.0':'10D double well product, beta=0',
           'product10':'10D double-well product','product50':'50D double-well product','OU1':'1D OU','OU10':'10D OU'}
    name=names.get(c.get('system'),'2D double well' if task in ('a2','comparison') else task)
    parts=[name]
    if c.get('beta') is not None:parts.append('beta='+fmt(c['beta']))
    if c.get('coupling') is not None:parts.append('gamma='+fmt(c['coupling']))
    if c.get('method') is not None:
        parts.append({'RBF':'Koopman (RBF)','Legendre':'Koopman (Legendre)','A':'BKT','D':'KDE flow'}.get(c['method'],c['method']))
    for field,label in [('regime','regime'),('n_pairs','n'),('r_requested','r'),('rank','r'),('dt','h')]:
        if c.get(field) is not None:parts.append(label+'='+fmt(c[field]))
    if c.get('dictionary_size_parameter') is not None:
        parts.append(('centres per coordinate=' if c['method']=='RBF' else 'degree=')+fmt(c['dictionary_size_parameter']))
    return '; '.join(parts)

def build_revision_results(data):
    base=current_records();statistics_rows=[]
    expected=dict(a2=320,a10=70,multi=134,products=60,comparison=40,alanine=20,
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
    product_randomness=[]
    for dimension in (10,50):
        for seed in PRODUCT_SEED_INDICES:
            row,arrays=load_run('products',f'product{dimension}_exact_seed{seed}')
            source,target=arrays['source_x1'],arrays['target_x1']
            same_order=bool(np.array_equal(np.argsort(source),np.argsort(target)))
            assert not same_order
            product_randomness.append(dict(dimension=dimension,seed_index=seed,
                included_in_current_summary=seed in PRODUCT_SEED_INDICES,
                source_seed=row['source_seed'],target_seed=row['target_seed'],
                first_coordinate_rank_order_identical=same_order,
                scope='Both coordinate samplers invert their CDFs using M consecutive uniform draws. All ten source seeds differ from the target seed.'))
    alanine=data['alanine'];rotations=[];cost_summaries=[]
    required={f'rotation_fit{i}_eval{j}_seed{s}' for i in (0,) for j in (1,2) for s in (1101,1102,1103)}
    assert required<={r['id'] for r in alanine},'Missing fixed-fit alanine evaluations'
    assert {f'cost_{m}_seed{s}' for m in ('BKT','LAWGD','KDE') for s in (1101,1102,1103)}<={r['id'] for r in alanine}
    assert {f'iid_seed{s}' for s in (1101,1102,1103)}<={r['id'] for r in alanine}
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
    controls={}
    for design,part in [('iid',[r for r in alanine if r.get('task')=='B3c_iid']),
                        ('sobol',[r for r in alanine if r.get('task')=='B3a_cost' and r['method']=='BKT'])]:
        controls[design]={key:summarize(r['checkpoints'][-1][key] if r['status']=='ok' and r['checkpoints'][-1]['s']==8 else None for r in sorted(part,key=lambda r:r['seed']))
                          for key in ('sw2','mass_tv')}
    from alanine_convergence import SPEC as alanine_specification
    primary=json.loads((ROOT/'outputs/results.json').read_text())
    hardware_path=OUT/'hardware.json'
    hardware=json.loads(hardware_path.read_text(encoding='utf-8-sig')) if hardware_path.exists() else None
    configuration=dict(expected_run_counts=expected,
        synthetic_seed_indices=list(range(10)),training_seed_base=100,source_seed_base=500,independent_coefficient_seed_base=700,
        selection_seed_base=900,selection_samples=100000,target_seed=7,projections=64,projection_seed=0,reference_repetitions=10,
        density_floor=.001,speed_cap=20.,ou10_source_seeds=list(range(700,710)),
        product_seed_indices=list(PRODUCT_SEED_INDICES),product_source_seeds=[1+s for s in PRODUCT_SEED_INDICES],
        product_training_seeds=[1001+s for s in PRODUCT_SEED_INDICES],product_coordinate_workers=8,
        alanine_degree=28,alanine_rank=256,alanine_cutoff=1e-12,alanine_smoothing=.1,alanine_horizon=8,
        alanine_seeds=[1101,1102,1103],alanine_fit_threads=1,alanine_projection_directions=32,
        alanine_projection_seed=2026,alanine_reference_pairs_per_assignment=3,alanine_fit_trajectory=0,alanine_evaluation_trajectories=[1,2],quick=False,
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
    result=dict(statistics=statistics_rows,alanine_rows=alanine,alanine_rotations=rotations,alanine_cost_summaries=cost_summaries,alanine_source_controls=controls,
                saved_array_verification=verification,
                product_randomness_checks=product_randomness,
                hardware=hardware,configuration=configuration,
                notes=['Rank scans use the first source seed; the four-well Legendre r=32 instability additionally has ten realisations.',
                       'The 10D OU experiment uses ten source clouds. The 1D rank, time and particle-count curves use a single-cloud design; r=40 has path diagnostics.',
                       'Products preserve eight independent coordinate workers and one BLAS thread; their timings are descriptive.',
                       'Independent synthetic repetitions may run in four processes (two for products). The equal-data and alanine cost stages run alone. Concurrent timing records are not sampler-speed comparisons.',
                       'The 64-direction, seed-0 metric and ten-pair reference rule applies to the synthetic empirical-target tests. Alanine uses 32 directions (seed 2026) in the four-dimensional periodic embedding and three paired reference designs; analytic OU uses the Gaussian reference.',
                       'Product and rotated-OU safeguards act on one-dimensional factors: their ratio floors are factor-wise, and the reported particle fraction is the union over coordinates.',
                       'Fixed-step notebook transports retain int(round(T/h)) full steps. Requested and effective horizons can therefore differ by at most half a step. In the 10D/50D products, requested T=10.685414859800558 gives 534 steps of h=0.02 and effective time 10.68. The main 2D and equal-data horizons are already rounded to the step grid; adaptive alanine runs target s=8 exactly.',
                       'Product projections occur only at completed steps. Boxed 2D/10D double wells project the trial arguments of RK stages 2--4 and each completed endpoint; stage 1 uses the stored state, and the initial source is not pre-projected. Full-plane multiwells and OU have no such projection.',
                       'The uncoupled 10D source has stationary harmonic-coordinate variance 0.5. Mode selection uses an independent source cloud. Box projection remains a separate numerical approximation.',
                       'All adaptive RHS evaluations are observed, including rejected and dense-output stages. Torus wrapping is not a boundary projection.',
                       'Safeguard fractions monitor evaluated numerical stages, not exact continuous-time hitting probabilities. Projection counts refer to explicit clipping and do not certify containment in a theoretical admissible region.',
                       'All prescribed realisations within each retained configuration are included.'])
    from experiment_records import selected_summary
    result=selected_summary(result)
    write_json(OUT/'summary.json',result)
    return result

def append_revision(lines):
    from manuscript_results import read_json
    result=read_json('revision/summary.json')
    lines += ['', '## Fixed-configuration details', '',
        'The reported configurations retain every prescribed source realisation. Alanine uses trajectory 1 for spectrum fitting and source construction; all three seeds are retained. Its results are conditional on this fixed fit and do not establish robustness across estimation trajectories.', '',
        '### Alanine fitting and transport costs', '',
        'Costs use one BLAS thread and exclude input generation and metric callbacks. Spectrum fitting includes the Gram and Dirichlet matrices and eigendecomposition. Initial moments are evaluated separately.']
    rows=result['alanine_rows']
    table(lines,['Estimation','Wall seconds','CPU seconds'],[
        [r['id'],fmt(r.get('fit_seconds')),fmt(r.get('fit_cpu_seconds'))] for r in rows if r.get('task')=='B3a_fit'])
    table(lines,['Method','Transport wall seconds','Transport CPU seconds'],[
        [r['method'],fmt(r['wall_seconds']),fmt(r['cpu_seconds'])] for r in result['alanine_cost_summaries']])
    lines += ['', '### Fixed-fit evaluation', '',
        'Trajectory numbers in this table are 1-based. Both evaluations share the spectrum and source constructed from trajectory 1. Each entry includes seeds 1101, 1102 and 1103; standard deviations describe these paired designs, not independent spectrum estimates.']
    table(lines,['Fit / evaluation trajectory','SW2','Mass TV','Reference SW2','Reference TV','Local-width ratio'],[
        [f"{r['fit_trajectory']+1} / {r['evaluation_trajectory']+1}",fmt(r['sw2']),fmt(r['mass_tv']),fmt(r['reference_sw2']),fmt(r['reference_mass_tv']),fmt(r['local_width_ratio'])]
        for r in result['alanine_rotations']])
    table(lines,['Source design','SW2 at s=8','Mass TV at s=8'],[
        [name,fmt(v['sw2']),fmt(v['mass_tv'])] for name,v in result['alanine_source_controls'].items()])
    lines += ['', '### Numerical safeguards', '',
        'The synthetic ratio floor is 0.001 and speed cap is 20. Box projection acts as described in each protocol. Alanine masks count particles meeting a safeguard at any attempted adaptive RHS evaluation, including rejected stages; torus wrapping is not box projection. Per-realisation masks and numerical records are retained in the data archives.']
    table(lines,['Method','Seed','Floor fraction','Speed-cap fraction'],[
        [r['method'],r['seed'],fmt(r['events'].get('floor_particle_fraction')),fmt(r['events'].get('cap_particle_fraction'))]
        for r in rows if r.get('task')=='B3a_cost' and r['method'] in ('BKT','LAWGD')])
    verified=result.get('saved_array_verification')
    if verified:
        lines += ['',f"Saved-array verification recomputed {sum(r['checked_endpoint_distances'] for r in verified['tasks'])} endpoint distances and checked {verified['checked_masks']} particle masks. Maximum metric discrepancy: {verified['max_absolute_metric_difference']:.3g}. This checks stored metrics, not bitwise reproduction of a newly fitted spectrum."]

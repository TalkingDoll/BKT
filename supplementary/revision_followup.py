"""Fixed group-B follow-up: product seed correction and alanine budget test.

Three distinct fit-2 transports are run once, then evaluated against both
held-out trajectories. The original rotations and excluded product records
remain immutable audit inputs. No optional confined multiwell test is run.
"""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):os.environ[key]='1'
import argparse,copy,hashlib,json,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from revision_common import ROOT,OUT,write_json,save_run,load_run,array_sha,summarize,PRODUCT_SEED_INDICES
import revision_alanine as ra

FOLDER='followup_alanine'
GRID_SIZE=512
FACTOR=5

def original_stop(row):
    if row['status']=='ok':return 'completed'
    if row['events']['nfev']>=ra.ac.SPEC['maximum_evaluations']:return 'evaluation_budget'
    if row['wall_seconds']>=ra.ac.SPEC['maximum_seconds']:return 'time_budget'
    if row.get('failure')==ra.ac.DOP853.TOO_SMALL_STEP:return 'step_size_underflow'
    return 'other_solver_failure'

def frozen_fit(index,evaluation):
    trajectories=ra.full_trajectories();original,dic=ra.ac.inputs()
    fit,arrays=load_run('alanine',f'spectrum_fit{index}')
    assert array_sha(trajectories[index])==fit['train_sha256']
    data=ra.design(trajectories[index],trajectories[evaluation],arrays['lam'],arrays['basis'],original['record']['setting'])
    return trajectories,data,dic,fit

def wrapped_gaussian_grid(points,mean,cov):
    precision=np.linalg.inv(cov);normalization=2*np.pi*np.sqrt(np.linalg.det(cov))
    result=np.zeros(len(points))
    for i in range(-3,4):
        for j in range(-3,4):
            delta=points-mean+2*np.pi*np.array([i,j])
            result+=np.exp(-.5*np.einsum('ni,ij,nj->n',delta,precision,delta))/normalization
    return result

def diagnose():
    started=time.perf_counter();axis=-np.pi+2*np.pi*np.arange(GRID_SIZE)/GRID_SIZE
    points=np.stack(np.meshgrid(axis,axis,indexing='ij'),-1).reshape(-1,2);area=(2*np.pi/GRID_SIZE)**2
    results=[];new_fits=0
    for fit_index in range(3):
        identity=f'fit{fit_index}_diagnostics';saved=load_run(FOLDER,identity)
        if saved:results.append(saved[0]);continue
        evaluations=[i for i in range(3) if i!=fit_index]
        trajectories,data,dic,fit=frozen_fit(fit_index,evaluations[0])
        labels,centers,k=ra.ae.partition(None,centers=data['cluster_centers'])
        small=trajectories[fit_index][np.linspace(0,249999,25000,dtype=int)]
        train_mass=ra.ae.masses(small,labels,k);selected=int(np.argmax(train_mass))
        center_angles=np.arctan2(centers[:,2:],centers[:,:2])
        source_density=wrapped_gaussian_grid(points,data['source_mean'],data['source_covariance'])
        source_normalization=float(source_density.sum()*area)
        assert abs(source_normalization-1)<1e-10
        source_probability=source_density*area/source_normalization
        target_fit=ra.ab.fit_target(trajectories[fit_index],grid_size=GRID_SIZE,smoothing=.1)
        target_probability=target_fit['density'].ravel()*area
        assert abs(target_probability.sum()-1)<1e-12
        arrays=dict(axis=axis,source_grid_probability=source_probability.reshape(GRID_SIZE,GRID_SIZE),
                    target_grid_probability=target_probability.reshape(GRID_SIZE,GRID_SIZE),cluster_centers=centers)
        seed_rows=[]
        for i,seed in enumerate(ra.SEEDS):
            source=data['source'][i];basis=np.ascontiguousarray(data['basis'][:,:256])
            initial=ra.ac.mean_features(dic,ra.ac.geometry(dic,source))@basis
            coef=basis@initial
            values=[]
            for start in range(0,len(points),4096):
                values.append(ra.ac.contract(dic,coef,ra.ac.geometry(dic,points[start:start+4096]))[0])
            rho=np.concatenate(values);low=rho<=ra.ac.SPEC['bkt_ratio_floor']
            rho_source=ra.ac.contract(dic,coef,ra.ac.geometry(dic,source))[0]
            old,oldarrays=load_run('alanine',f'rotation_fit{fit_index}_eval{evaluations[0]}_seed{seed}')
            assert array_sha(source)==old['source_sha256']
            assert array_sha(initial)==old['initial_empirical_moments_sha256']
            outcomes=[]
            for evaluation in evaluations:
                row,a=load_run('alanine',f'rotation_fit{fit_index}_eval{evaluation}_seed{seed}')
                assert row['source_sha256']==old['source_sha256']
                assert row['events']['nfev']==old['events']['nfev']
                assert np.array_equal(a['clouds'],oldarrays['clouds'])
                for name in ('floor','cap'):assert np.array_equal(a['mask_'+name],oldarrays['mask_'+name])
                last=row['last_checkpoint_score'];width=ra.ae.thickness(a['target'])
                outcomes.append(dict(evaluation_trajectory=evaluation,endpoint=row['endpoint'],
                    last_checkpoint_s=row['last_checkpoint_s'],last_checkpoint_score=last,
                    initial_local_width_ratio=ra.ae.thickness(source)/width))
            seed_rows.append(dict(seed=seed,source_sha256=array_sha(source),initial_moments_sha256=array_sha(initial),
                grid_minimum=float(rho.min()),grid_minimum_angles=points[np.argmin(rho)],
                grid_source_mass_below_threshold=float(source_probability[low].sum()),
                grid_target_mass_below_threshold=float(target_probability[low].sum()),
                grid_area_fraction_below_threshold=float(low.mean()),
                source_particle_fraction_below_threshold=float(np.mean(rho_source<=.001)),
                source_particle_minimum=float(rho_source.min()),source_basin_masses=ra.ae.masses(source,labels,k),
                status=old['status'],termination_reason=original_stop(old),s_reached=old['completed_s'],
                nfev=old['events']['nfev'],floor_particle_fraction=old['events']['floor_particle_fraction'],
                cap_particle_fraction=old['events']['cap_particle_fraction'],evaluations=outcomes))
            arrays[f'ratio_seed{seed}']=rho.reshape(GRID_SIZE,GRID_SIZE)
        row=dict(id=identity,fit_trajectory=fit_index,lambda1_to_lambda5=data['lam'][:5],
            retained_gram_rank=fit['gram_kept'],gram_rank_definition='Rank of the centered nonconstant Gram matrix after relative cutoff 1e-12; the constant is separate.',
            source_mean=data['source_mean'],source_covariance=data['source_covariance'],
            selected_basin=selected,mean_basin=int(labels(data['source_mean'][None])[0]),
            basin_center_angles=center_angles,basin_training_masses=train_mass,
            source_mean_degrees=np.degrees(data['source_mean']),
            basin_label_scope='Four fit-specific k-means regions in the periodic embedding; labels are not physical conformer assignments and are not aligned across fits.',
            grid_size=GRID_SIZE,grid_spacing=2*np.pi/GRID_SIZE,source_grid_normalization=source_normalization,
            mass_definition='Region rho_hat_0 <= 1e-3. Source mass uses the analytic wrapped Gaussian (image shifts -3..3); target mass uses the unchanged 0.1-rad smoothed training marginal on the periodic grid. Both are grid estimates, not certified bounds; area fraction is distinct.',
            target_grid_estimator=target_fit['metadata'],seeds=seed_rows,threads=1)
        save_run(FOLDER,identity,row,arrays);results.append(row);new_fits+=1
        print('DIAGNOSED FIT',fit_index,'lambda',data['lam'][:5].tolist(),'source masses',[v['grid_source_mass_below_threshold'] for v in seed_rows],flush=True)
    write_json(OUT/'followup_diagnostics.json',results)
    if new_fits or not (OUT/'followup_diagnostics_execution.json').exists():
        write_json(OUT/'followup_diagnostics_execution.json',dict(wall_seconds=time.perf_counter()-started,new_fits=new_fits,threadpools=threadpool_info()))

def retry(seed):
    identity=f'fit2_budget5_seed{seed}'
    if load_run(FOLDER,identity):print('REUSE',identity,flush=True);return
    started=time.perf_counter();trajectories,data,dic,fit=frozen_fit(2,0)
    limits={key:FACTOR*ra.ac.SPEC[key] for key in ('maximum_seconds','maximum_evaluations')}
    extra={};row,clouds=ra.ac.transport(data,dic,256,'BKT',seed,budgets=limits,diagnostics=extra)
    i=ra.SEEDS.index(seed);masks=ra.attach(row,clouds,data['target'][i])
    evaluations=[];last=extra['last_accepted_state'];arrays=dict(clouds=clouds,last_accepted_state=last,**masks)
    for evaluation in (0,1):
        d=ra.design(trajectories[2],trajectories[evaluation],data['lam'],data['basis'],data['record']['setting'])
        assert np.array_equal(d['source'],data['source'])
        target=d['target'][i];labels,_,k=ra.ae.partition(None,centers=d['cluster_centers']);width=ra.ae.thickness(target)
        completed=row['status']=='ok' and row['checkpoints'][-1]['s']==8
        evaluations.append(dict(evaluation_trajectory=evaluation,
            endpoint=ra.ae.score(clouds[-1],target,labels,k,width) if completed else None,
            last_accepted_score=ra.ae.score(last,target,labels,k,width),
            last_checkpoint_score=ra.ae.score(clouds[-1],target,labels,k,width),
            reference=ra.ac.metrics(d['reference_a'][i],d['reference_b'][i],d['cluster_centers'])))
        arrays[f'target_eval{evaluation}']=target
    old,oldarrays=load_run('alanine',f'rotation_fit2_eval0_seed{seed}')
    assert row['source_sha256']==old['source_sha256']
    assert row['initial_empirical_moments_sha256']==old['initial_empirical_moments_sha256']
    assert np.array_equal(clouds[:len(oldarrays['clouds'])],oldarrays['clouds'])
    assert all(np.all(~oldarrays['mask_'+name]|masks['mask_'+name]) for name in ('floor','cap','affected'))
    row.update(id=identity,task='B3_followup_budget5',fit_trajectory=2,budget_multiplier=FACTOR,
        original_resource_budgets={key:ra.ac.SPEC[key] for key in limits},
        unchanged_transport_settings={key:ra.ac.SPEC[key] for key in ('rtol','atol','max_step','first_step_raw','raw_bkt_speed_cap','bkt_ratio_floor')},
        lambda1=fit['lambda1'],last_checkpoint_s=row['checkpoints'][-1]['s'],
        requested_endpoint_available=row['status']=='ok' and row['checkpoints'][-1]['s']==8,evaluations=evaluations,
        last_accepted_state_sha256=array_sha(last),original_checkpoints_bitwise_equal=True,
        original_path_masks_are_subsets=True,threads=1)
    if not row['requested_endpoint_available']:
        row['events']['last_checkpoint_unaffected_sw2']=row['events']['unaffected_sw2'];row['events']['unaffected_sw2']=None
    save_run(FOLDER,identity,row,arrays)
    print('RETRY FINISHED',identity,row['status'],row['termination_reason'],row['completed_s'],row['events']['nfev'],flush=True)
    write_json(OUT/f'followup_retry_{seed}_execution.json',dict(wall_seconds=time.perf_counter()-started,threadpools=threadpool_info()))

def run():
    from experiment_store import managed_outputs
    with managed_outputs('double_well','ou','alanine'),threadpool_limits(limits=1):
        execution_path=OUT/'followup_execution.json'
        if execution_path.exists():
            previous=json.loads(execution_path.read_text())
            if previous.get('complete') and all(r['exit_code']==0 for r in previous['jobs']):
                expected=[('products',f'product{d}_{name}_seed10') for d in (10,50) for name in ('exact','estimated','legendre')]
                expected += [(FOLDER,f'fit2_budget5_seed{s}') for s in ra.SEEDS]
                expected += [(FOLDER,f'fit{i}_diagnostics') for i in range(3)]
                if not all(load_run(folder,identity) is not None for folder,identity in expected):
                    raise ValueError('Completed follow-up manifest has missing result records')
                print('REUSE completed follow-up; original execution measurements retained.',flush=True)
                return
        snapshot=OUT/'followup_baseline.json'
        if not snapshot.exists():
            write_json(snapshot,dict(summary=json.loads((OUT/'summary.json').read_text()),
                products={str(d):json.loads((ROOT/f'outputs/product_{d}_results.json').read_text()) for d in (10,50)},
                prior_pdf_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'outputs/figures').glob('*.pdf')},
                original_product_rows=json.loads((OUT/'products_runs.json').read_text()),
                original_alanine_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'alanine').glob('*.npz')}))
        baseline=ROOT/'followup_repository_baseline.json'
        if baseline.exists():baseline.replace(OUT/'followup_repository_baseline.json')
        write_json(OUT/'followup_config.json',dict(product_seed_indices=PRODUCT_SEED_INDICES,excluded_product_seed_index=6,
            source_seeds=[1+s for s in PRODUCT_SEED_INDICES],training_seeds=[1001+s for s in PRODUCT_SEED_INDICES],target_seed=7,
            retained_previous_product_indices=[s for s in PRODUCT_SEED_INDICES if s!=10],
            alanine_budget_multiplier=FACTOR,alanine_original_budgets={k:ra.ac.SPEC[k] for k in ('maximum_seconds','maximum_evaluations')},
            alanine_new_budgets={k:FACTOR*ra.ac.SPEC[k] for k in ('maximum_seconds','maximum_evaluations')},
            diagnostic_grid_size=GRID_SIZE,optional_confined_multiwells_run=False,threads_per_blas=1,
            scheduling='Five independent processes: two product runs with eight coordinate workers each, and three alanine transports with one BLAS thread each. Elapsed times are descriptive.'))
        diagnose()
        jobs=[(f'product{d}',ROOT/'supplementary/revision_products.py',[str(d),'--seed-index','10']) for d in (10,50)]
        jobs += [(f'retry{seed}',Path(__file__),['retry','--seed',str(seed)]) for seed in ra.SEEDS]
        def execute(name,script,args):
            start=time.perf_counter();log=OUT/f'followup_{name}.log'
            with log.open('a',encoding='utf-8') as stream:
                result=subprocess.run([sys.executable,'-u','-B',str(script),*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
            row=dict(job=name,exit_code=result.returncode,wall_seconds=time.perf_counter()-start,log=log.name)
            print('FOLLOWUP JOB',json.dumps(row),flush=True);return row
        start=time.perf_counter();records=[]
        with ThreadPoolExecutor(max_workers=5) as pool:
            for future in as_completed([pool.submit(execute,*job) for job in jobs]):
                records.append(future.result());write_json(OUT/'followup_execution.json',dict(jobs=records,wall_seconds=time.perf_counter()-start,complete=len(records)==5))
        if any(r['exit_code'] for r in records):raise RuntimeError('A follow-up process failed; saved records are retained')
    print('FOLLOWUP COMPUTATION FINISHED',flush=True)

def build_results(products):
    """Verify the saved follow-up, then construct publication records."""
    from revision_verify import verify_masks
    baseline=json.loads((OUT/'followup_baseline.json').read_text())
    config=json.loads((OUT/'followup_config.json').read_text())
    execution=json.loads((OUT/'followup_execution.json').read_text())
    assert execution['complete'] and len(execution['jobs'])==5
    assert all(r['exit_code']==0 for r in execution['jobs'])
    for name,sha in baseline['original_alanine_sha256'].items():
        assert hashlib.sha256((OUT/'alanine'/name).read_bytes()).hexdigest()==sha,name
    old_by_id={r['id']:r for r in baseline['original_product_rows']}
    for row in products:
        assert row['seed'] in PRODUCT_SEED_INDICES and row['source_seed']!=row['target_seed']
        if row['seed']!=10:assert row==old_by_id[row['id']],row['id']
    excluded=[r for r in baseline['original_product_rows'] if r['seed']==6]
    assert len(excluded)==6
    product_tables=[];changes=[]
    for d in (10,50):
        current=json.loads((ROOT/f'outputs/product_{d}_results.json').read_text())
        previous=baseline['products'][str(d)]
        assert current['reference']==previous['reference']
        for method,label in [('exact','FD'),('estimated','Koopman (RBF)'),('legendre','Koopman (Legendre)')]:
            before=previous['methods'][method]['metrics'];after=current['methods'][method]['metrics']
            part=sorted([r for r in products if r['dimension']==d and r['method']=={'exact':'FD','estimated':'RBF','legendre':'Legendre'}[method]],key=lambda r:r['seed'])
            assert [r['seed'] for r in part]==list(PRODUCT_SEED_INDICES)
            assert len({r['target_sha256'] for r in part})==1
            new=next(r for r in part if r['seed']==10)
            assert (new['source_seed'],new['training_seed'],new['target_seed'])==(11,1011,7)
            product_tables.append(dict(dimension=d,method=label,seeds=list(PRODUCT_SEED_INDICES),
                old=before['sw'],new=after['sw'],reference=current['reference']['metrics']['sw'],
                removed_sw2=next(r['sw2'] for r in excluded if r['dimension']==d and r['method']==new['method']),
                added_sw2=new['sw2']))
            for metric in before:
                for statistic in ('mean','std','median'):
                    a,b=before[metric].get(statistic),after[metric].get(statistic)
                    if isinstance(a,(int,float)) and isinstance(b,(int,float)) and a!=b:
                        changes.append(dict(entry=f'Product seed correction / {d}D / {label} / {metric} / {statistic}',old=a,new=b))
    fits=json.loads((OUT/'followup_diagnostics.json').read_text());retries=[];mask_count=0;maximum=0.
    assert [r['fit_trajectory'] for r in fits]==[0,1,2]
    for fit in fits:
        _,arrays=load_run(FOLDER,fit['id'])
        for seed in fit['seeds']:
            rho=arrays[f"ratio_seed{seed['seed']}"];low=rho<=.001
            assert rho.shape==(GRID_SIZE,GRID_SIZE)
            measured=dict(grid_minimum=float(rho.min()),grid_area_fraction_below_threshold=float(low.mean()),
                grid_source_mass_below_threshold=float(arrays['source_grid_probability'][low].sum()),
                grid_target_mass_below_threshold=float(arrays['target_grid_probability'][low].sum()))
            for key,value in measured.items():
                error=abs(value-seed[key]);maximum=max(maximum,error);assert error<=1e-12,(fit['id'],seed['seed'],key)
    _,data,_,_=frozen_fit(2,0);labels,_,k=ra.ae.partition(None,centers=data['cluster_centers'])
    for seed in ra.SEEDS:
        row,arrays=load_run(FOLDER,f'fit2_budget5_seed{seed}')
        assert row['budget_multiplier']==5
        assert row['resource_budgets']==config['alanine_new_budgets']
        for key,value in row['unchanged_transport_settings'].items():assert value==ra.ac.SPEC[key],key
        assert row['last_accepted_state_sha256']==array_sha(arrays['last_accepted_state'])
        original,oldarrays=load_run('alanine',f'rotation_fit2_eval0_seed{seed}')
        assert np.array_equal(arrays['clouds'][:len(oldarrays['clouds'])],oldarrays['clouds'])
        for name in ('floor','cap','affected'):assert np.all(~oldarrays['mask_'+name]|arrays['mask_'+name])
        mask_count+=verify_masks(row,arrays)
        for result in row['evaluations']:
            target=arrays[f"target_eval{result['evaluation_trajectory']}"];width=ra.ae.thickness(target)
            for key,cloud in [('last_accepted_score',arrays['last_accepted_state']),('last_checkpoint_score',arrays['clouds'][-1])]:
                measured=ra.ae.score(cloud,target,labels,k,width)
                for metric in ('sw2','mass_tv','local_width_ratio'):
                    error=abs(measured[metric]-result[key][metric]);maximum=max(maximum,error)
                    assert error<=1e-12,(row['id'],key,metric)
            if row['requested_endpoint_available']:
                assert result['endpoint']==result['last_checkpoint_score'] and row['last_checkpoint_s']==8
            else:assert result['endpoint'] is None
        retries.append(row)
    result=dict(configuration=config,products=product_tables,product_old_to_new=changes,
        excluded_historical_product_rows=excluded,alanine_fits=fits,alanine_budget5=retries,
        verification=dict(original_alanine_files_unchanged=len(baseline['original_alanine_sha256']),
            original_product_rows_unchanged=54,checked_new_masks=mask_count,
            maximum_diagnostic_difference=maximum,initial_sources_and_moments_unchanged=True,
            original_saved_checkpoints_bitwise_equal=True,original_masks_subsets_of_extended_masks=True),
        execution=execution,
        interpretation='Three distinct third-trajectory integrations, each evaluated against both other trajectories. No extra fit, source, spectrum, solver setting or trial is selected. An incomplete path has no SW2 or TV at s=8. Grid masses and minima are discrete diagnostics, not certified bounds.')
    write_json(OUT/'followup_summary.json',result)
    return result


def append_report(lines,result):
    from revision_report import table,fmt
    lines+=['','## Group-B follow-up','','The optional confined four- and nine-well runs were not performed. All unconfined multiwell results remain unchanged. This follow-up corrects the product seed dependence and diagnoses the three distinct integrations fitted on trajectory 3. Trajectories are numbered 1--3 here; JSON indices remain 0--2.','',
        '### Product seed correction','',
        'Current indices are s=0--5,7--10, with source seed 1+s and training seed 1001+s. Index 6 is excluded because source and target both used seed 7. Index 10 uses source 11 and training 1011. The other nine realisations, target seed 7, reference samples and projection directions are unchanged. The six excluded method/system records are historical audit inputs only; they enter no current table or figure.']
    table(lines,['Dimension','Spectrum','Previous SW2 mean +/- SD','Corrected SW2 mean +/- SD','Removed s=6','Added s=10','Reference'],[
        [r['dimension'],r['method'],fmt(r['old']),fmt(r['new']),fmt(r['removed_sw2']),fmt(r['added_sw2']),fmt(r['reference'])] for r in result['products']])
    increases=[100*(r['new']['mean']/r['old']['mean']-1) for r in result['products']]
    if min(increases)>0:
        lines+=[f'The six mean errors increase by {min(increases):.2f}%--{max(increases):.2f}% after removal of the dependent source/target pair. The correction is required by the sampling protocol, independently of its effect on the errors.','']
    lines+=['The product PDFs retain the first realisation in the marginal histograms and use the corrected ten-realisation mean and sample SD in the marginal-W2 panels. The old-to-new list below explicitly labels changes relative to the previous group-B ten-realisation results.','',
        '### Alanine fitted spectra and initial sources','',
        'The three archived spectra use the same Fourier dictionary (J=3249), r=256, smoothing 0.1 rad and relative Gram cutoff 1e-12. The Gram ranks below count centered nonconstant directions; the constant is separate. Eigenvalues are positive generator rates, before normalized flow time s=lambda1*t. They belong to the unit-mobility reversible surrogate fitted to the smoothed angular marginal, not the physical MD generator.']
    fits=result['alanine_fits']
    table(lines,['Fit trajectory','lambda1','lambda2','lambda3','lambda4','lambda5','Retained Gram rank'],[
        [r['fit_trajectory']+1,*[fmt(v) for v in r['lambda1_to_lambda5']],r['retained_gram_rank']] for r in fits])
    def vector(values):return '['+', '.join(fmt(v) for v in values)+']'
    table(lines,['Fit trajectory','Source mean (rad)','Source covariance (rad^2)','Mean basin / selected basin','Basin center (rad)','Training basin mass'],[
        [r['fit_trajectory']+1,vector(r['source_mean']),'; '.join(vector(v) for v in r['source_covariance']),
         f"{r['mean_basin']} / {r['selected_basin']}",vector(r['basin_center_angles'][r['mean_basin']]),fmt(r['basin_training_masses'][r['mean_basin']])] for r in fits])
    lines+=['Angles are ordered (phi, psi). Basins are the four fit-specific k-means regions in the periodic embedding; numeric basin labels are local to each fit and are not aligned physical conformer names. Each source mean lies in the selected, most populated training basin. The full Gaussian need not lie in that basin; all source-cloud basin masses and all basin centers are in the JSON. The third fit selects a different angular region and a much broader source.','']
    widths=[]
    for fit in fits:
        for evaluation in range(3):
            if evaluation==fit['fit_trajectory']:continue
            part=[next(r for r in seed['evaluations'] if r['evaluation_trajectory']==evaluation) for seed in fit['seeds']]
            widths.append([fit['fit_trajectory']+1,evaluation+1,
                fmt(summarize(r['initial_local_width_ratio'] for r in part)),
                fmt(summarize(r['endpoint']['local_width_ratio'] if r['endpoint'] else None for r in part))])
    table(lines,['Fit trajectory','Evaluation trajectory','Source local-width ratio','Local-width ratio at s=8'],widths)
    lines+=['Local width is the median square root of the smaller local covariance eigenvalue over 12 periodic nearest neighbors, divided by the same statistic of the evaluation cloud. Its sample mean and SD use all three prescribed source designs. No terminal width is assigned to an incomplete integration.','',
        '### Initial truncated ratio','',
        'The table evaluates the unchanged initial empirical coefficients on a 512-by-512 periodic grid. The source mass of {rho_hat_0 <= 1e-3} integrates the analytic wrapped Gaussian over that grid; the target mass uses the training trajectory smoothed by the unchanged 0.1-rad kernel. Uniform grid area and source-particle fractions are reported separately. These are quadrature diagnostics, not certified global bounds.']
    table(lines,['Fit','Seed','Grid minimum','Source mass (%)','Smoothed target mass (%)','Grid area (%)','Source particles (%)'],[
        [fit['fit_trajectory']+1,row['seed'],fmt(row['grid_minimum']),
         *[fmt(100*row[k]) for k in ('grid_source_mass_below_threshold','grid_target_mass_below_threshold','grid_area_fraction_below_threshold','source_particle_fraction_below_threshold')]]
        for fit in fits for row in fit['seeds']])
    lines+=['All three fits have negative grid values. For the first two fits, the small-ratio region has little initial source mass; for the third it contains a substantial part of the source. A global grid minimum by itself does not indicate how many transported particles encounter that region. The change of fit also changes the source and basin partition, so these observations do not isolate a spectral-estimation effect.','',
        '### Original and fivefold-budget integrations','',
        'For each fit and seed the two evaluation assignments have identical saved particle paths, RHS counts and floor/cap masks. Thus the original eighteen evaluations contain nine distinct integrations; only the three fitted on trajectory 3 are retried. Each is rerun once, then evaluated against trajectories 1 and 2. The original limits of 150000 RHS evaluations and 1200 seconds become 750000 evaluations and 6000 seconds. Dictionary, eigenpairs, source clouds, empirical coefficients, tolerances, step controls, floor and speed cap are unchanged.']
    table(lines,['Original fit','Seed','Termination reason','s reached','RHS evaluations','Floor fraction','Cap fraction'],[
        [fit['fit_trajectory']+1,r['seed'],r['termination_reason'],fmt(r['s_reached']),r['nfev'],fmt(r['floor_particle_fraction']),fmt(r['cap_particle_fraction'])]
        for fit in fits for r in fit['seeds']])
    retry=result['alanine_budget5']
    table(lines,['Fivefold-budget seed','Termination reason','s reached','Last saved s','RHS evaluations','Floor fraction','Cap fraction'],[
        [r['seed'],r['termination_reason'],fmt(r['completed_s']),fmt(r['last_checkpoint_s']),r['events']['nfev'],
         fmt(r['events']['floor_particle_fraction']),fmt(r['events']['cap_particle_fraction'])] for r in retry])
    table(lines,['Seed','Evaluation trajectory','SW2 at s=8','Mass TV at s=8','SW2 at last accepted s','Mass TV at last accepted s','Local-width ratio at last accepted s'],[
        [r['seed'],e['evaluation_trajectory']+1,fmt(e['endpoint']['sw2'] if e['endpoint'] else None),
         fmt(e['endpoint']['mass_tv'] if e['endpoint'] else None),fmt(e['last_accepted_score']['sw2']),
         fmt(e['last_accepted_score']['mass_tv']),fmt(e['last_accepted_score']['local_width_ratio'])]
        for r in retry for e in r['evaluations']])
    completed=sum(r['requested_endpoint_available'] for r in retry)
    lines+=[f'{completed}/3 distinct fivefold-budget integrations reached s=8. Incomplete integrations have unavailable s=8 SW2 and TV; the explicitly timed last accepted states are not terminal substitutes. Floor and cap fractions count particles affected at any attempted RHS evaluation, including rejected stages, up to termination. They are not fractions of evaluation calls.',
        f"The audit verified that all {result['verification']['original_alanine_files_unchanged']} original alanine files and 54 retained product records are unchanged. Original saved retry checkpoints are bitwise identical, and their floor/cap masks are subsets of the extended masks. The maximum recomputed grid/endpoint diagnostic difference is {fmt(result['verification']['maximum_diagnostic_difference'])}.",
        'Follow-up jobs run concurrently with one BLAS thread each; the product tasks retain eight coordinate workers. Their elapsed times describe this execution and are not sampler speed comparisons.','']


def export_public(data,summary):
    """One Git-visible numerical record, without local paths or large arrays."""
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k!='filepath'}
        if isinstance(value,list):return [clean(v) for v in value]
        return value
    followup=summary.get('followup')
    record=dict(format=1,scope='Published group-B per-realisation records and fixed follow-up; arrays remain in local archives.',
        trajectory_indexing='JSON uses 0,1,2; report prose uses trajectories 1,2,3.',
        rows=data,summary=summary,counts={name:len(rows) for name,rows in data.items()},
        supplemental_counts=dict(alanine_fit_diagnostics=3,distinct_budget5_integrations=3) if followup else {},
        excluded_product_indices=[6],active_product_indices=list(PRODUCT_SEED_INDICES))
    write_json(ROOT/'outputs/revision_results.json',clean(record))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('run','retry','diagnose'))
    p.add_argument('--seed',type=int,choices=ra.SEEDS);args=p.parse_args()
    if args.stage=='run':run()
    else:
        from experiment_store import managed_outputs
        with managed_outputs('double_well','alanine'),threadpool_limits(limits=1):
            if args.stage=='retry':
                if args.seed is None:p.error('--seed is required for retry')
                retry(args.seed)
            else:diagnose()

if __name__=='__main__':main()

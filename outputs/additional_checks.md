# Additional checks

These previously reported alanine trajectory-role checks supplement the manuscript experiments. The material was moved from `all_experiment_results_and_assessment.md` without changing numerical results. The manuscript report retains the original alanine experiment, cost comparison and iid source control.

Per-realisation records remain in `revision_results.json`; archived arrays and reproduction code are unchanged.

## B3(b). Alanine trajectory-role rotations

The additional B3 trajectory-role experiment completed 12/18 prescribed transports to s=8 under the unchanged numerical controls. Its six ordered pairs vary the fitted spectrum, source construction, basin partition and evaluation trajectory. Results and all incomplete integrations are reported below; the original figure alone does not establish robustness to changing the estimation trajectory.

Trajectory-pair tables number trajectories 1--3; stored IDs and JSON indices use 0--2.


| Fit / evaluation trajectory | lambda1 | SW2 | Mass TV | Reference SW2 | Reference TV | Local-width ratio | Completed |
|---|---|---|---|---|---|---|---|
| 1 / 2 | 0.0013776 | 0.0669617 +/- 0.0315511 | 0.0266667 +/- 0.00950438 | 0.0691394 +/- 0.0258861 | 0.0286667 +/- 0.012897 | 1.1886 +/- 0.0380956 | 3/3 |
| 1 / 3 | 0.0013776 | 0.0596977 +/- 0.0188045 | 0.033 +/- 0.0177764 | 0.0507342 +/- 0.0206598 | 0.0226667 +/- 0.0140119 | 1.1737 +/- 0.0878244 | 3/3 |
| 2 / 1 | 0.000162975 | 0.131598 +/- 0.00236414 | 0.053 +/- 0.00360555 | 0.0444623 +/- 0.00604066 | 0.0346667 +/- 0.00929157 | 0.794575 +/- 0.0202259 | 3/3 |
| 2 / 3 | 0.000162975 | 0.103306 +/- 0.00548067 | 0.032 +/- 0.00360555 | 0.0507342 +/- 0.0206598 | 0.0253333 +/- 0.0141892 | 0.78857 +/- 0.0723111 | 3/3 |
| 3 / 1 | 0.00163506 | unavailable | unavailable | 0.0444623 +/- 0.00604066 | 0.0243333 +/- 0.00665833 | unavailable | 0/3 |
| 3 / 2 | 0.00163506 | unavailable | unavailable | 0.0691394 +/- 0.0258861 | 0.0336667 +/- 0.0135769 | unavailable | 0/3 |


| Statistic across six ordered pairs | Mean +/- SD |
|---|---|
| sw2 | unavailable |
| mass_tv | unavailable |
| local_width_ratio | unavailable |
| reference_sw2 | 0.0547787 +/- 0.011472 |
| reference_mass_tv | 0.0282222 +/- 0.00501405 |
| lambda1 | 0.00105854 +/- 0.000703196 |

Terminal statistics across all six pairs require all eighteen requested endpoints; incomplete pairs are not omitted from the aggregation. For an incomplete rotation the JSON endpoint is null, while last_checkpoint_score and last_checkpoint_s retain the available checkpoint. The analogous filtered distance is retained as last_checkpoint_unaffected_sw2; it is not a terminal error.


| Incomplete integration | Last accepted s | Last saved s | RHS evaluations | Reason |
|---|---|---|---|---|
| rotation_fit2_eval0_seed1101 | 1.30976e-05 | 0 | 150000 | Resource limit reached; no completed endpoint is claimed. |
| rotation_fit2_eval0_seed1102 | 1.19209e-05 | 0 | 150000 | Resource limit reached; no completed endpoint is claimed. |
| rotation_fit2_eval0_seed1103 | 5.4682e-06 | 0 | 150000 | Resource limit reached; no completed endpoint is claimed. |
| rotation_fit2_eval1_seed1101 | 1.30976e-05 | 0 | 150000 | Resource limit reached; no completed endpoint is claimed. |
| rotation_fit2_eval1_seed1102 | 1.19209e-05 | 0 | 150000 | Resource limit reached; no completed endpoint is claimed. |
| rotation_fit2_eval1_seed1103 | 5.4682e-06 | 0 | 150000 | Resource limit reached; no completed endpoint is claimed. |

### Additional spectrum-fitting costs

| Estimation | Fit wall seconds | Fit CPU seconds | Threads |
|---|---|---|---|
| spectrum_fit1 | 27.0013 | 25.625 | 1 |
| spectrum_fit2 | 28.381 | 26.6719 | 1 |

### Safeguards for trajectory-role rotations

Fractions count particles affected at any evaluated stage, including rejected and dense-output stages. The unaffected-cloud distance is a conditional diagnostic. Torus wrapping is not box projection.

For incomplete alanine integrations, mask fractions cover the attempted RHS evaluations, but terminal full/filtered distances are unavailable. Any raw last-checkpoint distance is retained with its checkpoint time and is not substituted for the requested endpoint.

| Alanine case | Seed | Status | Floor | Nonpositive | Speed cap | Projection | Any | Full cloud SW2 | Unaffected SW2 |
|---|---|---|---|---|---|---|---|---|---|
| rotation_fit0_eval1_seed1101 | 1101 | ok | 0.001 | 0.001 | 0.006 | 0 | 0.006 | 0.045954 | 0.0425054 |
| rotation_fit0_eval1_seed1102 | 1102 | ok | 0.002 | 0.002 | 0.005 | 0 | 0.005 | 0.103243 | 0.101939 |
| rotation_fit0_eval1_seed1103 | 1103 | ok | 0.002 | 0.002 | 0.008 | 0 | 0.008 | 0.051688 | 0.0503011 |
| rotation_fit0_eval2_seed1101 | 1101 | ok | 0.001 | 0.001 | 0.006 | 0 | 0.006 | 0.0418771 | 0.0410331 |
| rotation_fit0_eval2_seed1102 | 1102 | ok | 0.002 | 0.002 | 0.005 | 0 | 0.005 | 0.0578643 | 0.0595371 |
| rotation_fit0_eval2_seed1103 | 1103 | ok | 0.002 | 0.002 | 0.008 | 0 | 0.008 | 0.0793518 | 0.0777545 |
| rotation_fit1_eval0_seed1101 | 1101 | ok | 0 | 0 | 0.003 | 0 | 0.003 | 0.13308 | 0.135018 |
| rotation_fit1_eval0_seed1102 | 1102 | ok | 0 | 0 | 0.001 | 0 | 0.001 | 0.128871 | 0.128561 |
| rotation_fit1_eval0_seed1103 | 1103 | ok | 0.001 | 0.001 | 0.002 | 0 | 0.002 | 0.132841 | 0.133661 |
| rotation_fit1_eval2_seed1101 | 1101 | ok | 0 | 0 | 0.003 | 0 | 0.003 | 0.102745 | 0.104663 |
| rotation_fit1_eval2_seed1102 | 1102 | ok | 0 | 0 | 0.001 | 0 | 0.001 | 0.0981274 | 0.0981028 |
| rotation_fit1_eval2_seed1103 | 1103 | ok | 0.001 | 0.001 | 0.002 | 0 | 0.002 | 0.109046 | 0.109588 |
| rotation_fit2_eval0_seed1101 | 1101 | incomplete | 0.639 | 0.639 | 0.729 | 0 | 0.729 | unavailable | unavailable |
| rotation_fit2_eval0_seed1102 | 1102 | incomplete | 0.622 | 0.622 | 0.711 | 0 | 0.711 | unavailable | unavailable |
| rotation_fit2_eval0_seed1103 | 1103 | incomplete | 0.538 | 0.538 | 0.661 | 0 | 0.661 | unavailable | unavailable |
| rotation_fit2_eval1_seed1101 | 1101 | incomplete | 0.639 | 0.639 | 0.729 | 0 | 0.729 | unavailable | unavailable |
| rotation_fit2_eval1_seed1102 | 1102 | incomplete | 0.622 | 0.622 | 0.711 | 0 | 0.711 | unavailable | unavailable |
| rotation_fit2_eval1_seed1103 | 1103 | incomplete | 0.538 | 0.538 | 0.661 | 0 | 0.661 | unavailable | unavailable |

### Reproduction audit

503 endpoint/scalar checks were recorded; 4 did not satisfy the requested reproduction check (tolerance 1e-12, with missing completed endpoints also flagged). B1 deliberately changes the mode set; its new endpoint is not expected to equal the legacy endpoint.

The separate saved-array audit recomputed 774 endpoint distances and checked 3585 masks, including their unions and reported fractions. The maximum absolute difference in the full or filtered distances was 8.88e-16.

| Task | Run | Check |
|---|---|---|
| alanine_original_assignment_refit | rotation_fit0_eval2_seed1101 | {'endpoint_bitwise_equal': False, 'endpoint_max_absolute_difference': 4.518925985852462e-06, 'max_checkpoint_cloud_difference': 7.089551102490432e-05, 'max_checkpoint_sw2_difference': 3.551418938790851e-08, 'requested_horizon_completed': True, 'passes_1e12': False, 'scope': 'Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.'} |
| alanine_original_assignment_refit | rotation_fit0_eval2_seed1102 | {'endpoint_bitwise_equal': False, 'endpoint_max_absolute_difference': 3.822091440675024e-06, 'max_checkpoint_cloud_difference': 0.000850465561576641, 'max_checkpoint_sw2_difference': 1.3822372150334994e-07, 'requested_horizon_completed': True, 'passes_1e12': False, 'scope': 'Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.'} |
| alanine_original_assignment_refit | rotation_fit0_eval2_seed1103 | {'endpoint_bitwise_equal': False, 'endpoint_max_absolute_difference': 7.1358525630671465e-06, 'max_checkpoint_cloud_difference': 4.5597218975679255e-05, 'max_checkpoint_sw2_difference': 2.059280550248399e-08, 'requested_horizon_completed': True, 'passes_1e12': False, 'scope': 'Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.'} |
| alanine_single_thread_refit | spectrum_fit0 | {'maximum_eigenvalue_absolute_difference': 1.2153662964919931e-08, 'maximum_eigenvalue_relative_difference': 8.284119113814352e-10, 'eigenvalues_above_absolute_tolerance': 246, 'lambda1_absolute_difference': 1.1412199310556481e-12, 'passes_1e12': False, 'scope': 'Requested single-thread refit versus archived spectrum. Cost transports retain archived eigenpairs; role rotations use the refit. Eigenvector signs are not compared as numerical errors.'} |

### Protocol and execution notes

- The three alanine spectra are fitted sequentially. After fitting, the eighteen independent role-rotation transports may run in four single-BLAS-thread processes; those transport timings are descriptive.
- Six ordered trajectory pairs share three fits and three evaluation trajectories; their sample SD is descriptive, not an independent-data standard error.
- Role rotations jointly change the fitted spectrum, training-derived source and basin partition, and evaluation trajectory. Their spread does not isolate spectral estimation error alone.

| Task execution | Wall seconds |
|---|---|
| B3(b)/B4: trajectory rotations | 1188.41 |

## Group-B follow-up: alanine

Trajectories are numbered 1--3 here; JSON indices remain 0--2.

### Alanine fitted spectra and initial sources

The three archived spectra use the same Fourier dictionary (J=3249), r=256, smoothing 0.1 rad and relative Gram cutoff 1e-12. The Gram ranks below count centered nonconstant directions; the constant is separate. Eigenvalues are positive generator rates, before normalized flow time s=lambda1*t. They belong to the unit-mobility reversible surrogate fitted to the smoothed angular marginal, not the physical MD generator.

| Fit trajectory | lambda1 | lambda2 | lambda3 | lambda4 | lambda5 | Retained Gram rank |
|---|---|---|---|---|---|---|
| 1 | 0.0013776 | 0.0753225 | 0.180084 | 2.02018 | 2.91361 | 3098 |
| 2 | 0.000162975 | 0.077851 | 0.153868 | 2.00492 | 2.93875 | 3098 |
| 3 | 0.00163506 | 0.0764672 | 0.17607 | 1.98478 | 2.92734 | 3115 |


| Fit trajectory | Source mean (rad) | Source covariance (rad^2) | Mean basin / selected basin | Basin center (rad) | Training basin mass |
|---|---|---|---|---|---|
| 1 | [-1.32805, 2.61219] | [0.0321022, -0.00547382]; [-0.00547382, 0.0480748] | 0 / 0 | [-1.32742, 2.61242] | 0.37952 |
| 2 | [-1.32262, 2.61679] | [0.0377047, -0.00524228]; [-0.00524228, 0.0474885] | 1 / 1 | [-1.32184, 2.61978] | 0.39288 |
| 3 | [-1.62154, -0.0492303] | [0.431259, 0.0421493]; [0.0421493, 0.103421] | 0 / 0 | [-1.62711, -0.044565] | 0.35148 |

Angles are ordered (phi, psi). Basins are the four fit-specific k-means regions in the periodic embedding; numeric basin labels are local to each fit and are not aligned physical conformer names. Each source mean lies in the selected, most populated training basin. The full Gaussian need not lie in that basin; all source-cloud basin masses and all basin centers are in the JSON. The third fit selects a different angular region and a much broader source.


| Fit trajectory | Evaluation trajectory | Source local-width ratio | Local-width ratio at s=8 |
|---|---|---|---|
| 1 | 2 | 0.410862 +/- 0.0097382 | 1.1886 +/- 0.0380956 |
| 1 | 3 | 0.405632 +/- 0.027294 | 1.1737 +/- 0.0878244 |
| 2 | 1 | 0.42561 +/- 0.0165471 | 0.794575 +/- 0.0202259 |
| 2 | 3 | 0.421693 +/- 0.0268803 | 0.78857 +/- 0.0723111 |
| 3 | 1 | 0.949447 +/- 0.027562 | unavailable |
| 3 | 2 | 0.953364 +/- 0.0322457 | unavailable |

Local width is the median square root of the smaller local covariance eigenvalue over 12 periodic nearest neighbors, divided by the same statistic of the evaluation cloud. Its sample mean and SD use all three prescribed source designs. No terminal width is assigned to an incomplete integration.

### Initial truncated ratio

The table evaluates the unchanged initial empirical coefficients on a 512-by-512 periodic grid. The source mass of {rho_hat_0 <= 1e-3} integrates the analytic wrapped Gaussian over that grid; the target mass uses the training trajectory smoothed by the unchanged 0.1-rad kernel. Uniform grid area and source-particle fractions are reported separately. These are quadrature diagnostics, not certified global bounds.

| Fit | Seed | Grid minimum | Source mass (%) | Smoothed target mass (%) | Grid area (%) | Source particles (%) |
|---|---|---|---|---|---|---|
| 1 | 1101 | -58.8162 | 0.147686 | 33.4153 | 45.8012 | 0.1 |
| 1 | 1102 | -61.0964 | 0.146406 | 32.9806 | 46.1262 | 0.1 |
| 1 | 1103 | -60.4244 | 0.148117 | 33.0097 | 45.7211 | 0.2 |
| 2 | 1101 | -60.1149 | 0.0400675 | 31.6691 | 50.7416 | 0 |
| 2 | 1102 | -58.9217 | 0.0379282 | 31.6959 | 48.5111 | 0 |
| 2 | 1103 | -55.4157 | 0.0436349 | 30.0757 | 51.2875 | 0.1 |
| 3 | 1101 | -18775.7 | 37.4529 | 46.1426 | 44.9745 | 37.3 |
| 3 | 1102 | -17065.2 | 37.4215 | 46.5376 | 44.1147 | 37 |
| 3 | 1103 | -14011 | 36.6881 | 47.2772 | 43.4772 | 37.8 |

All three fits have negative grid values. For the first two fits, the small-ratio region has little initial source mass; for the third it contains a substantial part of the source. A global grid minimum by itself does not indicate how many transported particles encounter that region. The change of fit also changes the source and basin partition, so these observations do not isolate a spectral-estimation effect.

### Original and fivefold-budget integrations

For each fit and seed the two evaluation assignments have identical saved particle paths, RHS counts and floor/cap masks. Thus the original eighteen evaluations contain nine distinct integrations; only the three fitted on trajectory 3 are retried. Each is rerun once, then evaluated against trajectories 1 and 2. The original limits of 150000 RHS evaluations and 1200 seconds become 750000 evaluations and 6000 seconds. Dictionary, eigenpairs, source clouds, empirical coefficients, tolerances, step controls, floor and speed cap are unchanged.

| Original fit | Seed | Termination reason | s reached | RHS evaluations | Floor fraction | Cap fraction |
|---|---|---|---|---|---|---|
| 1 | 1101 | completed | 8 | 22741 | 0.001 | 0.006 |
| 1 | 1102 | completed | 8 | 20737 | 0.002 | 0.005 |
| 1 | 1103 | completed | 8 | 21253 | 0.002 | 0.008 |
| 2 | 1101 | completed | 8 | 21697 | 0 | 0.003 |
| 2 | 1102 | completed | 8 | 36577 | 0 | 0.001 |
| 2 | 1103 | completed | 8 | 8941 | 0.001 | 0.002 |
| 3 | 1101 | evaluation_budget | 1.30976e-05 | 150000 | 0.639 | 0.729 |
| 3 | 1102 | evaluation_budget | 1.19209e-05 | 150000 | 0.622 | 0.711 |
| 3 | 1103 | evaluation_budget | 5.4682e-06 | 150000 | 0.538 | 0.661 |


| Fivefold-budget seed | Termination reason | s reached | Last saved s | RHS evaluations | Floor fraction | Cap fraction |
|---|---|---|---|---|---|---|
| 1101 | evaluation_budget | 2.43264e-05 | 0 | 750000 | 0.659 | 0.747 |
| 1102 | evaluation_budget | 3.30263e-05 | 0 | 750000 | 0.654 | 0.736 |
| 1103 | evaluation_budget | 1.23319e-05 | 0 | 750000 | 0.633 | 0.716 |


| Seed | Evaluation trajectory | SW2 at s=8 | Mass TV at s=8 | SW2 at last accepted s | Mass TV at last accepted s | Local-width ratio at last accepted s |
|---|---|---|---|---|---|---|
| 1101 | 1 | unavailable | unavailable | 0.740972 | 0.623 | 0.0969751 |
| 1101 | 2 | unavailable | unavailable | 0.759964 | 0.647 | 0.0978425 |
| 1102 | 1 | unavailable | unavailable | 0.72664 | 0.622 | 0.0722427 |
| 1102 | 2 | unavailable | unavailable | 0.768098 | 0.675 | 0.0701893 |
| 1103 | 1 | unavailable | unavailable | 0.755998 | 0.622 | 0.374106 |
| 1103 | 2 | unavailable | unavailable | 0.771564 | 0.645 | 0.386271 |

0/3 distinct fivefold-budget integrations reached s=8. Incomplete integrations have unavailable s=8 SW2 and TV; the explicitly timed last accepted states are not terminal substitutes. Floor and cap fractions count particles affected at any attempted RHS evaluation, including rejected stages, up to termination. They are not fractions of evaluation calls.
The audit verified that all 42 original alanine files are unchanged. Original saved retry checkpoints are bitwise identical, and their floor/cap masks are subsets of the extended masks. The maximum recomputed grid/endpoint diagnostic difference is 0.
Follow-up jobs run concurrently with one BLAS thread each; the product tasks retain eight coordinate workers. Their elapsed times describe this execution and are not sampler speed comparisons.

## Files and reproduction

The revision records, raw public alanine trajectories needed for role rotations, configuration snapshots and baseline are archive members under `outputs/revision/` in `double_well.zip`. The Git-visible `outputs/revision_results.json` retains all group-B per-realisation records, summaries and follow-up diagnostics. The archive contents and JSON were not changed by this reorganization.

Alanine role rotations use four independent transport processes after their three spectra have been fitted sequentially.

For the fixed follow-up, run `python -u -B supplementary/revision_followup.py run` in the same pinned environment, then run `revision_verify.py`, `revision_publish.py` and `revision_figures.py --products-only`. It adds product index 10 (source 11, training 1011), excludes the dependent index 6, and performs exactly three distinct alanine integrations with both budgets multiplied by five. Saved follow-up integrations are reused. The original spectra and numerical controls are preserved; the optional confined multiwell study is not run. Do not run two managed archive sessions concurrently.

# Manuscript experiment results

Retained results include favorable and unfavorable manuscript cases. Every repeated summary includes all prescribed seeds and uses sample standard deviations. Alanine retains one 256-mode Fourier experiment with distribution and convergence figures, together with the RBF control and collapse diagnostics.

Synthetic multivariate distances use 64 fixed projections (seed 0); references use ten target-cloud repetitions. The analytical OU studies compare directly with the Gaussian target. References describe empirical sampling variability and are not universal lower bounds. Alanine has a separate periodic metric.

## Manuscript correspondence

| Manuscript item | Retained configuration |
|---|---|
| Figure 1 and dictionary tables | Koopman (RBF) and Koopman (Legendre) identify reversible gEDMD generator estimates; all use the same BKT transport. Figure 1 shows one fixed realisation, whereas repeated table entries report means and sample standard deviations. |
| Table 1 | 10D double well product, beta=0: one double-well factor and nine stationary Gaussian factors. 50D double-well product: fifty double-well factors. Product refers to the invariant density; the potential is additive. |
| [Figure 10](figures/fig_alanine.pdf) | 256-mode BKT at s=8, seeds 1101-1103, empirical initial coefficients. The angle panels show seed 1101; the error panel includes all three paired designs. |
| [Figure 11](figures/fig_alanine_convergence.pdf) | The same BKT trajectories over 0 <= s <= 8, compared with LAWGD and KDE. BKT and LAWGD share the 256 eigenpairs and initial empirical coefficients. |

## Fixed protocols

| Experiment | Setup |
|---|---|
| 1D OU | N(1.5,0.5^2) to N(0,1); Hermite spectrum; RK4 h=0.05; initial-particle coefficients (S). |
| Matched OU paths | M=2000; r=10,20,40; T=6; h=0.05,0.025; seeds 1000-1009; P/I/S; all 180 runs. |
| 10D OU | Coupling 0 and 0.15; M=5000; 30 modes/coordinate; T=6; h=0.05; seeds 700-709. |
| 2D double wells | beta=0,0.25,0.5,1; M=2000; n=200000; r=64; RBF J=145; FD-201; T=8/lambda1; h=0.05. |
| 4/9 wells | M=2000; n=200000; r=64; RBF/Legendre/FD-201; h=0.02; ten seeds. |
| 10D double wells | beta=0,0.5; M=1000; n=100000; r=16; RBF J=657; h=0.05; ten seeds; independent mode selection. |
| 10D/50D double-well products | M=20000; n=200000; r=16 per coordinate; requested T=10.6854, effective time 10.68 (534 steps); h=0.02; ten paired clouds. |
| Equal-data comparison | beta=0,0.5; n=200000 shared pairs; M=2000; ten paired seeds; common horizon. |

The synthetic ratio floor is 0.001 and speed cap is 20. The boxed double-well solver projects intermediate RK stages. The main 2D double-well experiments and equal-data comparison share the admissible source: a cosine-squared x1 bump on [0.4,1.6] and x2 variance 0.3. The uncoupled 10D experiment retains nine stationary harmonic coordinates of variance 0.5. Reproduction uses frozen main training sizes; the appendix sample-size and rank studies remain explicit sensitivity experiments.

## Ornstein-Uhlenbeck results

| Scan | Values | W2 |
|---|---|---|
| Rank (M=10000, T=6) | 10, 15, 20, 30, 60 | 0.0744, 0.0451, 0.0233, 0.0112, 0.0109 |
| Particles (r=40, T=6) | 500, 1000, 2000, 5000, 20000 | 0.0384, 0.0300, 0.0242, 0.0117, 0.0103 |
| Time (r=40) | 1.0, 2.0, 3.0, 4.0, 6.0 | 0.5560, 0.2044, 0.0765, 0.0311, 0.0144 |

At M=10000 the reference is 0.0189 +/- 0.0049. The 1D notebook scans use midpoint quantiles; the matched path diagnostic uses exact Gaussian quantile-interval integrals.

| 10D coupling | Final SW2 | Reference SW2 | Relative covariance error |
|---|---|---|---|
| 0.0 | 0.0219 +/- 0.0004 | 0.0262 +/- 0.0026 | 0.0425 +/- 0.0050 |
| 0.15 | 0.0195 +/- 0.0005 | 0.0235 +/- 0.0018 | 0.0421 +/- 0.0059 |


| Matched OU, h=0.025 | Regime | W2 to target | Endpoint D | Residual-norm B |
|---|---|---|---|---|
| 10 | P | 0.1020 +/- 0.0180 | 0.0953 +/- 0.0058 | 0.2529 +/- 0.0203 |
| 10 | I | 0.1104 +/- 0.0144 | 0.1011 +/- 0.0108 | 0.2664 +/- 0.0260 |
| 10 | S | 0.0961 +/- 0.0094 | 0.1020 +/- 0.0096 | 0.2563 +/- 0.0168 |
| 20 | P | 0.0533 +/- 0.0135 | 0.0249 +/- 0.0029 | 0.0433 +/- 0.0062 |
| 20 | I | 0.0668 +/- 0.0151 | 0.0415 +/- 0.0116 | 0.0590 +/- 0.0129 |
| 20 | S | 0.0382 +/- 0.0065 | 0.0456 +/- 0.0164 | 0.0629 +/- 0.0191 |
| 40 | P | 0.0447 +/- 0.0151 | 0.0015 +/- 0.0008 | 0.0200 +/- 0.0006 |
| 40 | I | 0.0609 +/- 0.0170 | 0.0330 +/- 0.0119 | 0.0504 +/- 0.0146 |
| 40 | S | 0.0227 +/- 0.0045 | 0.0411 +/- 0.0163 | 0.0545 +/- 0.0152 |

Exact-flow image of the same finite cloud: 0.0448 +/- 0.0152; independent-target reference: 0.0391 +/- 0.0096. P gives the smaller discrepancy from the paired exact trajectories; S gives the smaller empirical target distance. I uses 2000 extra source points. The same-sample corollary compares P and S under additional deterministic common-region bounds; those hypotheses are not verified by these experiments.

D is checked from endpoints and signed residual integration; B takes the norm before time integration. The maximum endpoint-identity RMS discrepancy is 2.7e-16. Quadrature and step differences are numerical diagnostics, not rigorously enclosed certificates. All ranks and both steps remain in the saved results.

| OU rank | Minimum ratio at t=0 | Screened Lipschitz integral | Minimum good-region mass |
|---|---|---|---|
| 10 | -4.8919 | 36.2076 | 0.8181 |
| 20 | -0.4383 | 4.9077 | 0.9151 |
| 40 | -0.3952 | 4.4948 | 0.9381 |

## Double wells, multiwells and products

Koopman (RBF) and Koopman (Legendre) denote generator eigenpairs estimated by reversible gEDMD with the respective dictionaries. These labels distinguish spectral approximations in the same BKT transport formula; FD denotes the finite-difference spectrum.

| System | FD | Koopman (RBF) | Koopman (Legendre) | Reference SW2 |
|---|---|---|---|---|
| 2D double well product, beta=0 | 0.0267 +/- 0.0024 | 0.0276 +/- 0.0027 | 0.0278 +/- 0.0026 | 0.0397 +/- 0.0076 |
| 2D double well, beta=0.25 | 0.0283 +/- 0.0023 | 0.0295 +/- 0.0027 | 0.0296 +/- 0.0025 | 0.0410 +/- 0.0084 |
| 2D double well, beta=0.5 | 0.0282 +/- 0.0024 | 0.0305 +/- 0.0043 | 0.0288 +/- 0.0028 | 0.0420 +/- 0.0099 |
| 2D double well, beta=1 | 0.0272 +/- 0.0018 | 0.0273 +/- 0.0027 | 0.0279 +/- 0.0026 | 0.0417 +/- 0.0119 |
| 2D four-well product | 0.0236 +/- 0.0026 | 0.0281 +/- 0.0024 | 0.0263 +/- 0.0021 | 0.0433 +/- 0.0083 |
| 2D nine wells | 0.0328 +/- 0.0029 | 0.0548 +/- 0.0063 | median 0.4771; 5/10 above 10 x reference mean | 0.0340 +/- 0.0075 |
| 10D double well product, beta=0 | 0.0526 +/- 0.0020 | 0.0610 +/- 0.0020 | 0.0724 +/- 0.0079 | 0.0590 +/- 0.0042 |
| 10D double well, beta=0.5 | -- | 0.1613 +/- 0.0337 | 0.2269 +/- 0.0285 | 0.0507 +/- 0.0034 |
| 10D double-well product | 0.0151 +/- 0.0003 | 0.0195 +/- 0.0021 | 0.0195 +/- 0.0021 | 0.0156 +/- 0.0014 |
| 50D double-well product | 0.0158 +/- 0.0002 | 0.0188 +/- 0.0012 | 0.0188 +/- 0.0012 | 0.0162 +/- 0.0008 |

The table summarizes ten prescribed realisations per repeated cell. Reference distances measure finite-sample variability. Nine-well Legendre seed errors are 1.637, 2.706, 0.052, 0.048, 0.902, 1.257, 2.038, 0.036, 0.045, 0.036. All are retained. The product results rely on separability: the potential is a sum of coordinate potentials and the invariant density is a product. The uncoupled 10D double well has one double-well factor and nine stationary N(0, 0.5) factors; the 10D/50D double-well products have a double-well factor in every coordinate.
The 10D/50D product summaries use indices s=0--5,7--10: source seed 1+s skips the fixed target seed 7. The dependent source/target pair at index 6 is excluded, and index 10 uses source seed 11 and training seed 1011. Nine original realisations and the fixed target, reference statistics and projection directions are unchanged. The follow-up section compares the previous and corrected ten-realisation summaries.

| Product | RBF worst marginal W2 | Reference worst marginal W2 | RBF energy | Reference energy | RBF negative-count TV | Reference negative-count TV |
|---|---|---|---|---|---|---|
| 10 | 0.0356 +/- 0.0056 | 0.0260 +/- 0.0055 | 0.0050 +/- 0.0010 | 0.0052 +/- 0.0013 | 0.0092 +/- 0.0021 | 0.0095 +/- 0.0035 |
| 50 | 0.0387 +/- 0.0047 | 0.0297 +/- 0.0045 | 0.0116 +/- 0.0009 | 0.0120 +/- 0.0010 | 0.0191 +/- 0.0028 | 0.0165 +/- 0.0032 |

### Appendix sensitivity results

Rank scans use the first source seed; they retain nonmonotone and unstable results. The complete 2D ranks, paired step checks and safeguard counts remain in the 320-run admissible-source suite.

| System | Spectrum | SW2 by rank |
|---|---|---|
| 4 wells | FD | r=3: 0.321, r=8: 0.129, r=16: 0.124, r=32: 0.051, r=64: 0.024, r=128: 0.022 |
| 4 wells | Koopman (RBF) | r=3: 0.315, r=16: 0.125, r=32: 0.050, r=64: 0.029, r=96: 0.029 |
| 4 wells | Koopman (Legendre) | r=3: 0.316, r=16: 0.128, r=32: 2.443, r=64: 0.027, r=96: 0.027 |
| 9 wells | FD | r=8: 0.325, r=16: 0.199, r=32: 0.049, r=64: 0.036, r=128: 0.032 |
| 9 wells | Koopman (RBF) | r=8: 0.309, r=16: 0.188, r=32: 0.063, r=64: 0.063, r=96: 0.062 |
| 9 wells | Koopman (Legendre) | r=8: 0.911, r=16: 1.559, r=32: 2.345, r=64: 1.637, r=96: 1.882 |


| Coupled 10D dictionary | Size parameter | Requested rank | SW2 |
|---|---|---|---|
| Koopman (Legendre) | 3 | 16 | 0.2099 |
| Koopman (Legendre) | 4 | 16 | 0.1913 |
| Koopman (Legendre) | 3 | 32 | 0.2126 |
| Koopman (Legendre) | 4 | 32 | 0.2198 |
| Koopman (Legendre) | 3 | 64 | 0.3250 |
| Koopman (Legendre) | 4 | 64 | 0.2084 |
| Koopman (RBF) | 10 | 16 | 0.1451 |
| Koopman (RBF) | 8 | 16 | 0.1119 |
| Koopman (RBF) | 10 | 32 | 0.1321 |
| Koopman (RBF) | 8 | 32 | 0.1033 |
| Koopman (RBF) | 10 | 64 | 0.0838 |
| Koopman (RBF) | 8 | 64 | 0.0876 |

The coupled 10D dictionary comparison uses n=100000 and the first seed. Its horizon changes with the fitted eigenvalue; 0/12 configurations have terminal SW2 at or below the reference mean plus one sample standard deviation.

| System | n=10000 | n=100000 | n=200000 |
|---|---|---|---|
| 2D double well product, beta=0 | 0.0345 +/- 0.0041 | 0.0285 +/- 0.0025 | 0.0276 +/- 0.0027 |
| 2D double well, beta=0.25 | 0.0364 +/- 0.0043 | 0.0309 +/- 0.0037 | 0.0295 +/- 0.0027 |
| 2D double well, beta=0.5 | 0.0373 +/- 0.0077 | 0.0308 +/- 0.0039 | 0.0305 +/- 0.0043 |
| 2D double well, beta=1 | 0.0532 +/- 0.0201 | 0.0284 +/- 0.0022 | 0.0273 +/- 0.0027 |
| 2D four-well product | 0.0475 +/- 0.0128 | 0.0294 +/- 0.0037 | 0.0281 +/- 0.0024 |
| 2D nine wells | 0.0866 +/- 0.0240 | 0.0561 +/- 0.0063 | 0.0548 +/- 0.0063 |
| 10D double well product, beta=0 | 0.0684 +/- 0.0039 | 0.0610 +/- 0.0020 | 0.0603 +/- 0.0042 |
| 10D double well, beta=0.5 | 0.1480 +/- 0.0298 | 0.1613 +/- 0.0337 | 0.1898 +/- 0.0268 |


| 2D beta | Independent I | Same-sample S |
|---|---|---|
| 0.0 | 0.0486 +/- 0.0142 | 0.0276 +/- 0.0027 |
| 0.25 | 0.0486 +/- 0.0138 | 0.0295 +/- 0.0027 |
| 0.5 | 0.0476 +/- 0.0111 | 0.0305 +/- 0.0043 |
| 1.0 | 0.0427 +/- 0.0082 | 0.0273 +/- 0.0027 |

I uses an extra 2000 independent source draws, with coefficients fixed thereafter. The original coupled full-plane Gaussian source violates the bounded-ratio assumption at positive coupling. Variance 0.3 restores this source condition for the four 2D cases; box projection and estimated eigenpairs still prevent verification of every theorem hypothesis.

## Equal-data comparison

| beta | Method | SW2 | Fit + sampling seconds | Reference-threshold hits |
|---|---|---|---|---|
| 0.0 | BKT | 0.0276 +/- 0.0027 | 9.5 +/- 0.5 | 10/10 |
| 0.0 | Drift + Langevin | 0.2418 +/- 0.1010 | 47.8 +/- 1.4 | 0/10 |
| 0.0 | KDE particle flow | 0.0394 +/- 0.0130 | 53.6 +/- 1.5 | 9/10 |
| 0.5 | BKT | 0.0305 +/- 0.0043 | 8.7 +/- 0.2 | 10/10 |
| 0.5 | Drift + Langevin | 0.2480 +/- 0.0661 | 40.5 +/- 0.6 | 0/10 |
| 0.5 | KDE particle flow | 0.0477 +/- 0.0267 | 45.9 +/- 0.6 | 8/10 |


| beta | Independent-target reference SW2 | Crossing threshold |
|---|---|---|
| 0.0 | 0.0397 +/- 0.0076 | 0.0473 |
| 0.5 | 0.0420 +/- 0.0099 | 0.0519 |

All six entries use ten paired realisations and report means +/- sample standard deviations. The source is the same as in the main two-dimensional double-well experiments: a cosine-squared first-coordinate bump on [0.4,1.6] and an independent centred Gaussian second coordinate with variance 0.3. Its density ratio is bounded for both coupling values, since 0.3 < 1/(2+beta).

The 200000 trajectory pairs per seed, target clouds, ten-pair reference statistics and 64 projection directions are unchanged. All 60 transports and the twenty spectral and twenty drift fits were recomputed. Single-thread costs are measured per run and exclude common input generation and metric callbacks; the shared measured drift-fit cost is charged separately to each baseline. The BKT clouds and observation-time errors are checked against the corresponding main variance-0.3 results.

The common horizons are T=10.7 for beta=0 and T=9.4 for beta=0.5. A reference-threshold crossing means SW2 at a prescribed common observation time is no greater than the independent-target-pair reference mean plus one sample standard deviation. The count is not restricted to the terminal observation and does not use the reference mean alone.

Projection of training trajectories, reference samples and transported particles onto the numerical box remains a separate approximation; intermediate RK stages are also projected. The KDE method interacts through its evolving particle density. The fitted-drift Langevin clouds again show widened tails and boundary accumulation; the saved endpoint diagnostics do not isolate the causes. These comparisons concern the stated fitted models and discretisations, not a general ranking of the methods.

### Manuscript integration

The table above and [updated comparison figure](figures/fig_data_comparison.pdf) provide the ten-realisation equal-data values for Section 5 and Appendix D.2. The source variance remains 0.3, as in the preceding five-realisation comparison. The figure displays errors, while costs are given in the text and table. The manuscript text and its figure copy are left for author integration. Retain the description of box projection. The variance-0.3 statement applies to the two-dimensional V_beta experiments; the ten-dimensional V_beta source retains harmonic-coordinate variance 0.5. Those coordinates are stationary only in the uncoupled case.

Suggested interpretation (all prescribed realisations retained):

> Under this fixed protocol, BKT has the smallest mean terminal sliced Wasserstein distance and the lowest mean fitting-plus-sampling cost at both coupling values.
> At beta=0, the numbers of realisations that cross the reference threshold are BKT 10/10, Drift + Langevin 0/10, KDE particle flow 9/10.
> At beta=0.5, the numbers of realisations that cross the reference threshold are BKT 10/10, Drift + Langevin 0/10, KDE particle flow 8/10.
> The threshold is the independent-target reference mean plus one sample standard deviation; these finite-sample comparisons do not establish a general ordering of the methods.

## Alanine dipeptide

Public mdshare trajectories 0/1/2 supply fitting/validation/evaluation data (250 ns and 250000 frames each, 1 ps spacing). All trajectory-0 frames enter the fit; 25000 fixed subsampled frames define the source partition. Validation/evaluation pools have 12000 frames each. Fourier degree 28 gives 3249 basis functions; the transport retains 256 nonconstant modes. Gram cutoff 1e-12, smoothing 0.10 rad, s=lambda1*T=8.

The local wrapped-Gaussian source uses a training-derived mean and covariance (scale 0.7^2). Each 1000-point cloud uses the first 1000 points of a scrambled 1024-point Sobol net, the Gaussian inverse CDF and a fixed Cholesky factor. The spectral coefficients are empirical moments of these same initial particles (regime S), fixed thereafter. Sobol points are not iid samples, so this example does not directly verify the theorem's iid sampling bound. Seeds 1101-1103 share one fitted spectrum. The distribution figure and the BKT convergence curve use exactly the same trajectories and endpoint s=8. Integration controls are specified in the convergence protocol below.

| Metric | Initial | BKT at s=8 | Reference-reference |
|---|---|---|---|
| sw2 | 0.6149 +/- 0.0032 | 0.0597 +/- 0.0188 | 0.0507 +/- 0.0207 |
| mass_tv | 0.6037 +/- 0.0186 | 0.0330 +/- 0.0178 | 0.0227 +/- 0.0140 |

BKT SW2 is 1.177 times the reference mean (2/3 smaller paired values). Local-width ratio: 1.1737 +/- 0.0878. Rare-region mass: 0.0287 versus 0.0420. The global distances are of the same order as the sampling reference; rare-region coverage and within-basin spread remain imperfect.

SW2 uses 32 projections (seed 2026) in [cos(phi), cos(psi), sin(phi), sin(psi)], an extrinsic periodic embedding. Mass TV measures four training-defined regions, not full densities. Three clouds per seed are disjoint subsets of one evaluation trajectory. Variability is conditional on the spectrum and reflects scrambling/reference draws, not independent MD datasets.

The operator is a unit-mobility reversible surrogate of the smoothed angle marginal, not the physical MD generator. Outputs are angles, not full molecular configurations.

The additional B3 trajectory-role experiment completed 12/18 prescribed transports to s=8 under the unchanged numerical controls. Its six ordered pairs vary the fitted spectrum, source construction, basin partition and evaluation trajectory. Results and all incomplete integrations are reported in the revision section; the original figure alone does not establish robustness to changing the estimation trajectory.

Fresh single-thread transport wall times to s=8 are 72.4349 +/- 2.8827 s for BKT, 70.2462 +/- 3.9356 s for LAWGD and 1056.3980 +/- 144.7780 s for KDE; estimation and initial moments are tabulated separately in B3. BKT and LAWGD have comparable full-horizon costs in this test. Earlier settling in normalized flow time does not by itself establish a lower total computational cost.


Fourier/BKT reproduction check, seed 1101 (spectrum refitted: True): endpoint wrapped RMS difference 1.46e-16 rad; absolute SW2 difference 6.94e-18. The saved trajectories are retained unchanged.


### Retained RBF failure

Periodic 16x16 RBF grid plus constant (J=257), width 0.45, r=64, Gram cutoff 1e-5, smoothing 0.08 rad (jitter seed 91073), population Gauss-Hermite source moments, and iid source clouds. Dictionary, rank, smoothing, coefficient regime, horizon and source design differ from the 256-mode Fourier experiment, so the contrast does not isolate a dictionary effect.

| Case | Seeds | tau | SW2 | Mass TV | Local-width ratio |
|---|---|---|---|---|---|
| collapse | 301, 302, 303 | 0.25 | 0.0890 +/- 0.0114 | 0.0293 +/- 0.0072 | 0.6942 +/- 0.0274 |
| collapse | 301, 302, 303 | 16.0 | 0.0895 +/- 0.0024 | 0.0473 +/- 0.0108 | 0.0209 +/- 0.0081 |
| control | 901, 902, 903, 904, 905 | 0.25 | 0.1008 +/- 0.0211 | 0.0394 +/- 0.0086 | 0.7066 +/- 0.0379 |

The long-time RBF cloud collapses within basins despite moderate sliced error. The width diagnostic preserves this negative result. Reconstructed arrays match the original reported metrics within 1e-4, using tight ODE tolerances.

### Three-method alanine convergence

**Main observation.** The mean BKT error decreases rapidly at small flow times and varies little after approaching its late-time level in this example.

[Convergence PDF](figures/fig_alanine_convergence.pdf). The single-panel comparison uses BKT, LAWGD and KDE, with 1000 particles per method, seeds 1101, 1102, 1103, the same initial/reference clouds and normalized horizon s=8. BKT and LAWGD share 256 nonconstant eigenfunctions; KDE has no spectral truncation.

The retained checkpoint arrays cover [0, 8]. BKT/LAWGD arrays are prefixes of the original s=10 trajectories, with that original horizon recorded in their reuse provenance; KDE is computed directly through s=8.

Both the spectrum and the fixed target KDE use exactly the same `train_all` array: all 250000 frames of trajectory 0. Both target the wrapped-Gaussian-smoothed empirical angle marginal with smoothing 0.1 rad. The spectral fit constructs Gram and Dirichlet matrices from smoothed Fourier moments; the KDE fit approximates the target density and its score on a periodic grid. These are different numerical representations of the same intended measure. Validation/evaluation frames enter neither fit.

The 256 retained eigenfunctions come from the degree-28 Fourier dictionary with 3249 functions. This static Gram/Dirichlet fit estimates the spectrum of a unit-mobility reversible surrogate; it uses no lagged trajectory pairs and does not recover physical MD kinetics. The common reference eigenvalue is lambda1=0.001377599616056442; s=8 corresponds to 5807.202548 units of surrogate diffusion time.

Write the fitted eigenpairs as $(\lambda_k,\phi_k)$. BKT uses $\widehat c_k=M^{-1}\sum_i\phi_k(X_0^i)$, frozen after initialization, and $\widehat\rho_s=1+\sum_k e^{-(\lambda_k/\lambda_1)s}\widehat c_k\phi_k$. Its field is $-\nabla\widehat\rho_s/[\lambda_1\max(\widehat\rho_s,0.001)]$ and requires no explicit target density or score. LAWGD uses the current moments $M^{-1}\sum_i\phi_k(X_s^i)$ and field $-\sum_k\lambda_k^{-1}\nabla\phi_k(X_s^j)M^{-1}\sum_i\phi_k(X_s^i)$. Thus the comparison starts from identical empirical moments. Both alanine figures use these same S-regime trajectories.

**KDE method.** KDE denotes a kernel implementation of the classical diffusion-velocity particle method, dating at least to [Degond and Mustieles (1990)](https://doi.org/10.1137/0911018). The kernel-smoothed velocity is described in [Chertock (2017), Section 4.1.2, equations (33)-(35)](https://chertock.wordpress.ncsu.edu/files/2024/01/Chertock_particles.pdf), [DOI](https://doi.org/10.1016/bs.hna.2016.11.004). Our periodic kernels and numerical solver adapt this framework to the angle data.

All methods use the same reference clock $s=\lambda_1t$. BKT and LAWGD use generator $L/\lambda_1$ and mobility $I/\lambda_1$; LAWGD cancels this scaling between mobility and inverse eigenvalues. KDE uses $dX_s^i/ds=[\nabla\log\widehat\pi(X_s^i)-\nabla\log\widehat q_s(X_s^i)]/\lambda_1$. The target estimate $\widehat\pi$ is fitted once from training frames. The current density $\widehat q_s=M^{-1}\sum_j K_h^{\mathrm{per}}(\cdot-X_s^j)$ uses all evolving particles, including self terms, and is recomputed at each field evaluation. Its fixed isotropic bandwidth h=0.1 rad matches the target smoothing but serves a separate density estimate. This deterministic method interacts through the current particle cloud and uses no Brownian noise.

The displayed grid includes 177 requested particle checkpoints per run through s=8. Metrics are evaluated from the particle states at these times; no error curve is fitted or smoothed. The horizontal axis measures normalized flow time, not physical MD time or computation time. Numerical controls are method-specific.

The fixed target fit uses positive separable periodic Gaussian convolution on a 512-by-512 grid, with a deposition-variance correction; its score is the gradient of a cubic spline interpolating the log density. The evolving particle KDE is evaluated by direct periodic kernel sums. BDF integration uses an analytic particle Jacobian and a finite-difference target-score Jacobian.
The target-density floor is 2.2251e-308, active at 0% of grid nodes. Those nodes contribute 0 to the normalized density-grid quadrature mass. The floor, grid and interpolation remain part of the fitted approximation.

| Method | Recorded numerical controls |
|---|---|
| BKT | DOP853; rtol=1e-08; atol=1e-10; maximum normalized step=0.05; first normalized step=0.0001*lambda1; normalized speed cap=20/lambda1; ratio floor=0.001 |
| LAWGD | DOP853; rtol=1e-08; atol=1e-10; maximum normalized step=0.05; first normalized step=0.0001*lambda1; normalized speed cap=20/lambda1 |
| KDE | solver="BDF; analytic fixed-bandwidth direct particle-kernel Jacobian"; first_step_raw=1e-05; normalized_max_step=0.05; rtol=1e-06; atol=1e-08; kernel="Periodic Gaussian; all current particles including self"; bandwidth=0.1; drift_cap=null; speed_cap=null; kde_density_floor=null; maximum_seconds=7200.0; maximum_evaluations=1000000 |

Saved-cloud verification checked all 1593 retained checkpoints; the maximum SW2/TV discrepancy was 0.


| Method | Completed archived runs | Last common plotted s |
|---|---|---|
| BKT | 3/3 | 8.0 |
| LAWGD | 3/3 | 8.0 |
| KDE | 3/3 | 8.0 |


| KDE numerical check | Recorded diagnostic |
|---|---|
| kde_checks | periodicity_error=2.7089e-14; analytic_gradient_error=1.0166e-09; direct_target_score_maximum_error=0.0055885; direct_particle_score_maximum_error=2.7465e-15; particle_score_periodicity_error=4.8184e-14; particle_jacobian_directional_error=1.3868e-08; short_solver_maximum_coordinate_difference=1.425e-05; status=ok; target_numerical_checks.source_direct_mixture_maximum_error=0.0001528; target_numerical_checks.status=ok; target_numerical_checks.source_seed=1101; target_numerical_checks.fit_metadata.grid_size=512 |


| s | BKT SW2 | LAWGD SW2 | KDE SW2 |
|---|---|---|---|
| 1.0 | 0.0679 +/- 0.0170 | 0.2095 +/- 0.0044 | 0.1477 +/- 0.0043 |
| 2.0 | 0.0621 +/- 0.0181 | 0.0730 +/- 0.0011 | 0.1477 +/- 0.0043 |
| 4.0 | 0.0599 +/- 0.0189 | 0.0542 +/- 0.0208 | 0.1477 +/- 0.0043 |
| 6.0 | 0.0597 +/- 0.0188 | 0.0586 +/- 0.0206 | 0.1477 +/- 0.0043 |
| 8.0 | 0.0597 +/- 0.0188 | 0.0591 +/- 0.0205 | 0.1477 +/- 0.0043 |

BKT approaches the low-error regime substantially earlier than LAWGD. Its mean error then settles smoothly into a steady plateau, while LAWGD shows a modest late rebound. The final displayed BKT and LAWGD errors are similar relative to the between-seed variability.

BKT's mean SW2 changes only from 0.0599 at s=4 to 0.0597 at s=8, illustrating its steady late-time behavior. The main observed benefit is rapid settling followed by a smooth, sustained low-error trajectory.

KDE decreases initially and then settles at a higher observed error: its SW2 is 0.1477 +/- 0.0043 at s=0.5 and 0.1477 +/- 0.0043 at s=8, compared with BKT's 0.0597 +/- 0.0188 at s=8. BKT also reduces error earlier: at s=0.1, its SW2 is 0.0907 +/- 0.0114, versus 0.2041 +/- 0.0047 for KDE. These results describe the retained protocol; they do not isolate the source of KDE's higher plateau.

Rapid convergence here describes the approach to the observed low-error plateau in normalized flow time; steadiness describes the plotted mean error over time. These finite-horizon observations do not establish an asymptotic convergence rate or CPU-time speedup.

Shading is mean +/- sample SD across the three prescribed paired source/reference designs, with one common training dataset and fixed fitted approximations. This variation is not a confidence interval or replication across independent MD datasets. SW2 uses the same 32 fixed directions in the four-dimensional periodic embedding as the main alanine experiment. The comparison uses auxiliary reversible diffusions of the smoothed angular marginal.

**Suggested caption.** Alanine convergence over normalized flow time s in [0, 8]. The mean BKT error decreases rapidly at small flow times and then varies little over the remaining interval. Lines and shading show mean and sample standard deviation of sliced Wasserstein error over three paired source/reference designs, with 1000 particles per method. BKT and LAWGD share 256 nonconstant eigenfunctions and initial empirical coefficients; KDE uses the same training angles and initial/reference clouds. KDE is a classical diffusion-velocity particle method with a fixed estimated target score and feedback through a kernel estimate of the current density. Numerical controls are method-specific. The horizontal axis denotes normalized flow time, not physical MD time or computation time.

## Numerical consistency and interpretation

The retained package contains eleven figure PDFs, one experiment report, fixed configurations and four checksum-verified archives. Koopman (RBF) and Koopman (Legendre) describe the dictionary used for the reversible gEDMD generator estimate; every such curve uses the same BKT transport formula.

Data attribution: the [mdshare alanine page](https://markovmodel.github.io/mdshare/ALA2/) documents the simulations and publication credits, including Nueske et al. (2017), cited in the manuscript. The Computational Molecular Biology Group, Freie Universitaet Berlin, supplies the data under the [mdshare CC BY 4.0 terms](https://markovmodel.github.io/mdshare/). Retained arrays use float64 conversion and the fixed subsampling described above.

The equal-data comparison contains 60 variance-0.3 transports with individual fit and sampling times. The revision section records checks against the original realisations and corresponding main results, including any discrepancy above the requested tolerance. The original alanine distribution/convergence arrays are retained for their figures; additional cost and trajectory-role checks are recorded separately below.

The alanine distribution summary uses the three BKT endpoints at s=8 from the convergence archive, with their original sources and evaluation clouds. The saved input file contains only the 256 retained eigenpairs and the three source/reference designs needed by this experiment. No independent set of Fourier transport results is used for the distribution figure. The RBF controls remain as explicit limitations.

Reference distances describe sampling variability and are not lower bounds for transport. In the equal-data comparison, a reference-threshold crossing uses the reference mean plus one sample standard deviation at a prescribed observation time. The two-dimensional admissible source has harmonic variance 0.3; the uncoupled ten-dimensional source has nine stationary harmonic coordinates of variance 0.5.

FD-201 uses a 201-by-201 grid for two-dimensional systems; the high-dimensional FD comparisons use separable one-dimensional factors. Separable high-dimensional experiments do not establish performance on general coupled targets. The nine-well and coupled-10D limitations remain. The angular-marginal example does not test physical molecular kinetics.

The same-sample comparison requires the stated common-region assumptions. Its coefficient factor is Delta_M = M^(-1/2) sum_k sqrt(Var(phi_k)); bounded individual variances give O(r/sqrt(M)), with possible additional rank dependence in the stability factor. Initial empirical coefficients do not imply exact spectral moments of the transported particles. These numerical checks do not constitute an independent proof review.

## Revision experiments

The fixed B1--B4 protocol retains all prescribed realisations, including failures, with the explicitly requested product correction: index 6 is excluded for source/target seed dependence and index 10 replaces it. No outcome-based seed selection or hyperparameter search is used. Complete arrays, configuration snapshots and execution records are archived under `outputs/revision/` in `double_well.zip`; per-realisation numerical records are also published in `outputs/revision_results.json`. All standard deviations below are sample standard deviations.

### B1. Independent selection of the 10D modes

Candidates satisfy the original generator/lag disagreement condition. Selection uses 100000 independent source points with seed 900+s. Velocity coefficients remain empirical moments of the transported source (seed 500+s). The table is paired within the original seed; it is not an independent replication. Old denotes the legacy selection rule. The additional Legendre training budgets have newly evaluated legacy-rule baselines; only configurations present in the original archive have archived-scalar reproduction checks. Full selected index sets are in the JSON.

| System | Dictionary | n | r | Size | Seed | Old SW2 | New SW2 | Shared modes | Jaccard |
|---|---|---|---|---|---|---|---|---|---|
| A10_beta0.0 | Legendre | 100000 | 16 | default | 0 | 0.0724358 | 0.0760516 | 5 | 0.185185 |
| A10_beta0.0 | Legendre | 100000 | 16 | default | 1 | 0.0677134 | 0.0686326 | 2 | 0.0666667 |
| A10_beta0.0 | Legendre | 10000 | 16 | default | 0 | 0.0846656 | 0.0886308 | 7 | 0.28 |
| A10_beta0.0 | Legendre | 10000 | 16 | default | 1 | 0.0789917 | 0.0777736 | 6 | 0.230769 |
| A10_beta0.0 | Legendre | 200000 | 16 | default | 0 | 0.0702373 | 0.0741498 | 2 | 0.0666667 |
| A10_beta0.0 | Legendre | 200000 | 16 | default | 1 | 0.0708605 | 0.0696603 | 1 | 0.0322581 |
| A10_beta0.0 | RBF | 100000 | 16 | default | 0 | 0.0544383 | 0.0613525 | 11 | 0.52381 |
| A10_beta0.0 | RBF | 100000 | 16 | default | 1 | 0.0605598 | 0.0600746 | 8 | 0.333333 |
| A10_beta0.0 | RBF | 10000 | 16 | default | 0 | 0.07196 | 0.0725737 | 13 | 0.684211 |
| A10_beta0.0 | RBF | 10000 | 16 | default | 1 | 0.0703459 | 0.0627822 | 10 | 0.454545 |
| A10_beta0.0 | RBF | 200000 | 16 | default | 0 | 0.057448 | 0.0608455 | 8 | 0.333333 |
| A10_beta0.0 | RBF | 200000 | 16 | default | 1 | 0.0610086 | 0.0618243 | 10 | 0.454545 |
| A10_beta0.5 | Legendre | 100000 | 16 | default | 0 | 0.213559 | 0.209898 | 14 | 0.777778 |
| A10_beta0.5 | Legendre | 100000 | 16 | default | 1 | 0.228251 | 0.218394 | 15 | 0.882353 |
| A10_beta0.5 | Legendre | 100000 | 16 | 3 | 0 | 0.213559 | 0.209898 | 14 | 0.777778 |
| A10_beta0.5 | Legendre | 100000 | 16 | 4 | 0 | 0.198971 | 0.191349 | 12 | 0.6 |
| A10_beta0.5 | Legendre | 100000 | 32 | 3 | 0 | 0.25695 | 0.212636 | 27 | 0.72973 |
| A10_beta0.5 | Legendre | 100000 | 32 | 4 | 0 | 0.243121 | 0.219833 | 24 | 0.6 |
| A10_beta0.5 | Legendre | 100000 | 64 | 3 | 0 | 0.262981 | 0.325046 | 56 | 0.777778 |
| A10_beta0.5 | Legendre | 100000 | 64 | 4 | 0 | 0.243112 | 0.208359 | 48 | 0.6 |
| A10_beta0.5 | Legendre | 10000 | 16 | default | 0 | 0.309124 | 0.259312 | 8 | 0.333333 |
| A10_beta0.5 | Legendre | 10000 | 16 | default | 1 | 0.279027 | 0.292677 | 10 | 0.454545 |
| A10_beta0.5 | Legendre | 200000 | 16 | default | 0 | 0.211611 | 0.207744 | 13 | 0.684211 |
| A10_beta0.5 | Legendre | 200000 | 16 | default | 1 | 0.21938 | 0.226773 | 13 | 0.684211 |
| A10_beta0.5 | RBF | 100000 | 16 | default | 0 | 0.127551 | 0.111852 | 11 | 0.52381 |
| A10_beta0.5 | RBF | 100000 | 16 | default | 1 | 0.163347 | 0.165747 | 13 | 0.684211 |
| A10_beta0.5 | RBF | 100000 | 16 | 10 | 0 | 0.140339 | 0.145123 | 15 | 0.882353 |
| A10_beta0.5 | RBF | 100000 | 16 | 8 | 0 | 0.127551 | 0.111852 | 11 | 0.52381 |
| A10_beta0.5 | RBF | 100000 | 32 | 10 | 0 | 0.161925 | 0.132053 | 23 | 0.560976 |
| A10_beta0.5 | RBF | 100000 | 32 | 8 | 0 | 0.123205 | 0.103295 | 21 | 0.488372 |
| A10_beta0.5 | RBF | 100000 | 64 | 10 | 0 | 0.127601 | 0.0838256 | 43 | 0.505882 |
| A10_beta0.5 | RBF | 100000 | 64 | 8 | 0 | 0.0838638 | 0.0875645 | 45 | 0.542169 |
| A10_beta0.5 | RBF | 10000 | 16 | default | 0 | 0.150382 | 0.153007 | 13 | 0.684211 |
| A10_beta0.5 | RBF | 10000 | 16 | default | 1 | 0.169686 | 0.161024 | 12 | 0.6 |
| A10_beta0.5 | RBF | 200000 | 16 | default | 0 | 0.189558 | 0.196395 | 14 | 0.777778 |
| A10_beta0.5 | RBF | 200000 | 16 | default | 1 | 0.179565 | 0.200693 | 12 | 0.6 |

### B2. Ten prescribed realisations

The JSON gives all ten values, mean, sample SD and median for each repeated cell. The nine-well Legendre table entry uses the median and exceedance count; its mean and SD remain in the JSON. Rank scans remain on source seed 0, except for the additional four-well Legendre r=32 repetitions. A single run has no sample SD. Original reference samples, ten-pair reference statistics and projection directions are unchanged.

| Experiment / configuration | SW2 mean +/- SD | Median | Above 10 x reference mean | Failed/nonfinite |
|---|---|---|---|---|
| 2D double well; beta=0.25; FD; regime=S; n=0; r=64; h=0.05 | 0.0283141 +/- 0.00227641 | 0.0280915 | 0 | 0 |
| 2D double well; beta=0.25; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.0296133 +/- 0.00254525 | 0.0293376 | 0 | 0 |
| 2D double well; beta=0.25; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0486371 +/- 0.013781 | 0.0450652 | 0 | 0 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0309156 +/- 0.00366935 | 0.0308598 | 0 | 0 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.0363814 +/- 0.004312 | 0.0384364 | 0 | 0 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.0294545 +/- 0.00271547 | 0.0295479 | 0 | 0 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=64; h=0.025 | 0.0290907 +/- 0.00211375 | 0.029059 | 0 | 0 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=64; h=0.05 | 0.0282007 +/- 0.00239512 | 0.0279091 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=64; h=0.025 | 0.029816 +/- 0.0037942 | 0.0296671 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.0288063 +/- 0.00281767 | 0.0290021 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (RBF); regime=I; n=200000; r=64; h=0.025 | 0.0492038 +/- 0.0119019 | 0.0472061 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0475984 +/- 0.0110648 | 0.0458452 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0308453 +/- 0.00390064 | 0.0301603 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.0373033 +/- 0.00768544 | 0.0360426 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=64; h=0.025 | 0.0309135 +/- 0.00409311 | 0.03014 | 0 | 0 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.0305498 +/- 0.00425869 | 0.030038 | 0 | 0 |
| 2D double well; beta=0; FD; regime=S; n=0; r=64; h=0.05 | 0.0266623 +/- 0.00244187 | 0.0263011 | 0 | 0 |
| 2D double well; beta=0; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.027761 +/- 0.00255831 | 0.0271997 | 0 | 0 |
| 2D double well; beta=0; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0486142 +/- 0.0142113 | 0.0466227 | 0 | 0 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0285014 +/- 0.00250153 | 0.0281393 | 0 | 0 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.0345281 +/- 0.00413231 | 0.0348518 | 0 | 0 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.0275993 +/- 0.00274004 | 0.0275923 | 0 | 0 |
| 2D double well; beta=1; FD; regime=S; n=0; r=64; h=0.05 | 0.027169 +/- 0.00180362 | 0.0270002 | 0 | 0 |
| 2D double well; beta=1; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.0278782 +/- 0.00261559 | 0.0274938 | 0 | 0 |
| 2D double well; beta=1; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0426916 +/- 0.00816502 | 0.0382904 | 0 | 0 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0283753 +/- 0.00218023 | 0.0289404 | 0 | 0 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.0532305 +/- 0.0200877 | 0.0467176 | 0 | 0 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.027251 +/- 0.00274179 | 0.0264934 | 0 | 0 |
| 10D double well product, beta=0; FD; n=0; r=16 | 0.0525616 +/- 0.00196185 | 0.0528011 | 0 | 0 |
| 10D double well product, beta=0; Koopman (Legendre); n=100000; r=16 | 0.0724255 +/- 0.00792988 | 0.0707536 | 0 | 0 |
| 10D double well product, beta=0; Koopman (Legendre); n=10000; r=16 | 0.0758538 +/- 0.0107378 | 0.0753038 | 0 | 0 |
| 10D double well product, beta=0; Koopman (Legendre); n=200000; r=16 | 0.0717264 +/- 0.00706789 | 0.0707571 | 0 | 0 |
| 10D double well product, beta=0; Koopman (RBF); n=100000; r=16 | 0.0609666 +/- 0.00204295 | 0.0609229 | 0 | 0 |
| 10D double well product, beta=0; Koopman (RBF); n=10000; r=16 | 0.0683851 +/- 0.00390213 | 0.067667 | 0 | 0 |
| 10D double well product, beta=0; Koopman (RBF); n=200000; r=16 | 0.0603374 +/- 0.00418302 | 0.0611472 | 0 | 0 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=16 | 0.226882 +/- 0.028493 | 0.217275 | 0 | 0 |
| 10D double well, beta=0.5; Koopman (Legendre); n=10000; r=16 | 0.256739 +/- 0.0417839 | 0.248997 | 0 | 0 |
| 10D double well, beta=0.5; Koopman (Legendre); n=200000; r=16 | 0.221224 +/- 0.0199814 | 0.220524 | 0 | 0 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=16 | 0.161302 +/- 0.0337389 | 0.16218 | 0 | 0 |
| 10D double well, beta=0.5; Koopman (RBF); n=10000; r=16 | 0.14804 +/- 0.0298243 | 0.153163 | 0 | 0 |
| 10D double well, beta=0.5; Koopman (RBF); n=200000; r=16 | 0.189804 +/- 0.0267543 | 0.185842 | 0 | 0 |
| 2D nine wells; FD; n=0; r=64 | 0.0327742 +/- 0.00294484 | 0.0326993 | 0 | 0 |
| 2D nine wells; Koopman (Legendre); n=200000; r=64 | Use median / count | 0.477127 | 5 | 0 |
| 2D nine wells; Koopman (RBF); n=100000; r=64 | 0.0561462 +/- 0.00627945 | 0.0555335 | 0 | 0 |
| 2D nine wells; Koopman (RBF); n=10000; r=64 | 0.086626 +/- 0.0240125 | 0.0808079 | 0 | 0 |
| 2D nine wells; Koopman (RBF); n=200000; r=64 | 0.0548159 +/- 0.00631786 | 0.0568503 | 0 | 0 |
| 2D four-well product; FD; n=0; r=64 | 0.0235866 +/- 0.00255507 | 0.0241233 | 0 | 0 |
| 2D four-well product; Koopman (Legendre); n=200000; r=32 | 3.15585 +/- 1.79081 | 2.51425 | 9 | 0 |
| 2D four-well product; Koopman (Legendre); n=200000; r=64 | 0.0263217 +/- 0.00212626 | 0.025542 | 0 | 0 |
| 2D four-well product; Koopman (RBF); n=100000; r=64 | 0.029449 +/- 0.0037221 | 0.0296357 | 0 | 0 |
| 2D four-well product; Koopman (RBF); n=10000; r=64 | 0.0475355 +/- 0.0127954 | 0.0457758 | 0 | 0 |
| 2D four-well product; Koopman (RBF); n=200000; r=64 | 0.0281003 +/- 0.0024227 | 0.0279132 | 0 | 0 |
| 10D OU; gamma=0.15 | 0.019495 +/- 0.000453983 | 0.0194103 | -- | 0 |
| 10D OU; gamma=0 | 0.0218517 +/- 0.000369173 | 0.0218478 | -- | 0 |
| 10D double-well product; Koopman (RBF) | 0.0195091 +/- 0.0021055 | 0.019196 | 0 | 0 |
| 10D double-well product; FD | 0.0151089 +/- 0.000259887 | 0.0151027 | 0 | 0 |
| 10D double-well product; Koopman (Legendre) | 0.0195119 +/- 0.00211656 | 0.0191807 | 0 | 0 |
| 50D double-well product; Koopman (RBF) | 0.0187747 +/- 0.00119452 | 0.0188975 | 0 | 0 |
| 50D double-well product; FD | 0.0157561 +/- 0.000189025 | 0.0158143 | 0 | 0 |
| 50D double-well product; Koopman (Legendre) | 0.0187978 +/- 0.00119715 | 0.0189226 | 0 | 0 |
| 2D double well; beta=0.5; BKT | 0.0305498 +/- 0.00425869 | 0.030038 | -- | 0 |
| 2D double well; beta=0.5; Drift + Langevin | 0.248024 +/- 0.0661021 | 0.256998 | -- | 0 |
| 2D double well; beta=0.5; KDE flow | 0.0476963 +/- 0.0267278 | 0.0377123 | -- | 0 |
| 2D double well; beta=0; BKT | 0.0275993 +/- 0.00274004 | 0.0275923 | -- | 0 |
| 2D double well; beta=0; Drift + Langevin | 0.241766 +/- 0.100975 | 0.217176 | -- | 0 |
| 2D double well; beta=0; KDE flow | 0.039419 +/- 0.0129579 | 0.0348559 | -- | 0 |


| Equal-data configuration | Fit seconds | Sampling seconds | Total seconds |
|---|---|---|---|
| 2D double well; beta=0.5; BKT | 3.24359 +/- 0.0999868 | 5.41934 +/- 0.0871097 | 8.66293 +/- 0.162647 |
| 2D double well; beta=0.5; Drift + Langevin | 1.2957 +/- 0.073622 | 39.1573 +/- 0.555399 | 40.453 +/- 0.579825 |
| 2D double well; beta=0.5; KDE flow | 1.2957 +/- 0.073622 | 44.5982 +/- 0.592039 | 45.8938 +/- 0.632825 |
| 2D double well; beta=0; BKT | 3.12883 +/- 0.523919 | 6.32795 +/- 0.128322 | 9.45677 +/- 0.521346 |
| 2D double well; beta=0; Drift + Langevin | 1.32181 +/- 0.0623496 | 46.4364 +/- 1.33247 | 47.7582 +/- 1.36339 |
| 2D double well; beta=0; KDE flow | 1.32181 +/- 0.0623496 | 52.2958 +/- 1.53228 | 53.6176 +/- 1.54576 |

### B3. Alanine cost and estimation variability

All new costs use one BLAS thread. Spectrum fitting includes the Gram and Dirichlet matrices and eigendecomposition for J=3249. BKT/LAWGD cost repetitions reuse the archived eigenpairs while fitting cost is independently re-measured. Initial moments are timed separately. Input generation and metric callbacks are excluded from transport timings. KDE compilation time is recorded separately in its diagnostics and is also excluded from transport timings.

| Estimation | Fit wall seconds | Fit CPU seconds | Threads |
|---|---|---|---|
| kde_target_fit | 0.169732 | 0.171875 | 1 |
| spectrum_fit0 | 24.6921 | 24.0156 | 1 |
| spectrum_fit1 | 27.0013 | 25.625 | 1 |
| spectrum_fit2 | 28.381 | 26.6719 | 1 |


| Method | Seed | Status | Moments wall / CPU s | Transport wall / CPU s | RHS evaluations | Late SW2 level | First within-band s / wall s |
|---|---|---|---|---|---|---|---|
| BKT | 1101 | ok | 0.0030525 / 0 | 71.0114 / 68.6719 | 22450 | 0.0418894 | 0.6 / 37.873 |
| BKT | 1102 | ok | 0.0030786 / 0 | 75.7524 / 73.8906 | 20569 | 0.0578733 | 0.4 / 37.7395 |
| BKT | 1103 | ok | 0.00274 / 0 | 70.5408 / 68.4375 | 21733 | 0.0793623 | 0.25 / 26.858 |
| KDE | 1101 | ok | 0 / 0 | 954.149 / 927.375 | 23213 | 0.152448 | 0.15 / 786.018 |
| KDE | 1102 | ok | 0 / 0 | 1222.06 / 1184.61 | 23386 | 0.144166 | 0.14 / 934.627 |
| KDE | 1103 | ok | 0 / 0 | 992.982 / 941.891 | 23422 | 0.146634 | 0.14 / 772.868 |
| LAWGD | 1101 | ok | 0.0023534 / 0 | 72.4844 / 70.4531 | 19285 | 0.0388853 | 2.2 / 59.6959 |
| LAWGD | 1102 | ok | 0.0027494 / 0 | 72.5524 / 70.9375 | 19885 | 0.0580191 | 1.95 / 53.8175 |
| LAWGD | 1103 | ok | 0.0031404 / 0 | 65.7019 / 63.0781 | 19789 | 0.0799473 | 1.65 / 49.6585 |

The late level is the time average of checkpoint SW2 on s in [6,8], computed by the trapezoid rule. The first hit is the first prescribed checkpoint within one reference SD of that method's own level. Levels differ between methods, so these hit times are not a common-accuracy comparison.


| Method | Transport wall seconds | Transport CPU seconds | First within-band wall seconds |
|---|---|---|---|
| BKT | 72.4349 +/- 2.88266 | 70.3333 +/- 3.08293 | 34.1568 +/- 6.32135 |
| LAWGD | 70.2462 +/- 3.93562 | 68.1562 +/- 4.40445 | 54.3906 +/- 5.04315 |
| KDE | 1056.4 +/- 144.778 | 1017.96 +/- 144.506 | 831.171 +/- 89.8365 |

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


| IID control seed | Status | Last saved s | SW2 at s=8 | Mass TV at s=8 |
|---|---|---|---|---|
| 1101 | ok | 8.0 | 0.0342785 | 0.023 |
| 1102 | ok | 8.0 | 0.0755378 | 0.039 |
| 1103 | ok | 8.0 | 0.0641764 | 0.06 |


| Source design, original trajectory assignment | SW2 at s=8 | Mass TV at s=8 |
|---|---|---|
| iid | 0.0579976 +/- 0.0213123 | 0.0406667 +/- 0.0185562 |
| sobol | 0.0596977 +/- 0.0188045 | 0.033 +/- 0.0177764 |

### B4. Safeguards per particle path

A particle is counted once if any evaluated stage meets a safeguard. Product rows also record particle-coordinate fractions in the JSON. Caps apply to the Euclidean velocity norm in coupled transport, and to individual coordinate equations for products and rotated OU. Alanine path diagnostics cover BKT, LAWGD and the retained RBF tests. For empirical targets, the filtered distance renormalizes the unaffected cloud and compares it to the complete original target cloud by exact empirical quantile integration for unequal sample counts. Analytic OU cases retain their original Gaussian-reference metric. It is a conditional diagnostic, not the sampler's unconditional accuracy. An empty unaffected cloud has no distance.
For incomplete alanine integrations, mask fractions cover the attempted RHS evaluations, but terminal full/filtered distances are unavailable. Any raw last-checkpoint distance is retained with its checkpoint time and is not substituted for the requested endpoint.

| Experiment / configuration | Floor | Nonpositive | Speed cap | Projection | Any | Full SW2 | Unaffected SW2 |
|---|---|---|---|---|---|---|---|
| 2D double well; beta=0.25; FD; regime=S; n=0; r=128; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.02757 | 0.02757 |
| 2D double well; beta=0.25; FD; regime=S; n=0; r=16; h=0.05 | 0.0005 | 0.0005 | 0.0005 | 0 | 0.0005 | 0.074183 | 0.0740604 |
| 2D double well; beta=0.25; FD; regime=S; n=0; r=32; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0583326 | 0.0583326 |
| 2D double well; beta=0.25; FD; regime=S; n=0; r=64; h=0.05 | 0.00035 +/- 0.000337474 | 0.00035 +/- 0.000337474 | 0.0006 +/- 0.000737865 | 5e-05 +/- 0.000158114 | 0.0006 +/- 0.000737865 | 0.0283141 +/- 0.00227641 | 0.0274686 +/- 0.00196512 |
| 2D double well; beta=0.25; FD; regime=S; n=0; r=8; h=0.05 | 0.0055 | 0.0055 | 0.0055 | 0.004 | 0.0055 | 0.0863713 | 0.0823941 |
| 2D double well; beta=0.25; Koopman (Legendre); regime=S; n=200000; r=16; h=0.05 | 0.0005 | 0.0005 | 0.0005 | 0.0005 | 0.0005 | 0.0748075 | 0.0749032 |
| 2D double well; beta=0.25; Koopman (Legendre); regime=S; n=200000; r=32; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0596554 | 0.0596554 |
| 2D double well; beta=0.25; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.00085 +/- 0.000883491 | 0.00085 +/- 0.000883491 | 0.0013 +/- 0.000948683 | 0.0001 +/- 0.000210819 | 0.0013 +/- 0.000948683 | 0.0296133 +/- 0.00254525 | 0.0288186 +/- 0.00237509 |
| 2D double well; beta=0.25; Koopman (Legendre); regime=S; n=200000; r=96; h=0.05 | 0.001 | 0.001 | 0.001 | 0 | 0.0015 | 0.0292416 | 0.0284627 |
| 2D double well; beta=0.25; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0027 +/- 0.00165328 | 0.0027 +/- 0.00165328 | 0.00315 +/- 0.00193003 | 0.00115 +/- 0.0014729 | 0.00355 +/- 0.00217881 | 0.0486371 +/- 0.013781 | 0.042196 +/- 0.0101008 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0012 +/- 0.0010328 | 0.00115 +/- 0.000914391 | 0.00165 +/- 0.00135503 | 0.00065 +/- 0.000625833 | 0.00195 +/- 0.00123491 | 0.0309156 +/- 0.00366935 | 0.028694 +/- 0.00270615 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.00105 +/- 0.000797566 | 0.00105 +/- 0.000797566 | 0.0017 +/- 0.00100554 | 0.0008 +/- 0.000752773 | 0.0025 +/- 0.000816497 | 0.0363814 +/- 0.004312 | 0.0341758 +/- 0.00483885 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=200000; r=16; h=0.05 | 0 | 0 | 0 | 0.0005 | 0.0005 | 0.0737586 | 0.0737809 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=200000; r=32; h=0.05 | 0 | 0 | 0.001 | 0.0005 | 0.0015 | 0.0572417 | 0.0573593 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.0011 +/- 0.000809664 | 0.0011 +/- 0.000809664 | 0.0018 +/- 0.000918937 | 0.0005 +/- 0.000235702 | 0.0022 +/- 0.000788811 | 0.0294545 +/- 0.00271547 | 0.0278239 +/- 0.00260362 |
| 2D double well; beta=0.25; Koopman (RBF); regime=S; n=200000; r=96; h=0.05 | 0.001 | 0.001 | 0.001 | 0.0005 | 0.0015 | 0.0297212 | 0.028586 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=128; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0269657 | 0.0269657 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=16; h=0.05 | 0.0005 | 0.0005 | 0.0005 | 0 | 0.0005 | 0.0601493 | 0.0603083 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=32; h=0.05 | 0.0005 | 0.0005 | 0.001 | 0 | 0.001 | 0.0537012 | 0.0540746 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=64; h=0.025 | 0.00135 +/- 0.0011559 | 0.00135 +/- 0.0011559 | 0.0024 +/- 0.0011005 | 0 +/- 0 | 0.0024 +/- 0.0011005 | 0.0290907 +/- 0.00211375 | 0.0271241 +/- 0.00174967 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=64; h=0.05 | 0.0004 +/- 0.000394405 | 0.0004 +/- 0.000394405 | 0.0008 +/- 0.000948683 | 0 +/- 0 | 0.0008 +/- 0.000948683 | 0.0282007 +/- 0.00239512 | 0.0274333 +/- 0.0016935 |
| 2D double well; beta=0.5; FD; regime=S; n=0; r=8; h=0.05 | 0.007 | 0.007 | 0.007 | 0 | 0.007 | 0.094142 | 0.0957968 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=16; h=0.05 | 0.0005 | 0.0005 | 0.0005 | 0.0005 | 0.0005 | 0.0630728 | 0.0610987 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=32; h=0.05 | 0.0005 | 0.0005 | 0.001 | 0 | 0.001 | 0.0534263 | 0.0539595 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=64; h=0.025 | 0.00195 +/- 0.00101242 | 0.0019 +/- 0.00102198 | 0.00215 +/- 0.00108141 | 0.00025 +/- 0.000353553 | 0.00215 +/- 0.00108141 | 0.029816 +/- 0.0037942 | 0.0283584 +/- 0.00298649 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.0011 +/- 0.00107497 | 0.0011 +/- 0.00107497 | 0.00155 +/- 0.00114139 | 0.00015 +/- 0.000337474 | 0.00155 +/- 0.00114139 | 0.0288063 +/- 0.00281767 | 0.0281614 +/- 0.00265824 |
| 2D double well; beta=0.5; Koopman (Legendre); regime=S; n=200000; r=96; h=0.05 | 0.0015 | 0.0015 | 0.0015 | 0 | 0.0015 | 0.030213 | 0.0276207 |
| 2D double well; beta=0.5; Koopman (RBF); regime=I; n=200000; r=64; h=0.025 | 0.00315 +/- 0.00170049 | 0.00315 +/- 0.00170049 | 0.00365 +/- 0.00165076 | 0.00125 +/- 0.00108653 | 0.0039 +/- 0.00177639 | 0.0492038 +/- 0.0119019 | 0.0416699 +/- 0.00886701 |
| 2D double well; beta=0.5; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.00255 +/- 0.00162361 | 0.00255 +/- 0.00162361 | 0.0028 +/- 0.00160208 | 0.00115 +/- 0.00105541 | 0.0031 +/- 0.00155991 | 0.0475984 +/- 0.0110648 | 0.0417178 +/- 0.00915501 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0011 +/- 0.00102198 | 0.0011 +/- 0.00102198 | 0.00175 +/- 0.00113652 | 0.00055 +/- 0.000598609 | 0.00205 +/- 0.00106589 | 0.0308453 +/- 0.00390064 | 0.0285166 +/- 0.00235897 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.00125 +/- 0.000824958 | 0.00125 +/- 0.000824958 | 0.00175 +/- 0.000824958 | 0.00065 +/- 0.000579751 | 0.0023 +/- 0.0010328 | 0.0373033 +/- 0.00768544 | 0.0351558 +/- 0.00696612 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=16; h=0.05 | 0.0005 | 0.0005 | 0.0005 | 0.001 | 0.001 | 0.0609485 | 0.0602542 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=32; h=0.05 | 0.0035 | 0.0035 | 0.0055 | 0.001 | 0.0055 | 0.0495187 | 0.0437666 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=64; h=0.025 | 0.0022 +/- 0.0010328 | 0.00215 +/- 0.00105541 | 0.0025 +/- 0.00124722 | 0.00075 +/- 0.000634648 | 0.0028 +/- 0.00118322 | 0.0309135 +/- 0.00409311 | 0.0276159 +/- 0.0025125 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.0011 +/- 0.000875595 | 0.0011 +/- 0.000875595 | 0.00195 +/- 0.000895979 | 0.0007 +/- 0.000537484 | 0.0023 +/- 0.000788811 | 0.0305498 +/- 0.00425869 | 0.0276166 +/- 0.00251827 |
| 2D double well; beta=0.5; Koopman (RBF); regime=S; n=200000; r=96; h=0.05 | 0.001 | 0.001 | 0.001 | 0.0005 | 0.0015 | 0.0287637 | 0.0274331 |
| 2D double well; beta=0; FD; regime=S; n=0; r=128; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0260663 | 0.0260663 |
| 2D double well; beta=0; FD; regime=S; n=0; r=16; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.090494 | 0.090494 |
| 2D double well; beta=0; FD; regime=S; n=0; r=32; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0619205 | 0.0619205 |
| 2D double well; beta=0; FD; regime=S; n=0; r=64; h=0.05 | 0.00025 +/- 0.000263523 | 0.0002 +/- 0.000258199 | 0.00055 +/- 0.000437798 | 5e-05 +/- 0.000158114 | 0.00055 +/- 0.000437798 | 0.0266623 +/- 0.00244187 | 0.0259187 +/- 0.00192767 |
| 2D double well; beta=0; FD; regime=S; n=0; r=8; h=0.05 | 0.0065 | 0.0065 | 0.0065 | 0.0065 | 0.0065 | 0.0879992 | 0.0839346 |
| 2D double well; beta=0; Koopman (Legendre); regime=S; n=200000; r=16; h=0.05 | 0 | 0 | 0 | 0.0005 | 0.0005 | 0.0908816 | 0.0910023 |
| 2D double well; beta=0; Koopman (Legendre); regime=S; n=200000; r=32; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0628798 | 0.0628798 |
| 2D double well; beta=0; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.00095 +/- 0.000926463 | 0.00095 +/- 0.000926463 | 0.0014 +/- 0.00104881 | 0.00015 +/- 0.000337474 | 0.00145 +/- 0.0010395 | 0.027761 +/- 0.00255831 | 0.026751 +/- 0.00251457 |
| 2D double well; beta=0; Koopman (Legendre); regime=S; n=200000; r=96; h=0.05 | 0.0005 | 0.0005 | 0.001 | 0.0005 | 0.001 | 0.0329973 | 0.0266594 |
| 2D double well; beta=0; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0028 +/- 0.00200278 | 0.0028 +/- 0.00200278 | 0.0031 +/- 0.00191195 | 0.00135 +/- 0.00133437 | 0.0037 +/- 0.00226323 | 0.0486142 +/- 0.0142113 | 0.0421378 +/- 0.0116957 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.0012 +/- 0.000856349 | 0.0012 +/- 0.000856349 | 0.0017 +/- 0.000948683 | 0.0008 +/- 0.000537484 | 0.00235 +/- 0.00102875 | 0.0285014 +/- 0.00250153 | 0.0272754 +/- 0.0023784 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.00115 +/- 0.00129207 | 0.00115 +/- 0.00129207 | 0.00205 +/- 0.00138343 | 0.00075 +/- 0.000540062 | 0.00275 +/- 0.00141912 | 0.0345281 +/- 0.00413231 | 0.0340226 +/- 0.00443161 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=200000; r=16; h=0.05 | 0 | 0 | 0 | 0.0005 | 0.0005 | 0.0891133 | 0.0892555 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=200000; r=32; h=0.05 | 0 | 0 | 0 | 0.0005 | 0.0005 | 0.0586644 | 0.0585684 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.00115 +/- 0.000883491 | 0.00115 +/- 0.000883491 | 0.00165 +/- 0.000783511 | 0.00065 +/- 0.000337474 | 0.0023 +/- 0.00071492 | 0.0275993 +/- 0.00274004 | 0.0266443 +/- 0.00274134 |
| 2D double well; beta=0; Koopman (RBF); regime=S; n=200000; r=96; h=0.05 | 0.001 | 0.001 | 0.001 | 0.001 | 0.002 | 0.0282669 | 0.0275757 |
| 2D double well; beta=1; FD; regime=S; n=0; r=128; h=0.05 | 0 | 0 | 0 | 0 | 0 | 0.0235679 | 0.0235679 |
| 2D double well; beta=1; FD; regime=S; n=0; r=16; h=0.05 | 0.0035 | 0.003 | 0.0055 | 0.0005 | 0.0055 | 0.0507249 | 0.0534626 |
| 2D double well; beta=1; FD; regime=S; n=0; r=32; h=0.05 | 0.003 | 0.003 | 0.0045 | 0 | 0.0045 | 0.0403783 | 0.037672 |
| 2D double well; beta=1; FD; regime=S; n=0; r=64; h=0.05 | 0.00095 +/- 0.00283284 | 0.00095 +/- 0.00283284 | 0.0025 +/- 0.00463681 | 0 +/- 0 | 0.0025 +/- 0.00463681 | 0.027169 +/- 0.00180362 | 0.0273986 +/- 0.00247381 |
| 2D double well; beta=1; FD; regime=S; n=0; r=8; h=0.05 | 0.0075 | 0.0075 | 0.0075 | 0 | 0.0075 | 0.132267 | 0.139049 |
| 2D double well; beta=1; Koopman (Legendre); regime=S; n=200000; r=16; h=0.05 | 0.0045 | 0.0045 | 0.0055 | 0.002 | 0.0055 | 0.056463 | 0.0548045 |
| 2D double well; beta=1; Koopman (Legendre); regime=S; n=200000; r=32; h=0.05 | 0.004 | 0.0035 | 0.005 | 0.0005 | 0.005 | 0.0404321 | 0.0414254 |
| 2D double well; beta=1; Koopman (Legendre); regime=S; n=200000; r=64; h=0.05 | 0.00205 +/- 0.00251053 | 0.002 +/- 0.00254951 | 0.00275 +/- 0.00293684 | 0.0002 +/- 0.000349603 | 0.0028 +/- 0.00307499 | 0.0278782 +/- 0.00261559 | 0.0269804 +/- 0.00244462 |
| 2D double well; beta=1; Koopman (Legendre); regime=S; n=200000; r=96; h=0.05 | 0.0015 | 0.0015 | 0.0015 | 0 | 0.0015 | 0.0295986 | 0.0241837 |
| 2D double well; beta=1; Koopman (RBF); regime=I; n=200000; r=64; h=0.05 | 0.0025 +/- 0.00152753 | 0.0025 +/- 0.00152753 | 0.00335 +/- 0.00159948 | 0.00055 +/- 0.000283823 | 0.00355 +/- 0.00157145 | 0.0426916 +/- 0.00816502 | 0.0404108 +/- 0.00760289 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=100000; r=64; h=0.05 | 0.00135 +/- 0.000668747 | 0.00135 +/- 0.000668747 | 0.0021 +/- 0.00104881 | 0.00025 +/- 0.000263523 | 0.00225 +/- 0.00111181 | 0.0283753 +/- 0.00218023 | 0.027159 +/- 0.00248533 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=10000; r=64; h=0.05 | 0.00305 +/- 0.00199235 | 0.00305 +/- 0.00199235 | 0.0039 +/- 0.00217051 | 0.0021 +/- 0.00199722 | 0.00445 +/- 0.0024089 | 0.0532305 +/- 0.0200877 | 0.0380347 +/- 0.00916736 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=200000; r=16; h=0.05 | 0.0055 | 0.0055 | 0.006 | 0.0015 | 0.0065 | 0.0538848 | 0.0549961 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=200000; r=32; h=0.05 | 0.0035 | 0.0035 | 0.004 | 0.001 | 0.0045 | 0.0433104 | 0.040685 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=200000; r=64; h=0.05 | 0.0015 +/- 0.00110554 | 0.0015 +/- 0.00110554 | 0.00215 +/- 0.00129207 | 0.0002 +/- 0.000258199 | 0.0023 +/- 0.00149443 | 0.027251 +/- 0.00274179 | 0.0262936 +/- 0.00260675 |
| 2D double well; beta=1; Koopman (RBF); regime=S; n=200000; r=96; h=0.05 | 0.0015 | 0.0015 | 0.0015 | 0.0005 | 0.002 | 0.0247577 | 0.0226563 |
| 10D double well product, beta=0; FD; n=0; r=16 | 0 +/- 0 | 0 +/- 0 | 0.0011 +/- 0.00119722 | 0.0034 +/- 0.00177639 | 0.0045 +/- 0.00195789 | 0.0525616 +/- 0.00196185 | 0.052576 +/- 0.00218699 |
| 10D double well product, beta=0; Koopman (Legendre); n=100000; r=16 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0.0114 +/- 0.00368782 | 0.0114 +/- 0.00368782 | 0.0724255 +/- 0.00792988 | 0.0704303 +/- 0.0063839 |
| 10D double well product, beta=0; Koopman (Legendre); n=10000; r=16 | 0.0003 +/- 0.000674949 | 0.0003 +/- 0.000674949 | 0.0003 +/- 0.000674949 | 0.0122 +/- 0.00404969 | 0.0122 +/- 0.00404969 | 0.0758538 +/- 0.0107378 | 0.0733715 +/- 0.00741533 |
| 10D double well product, beta=0; Koopman (Legendre); n=200000; r=16 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0.0107 +/- 0.003093 | 0.0107 +/- 0.003093 | 0.0717264 +/- 0.00706789 | 0.0699708 +/- 0.00613677 |
| 10D double well product, beta=0; Koopman (RBF); n=100000; r=16 | 0.0002 +/- 0.000421637 | 0.0002 +/- 0.000421637 | 0.0002 +/- 0.000421637 | 0.0038 +/- 0.00181353 | 0.0038 +/- 0.00181353 | 0.0609666 +/- 0.00204295 | 0.0603618 +/- 0.00386581 |
| 10D double well product, beta=0; Koopman (RBF); n=10000; r=16 | 0.0017 +/- 0.00125167 | 0.0017 +/- 0.00125167 | 0.0017 +/- 0.00125167 | 0.0058 +/- 0.00198886 | 0.0059 +/- 0.00202485 | 0.0683851 +/- 0.00390213 | 0.0680054 +/- 0.00430721 |
| 10D double well product, beta=0; Koopman (RBF); n=200000; r=16 | 0.0003 +/- 0.000674949 | 0.0003 +/- 0.000674949 | 0.0003 +/- 0.000674949 | 0.0037 +/- 0.00182878 | 0.0037 +/- 0.00182878 | 0.0603374 +/- 0.00418302 | 0.0604121 +/- 0.00421275 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=16 | 0.0392 +/- 0.00802496 | 0.0392 +/- 0.00802496 | 0.0392 +/- 0.00802496 | 0.0432 +/- 0.00951957 | 0.0433 +/- 0.00958065 | 0.226882 +/- 0.028493 | 0.0969271 +/- 0.00923501 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=16; degree=3 | 0.046 | 0.046 | 0.046 | 0.048 | 0.049 | 0.209898 | 0.0860138 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=16; degree=4 | 0.024 | 0.024 | 0.024 | 0.037 | 0.037 | 0.191349 | 0.0961116 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=32; degree=3 | 0.041 | 0.041 | 0.041 | 0.045 | 0.045 | 0.212636 | 0.0732775 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=32; degree=4 | 0.034 | 0.034 | 0.035 | 0.049 | 0.049 | 0.219833 | 0.083217 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=64; degree=3 | 0.076 | 0.076 | 0.076 | 0.078 | 0.08 | 0.325046 | 0.0681301 |
| 10D double well, beta=0.5; Koopman (Legendre); n=100000; r=64; degree=4 | 0.03 | 0.03 | 0.03 | 0.043 | 0.043 | 0.208359 | 0.0713199 |
| 10D double well, beta=0.5; Koopman (Legendre); n=10000; r=16 | 0.0434 +/- 0.0116543 | 0.0434 +/- 0.0116543 | 0.0434 +/- 0.0116543 | 0.0489 +/- 0.0137635 | 0.0489 +/- 0.0137635 | 0.256739 +/- 0.0417839 | 0.104876 +/- 0.00877772 |
| 10D double well, beta=0.5; Koopman (Legendre); n=200000; r=16 | 0.0362 +/- 0.00441714 | 0.0362 +/- 0.00441714 | 0.0363 +/- 0.00444847 | 0.0407 +/- 0.00571645 | 0.0407 +/- 0.00571645 | 0.221224 +/- 0.0199814 | 0.0985217 +/- 0.0133327 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=16 | 0.0406 +/- 0.00948918 | 0.0406 +/- 0.00948918 | 0.0406 +/- 0.00948918 | 0.0451 +/- 0.00923099 | 0.0452 +/- 0.0092111 | 0.161302 +/- 0.0337389 | 0.0850587 +/- 0.0096133 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=16; centres per coordinate=10 | 0.03 | 0.03 | 0.03 | 0.037 | 0.037 | 0.145123 | 0.0820493 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=16; centres per coordinate=8 | 0.026 | 0.026 | 0.026 | 0.03 | 0.03 | 0.111852 | 0.0812616 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=32; centres per coordinate=10 | 0.04 | 0.04 | 0.04 | 0.047 | 0.047 | 0.132053 | 0.0717979 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=32; centres per coordinate=8 | 0.034 | 0.034 | 0.034 | 0.038 | 0.038 | 0.103295 | 0.0683818 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=64; centres per coordinate=10 | 0.042 | 0.042 | 0.042 | 0.033 | 0.049 | 0.0838256 | 0.0671374 |
| 10D double well, beta=0.5; Koopman (RBF); n=100000; r=64; centres per coordinate=8 | 0.031 | 0.031 | 0.031 | 0.035 | 0.035 | 0.0875645 | 0.067968 |
| 10D double well, beta=0.5; Koopman (RBF); n=10000; r=16 | 0.0385 +/- 0.00840965 | 0.0385 +/- 0.00840965 | 0.0387 +/- 0.00817924 | 0.0458 +/- 0.00846955 | 0.0463 +/- 0.00847283 | 0.14804 +/- 0.0298243 | 0.0925319 +/- 0.0101158 |
| 10D double well, beta=0.5; Koopman (RBF); n=200000; r=16 | 0.0504 +/- 0.00905784 | 0.0504 +/- 0.00905784 | 0.0505 +/- 0.00888507 | 0.0544 +/- 0.0101017 | 0.0544 +/- 0.0101017 | 0.189804 +/- 0.0267543 | 0.0788761 +/- 0.00692123 |
| 2D nine wells; FD; n=0; r=128 | 0 | 0 | 0.001 | 0 | 0.001 | 0.031656 | 0.0314847 |
| 2D nine wells; FD; n=0; r=16 | 0 | 0 | 0 | 0 | 0 | 0.198522 | 0.198522 |
| 2D nine wells; FD; n=0; r=32 | 0.004 | 0.004 | 0.0055 | 0 | 0.0055 | 0.0490063 | 0.0531254 |
| 2D nine wells; FD; n=0; r=64 | 0 +/- 0 | 0 +/- 0 | 0.00025 +/- 0.000353553 | 0 +/- 0 | 0.00025 +/- 0.000353553 | 0.0327742 +/- 0.00294484 | 0.0326873 +/- 0.00297025 |
| 2D nine wells; FD; n=0; r=8 | 0 | 0 | 0 | 0 | 0 | 0.325452 | 0.325452 |
| 2D nine wells; Koopman (Legendre); n=200000; r=16 | 0.0035 | 0.0035 | 0.0035 | 0 | 0.0035 | 1.55928 | 0.183781 |
| 2D nine wells; Koopman (Legendre); n=200000; r=32 | 0.006 | 0.006 | 0.007 | 0 | 0.007 | 2.34471 | 0.0529569 |
| 2D nine wells; Koopman (Legendre); n=200000; r=64 | 0.00115 +/- 0.0011559 | 0.00115 +/- 0.0011559 | 0.00195 +/- 0.00169066 | 0 +/- 0 | 0.00195 +/- 0.00169066 | 0.875562 +/- 0.993935 | 0.04214 +/- 0.00651862 |
| 2D nine wells; Koopman (Legendre); n=200000; r=8 | 0.002 | 0.002 | 0.002 | 0 | 0.002 | 0.911092 | 0.305506 |
| 2D nine wells; Koopman (Legendre); n=200000; r=96 | 0.004 | 0.004 | 0.0055 | 0 | 0.0055 | 1.88151 | 0.0342864 |
| 2D nine wells; Koopman (RBF); n=100000; r=64 | 0 +/- 0 | 0 +/- 0 | 0.00015 +/- 0.000241523 | 0 +/- 0 | 0.00015 +/- 0.000241523 | 0.0561462 +/- 0.00627945 | 0.0560918 +/- 0.00629311 |
| 2D nine wells; Koopman (RBF); n=10000; r=64 | 0.0005 +/- 0.000942809 | 0.00045 +/- 0.000955975 | 0.00175 +/- 0.00226385 | 0 +/- 0 | 0.00175 +/- 0.00226385 | 0.086626 +/- 0.0240125 | 0.0845047 +/- 0.0216103 |
| 2D nine wells; Koopman (RBF); n=200000; r=16 | 0 | 0 | 0 | 0 | 0 | 0.187693 | 0.187693 |
| 2D nine wells; Koopman (RBF); n=200000; r=32 | 0.002 | 0.002 | 0.0035 | 0 | 0.0035 | 0.0633643 | 0.0644676 |
| 2D nine wells; Koopman (RBF); n=200000; r=64 | 0 +/- 0 | 0 +/- 0 | 0.0001 +/- 0.000210819 | 0 +/- 0 | 0.0001 +/- 0.000210819 | 0.0548159 +/- 0.00631786 | 0.0547655 +/- 0.0063408 |
| 2D nine wells; Koopman (RBF); n=200000; r=8 | 0 | 0 | 0 | 0 | 0 | 0.308754 | 0.308754 |
| 2D nine wells; Koopman (RBF); n=200000; r=96 | 0 | 0 | 0.0005 | 0 | 0.0005 | 0.06242 | 0.062267 |
| 2D four-well product; FD; n=0; r=128 | 0.0005 | 0.0005 | 0.0015 | 0 | 0.0015 | 0.0222348 | 0.022269 |
| 2D four-well product; FD; n=0; r=16 | 0 | 0 | 0 | 0 | 0 | 0.124405 | 0.124405 |
| 2D four-well product; FD; n=0; r=32 | 0.015 | 0.015 | 0.016 | 0 | 0.016 | 0.050665 | 0.0365319 |
| 2D four-well product; FD; n=0; r=3 | 0 | 0 | 0 | 0 | 0 | 0.320537 | 0.320537 |
| 2D four-well product; FD; n=0; r=64 | 0.00185 +/- 0.0011068 | 0.00175 +/- 0.00100692 | 0.0037 +/- 0.00158465 | 0 +/- 0 | 0.0037 +/- 0.00158465 | 0.0235866 +/- 0.00255507 | 0.0232631 +/- 0.00166345 |
| 2D four-well product; FD; n=0; r=8 | 0.002 | 0.002 | 0.002 | 0 | 0.002 | 0.129207 | 0.129454 |
| 2D four-well product; Koopman (Legendre); n=200000; r=16 | 0 | 0 | 0 | 0 | 0 | 0.12806 | 0.12806 |
| 2D four-well product; Koopman (Legendre); n=200000; r=32 | 0.0101 +/- 0.00259058 | 0.0101 +/- 0.00259058 | 0.01055 +/- 0.00253257 | 0 +/- 0 | 0.01055 +/- 0.00253257 | 3.15585 +/- 1.79081 | 0.0416635 +/- 0.00635515 |
| 2D four-well product; Koopman (Legendre); n=200000; r=3 | 0 | 0 | 0 | 0 | 0 | 0.316241 | 0.316241 |
| 2D four-well product; Koopman (Legendre); n=200000; r=64 | 0.0031 +/- 0.00161245 | 0.0031 +/- 0.00161245 | 0.00375 +/- 0.0018893 | 0 +/- 0 | 0.00375 +/- 0.0018893 | 0.0263217 +/- 0.00212626 | 0.0263796 +/- 0.00218535 |
| 2D four-well product; Koopman (Legendre); n=200000; r=96 | 0.0035 | 0.0035 | 0.004 | 0 | 0.004 | 0.0265988 | 0.0259936 |
| 2D four-well product; Koopman (RBF); n=100000; r=64 | 0.002 +/- 0.001 | 0.0019 +/- 0.000936898 | 0.00275 +/- 0.00133853 | 0 +/- 0 | 0.00275 +/- 0.00133853 | 0.029449 +/- 0.0037221 | 0.0296321 +/- 0.00349838 |
| 2D four-well product; Koopman (RBF); n=10000; r=64 | 0.00265 +/- 0.0018265 | 0.00255 +/- 0.00186264 | 0.00375 +/- 0.00253037 | 0 +/- 0 | 0.0038 +/- 0.00252982 | 0.0475355 +/- 0.0127954 | 0.0431665 +/- 0.0103796 |
| 2D four-well product; Koopman (RBF); n=200000; r=16 | 0 | 0 | 0 | 0 | 0 | 0.124909 | 0.124909 |
| 2D four-well product; Koopman (RBF); n=200000; r=32 | 0.009 | 0.009 | 0.0095 | 0 | 0.0095 | 0.0498077 | 0.0478749 |
| 2D four-well product; Koopman (RBF); n=200000; r=3 | 0 | 0 | 0 | 0 | 0 | 0.315282 | 0.315282 |
| 2D four-well product; Koopman (RBF); n=200000; r=64 | 0.00185 +/- 0.000883491 | 0.00185 +/- 0.000883491 | 0.00275 +/- 0.00125277 | 0 +/- 0 | 0.00275 +/- 0.00125277 | 0.0281003 +/- 0.0024227 | 0.0272231 +/- 0.00224717 |
| 2D four-well product; Koopman (RBF); n=200000; r=96 | 0.0025 | 0.0025 | 0.0025 | 0 | 0.0025 | 0.0291222 | 0.0285235 |
| 10D OU; gamma=0.15 | 0.00202 +/- 0.000720802 | 0.00178 +/- 0.000695701 | 0.00242 +/- 0.00103043 | 0 +/- 0 | 0.00258 +/- 0.000995322 | 0.019495 +/- 0.000453983 | 0.0197699 +/- 0.000603168 |
| 10D OU; gamma=0 | 0.00294 +/- 0.000632807 | 0.0025 +/- 0.000749815 | 0.00306 +/- 0.000889694 | 0 +/- 0 | 0.00376 +/- 0.00100133 | 0.0218517 +/- 0.000369173 | 0.0221402 +/- 0.000522666 |
| 1D OU; r=10 | 0.0304 | 0.0303 | 0.0312 | 0 | 0.0318 | 0.0744429 | 0.105993 |
| 1D OU; r=15 | 0.0059 | 0.0058 | 0.0093 | 0 | 0.0094 | 0.0451134 | 0.050934 |
| 1D OU; r=20 | 0.0002 | 0.0002 | 0.0002 | 0 | 0.0002 | 0.0233305 | 0.0257621 |
| 1D OU; r=30 | 0 | 0 | 0 | 0 | 0 | 0.0112483 | 0.0112483 |
| 1D OU; r=40 | 0.0002 | 0.0002 | 0.0001 | 0 | 0.0002 | 0.0144014 | 0.0161104 |
| 1D OU; r=60 | 0.0005 | 0.0005 | 0.0008 | 0 | 0.0008 | 0.0108576 | 0.0151023 |
| 10D double-well product; Koopman (RBF) | 1.5e-05 +/- 2.41523e-05 | 1e-05 +/- 2.10819e-05 | 0.01437 +/- 0.00159203 | 0 +/- 0 | 0.01437 +/- 0.00159203 | 0.0195091 +/- 0.0021055 | 0.0201254 +/- 0.00235418 |
| 10D double-well product; FD | 5e-06 +/- 1.58114e-05 | 5e-06 +/- 1.58114e-05 | 0.0144 +/- 0.00109138 | 0 +/- 0 | 0.0144 +/- 0.00109138 | 0.0151089 +/- 0.000259887 | 0.015655 +/- 0.00036582 |
| 10D double-well product; Koopman (Legendre) | 0 +/- 0 | 0 +/- 0 | 0.01231 +/- 0.00145235 | 0 +/- 0 | 0.01231 +/- 0.00145235 | 0.0195119 +/- 0.00211656 | 0.0200872 +/- 0.002334 |
| 50D double-well product; Koopman (RBF) | 4e-05 +/- 6.58281e-05 | 3.5e-05 +/- 5.29675e-05 | 0.06826 +/- 0.00171007 | 0 +/- 0 | 0.06826 +/- 0.00171007 | 0.0187747 +/- 0.00119452 | 0.0198576 +/- 0.001262 |
| 50D double-well product; FD | 3.5e-05 +/- 5.29675e-05 | 3.5e-05 +/- 5.29675e-05 | 0.068345 +/- 0.00204606 | 0 +/- 0 | 0.068345 +/- 0.00204606 | 0.0157561 +/- 0.000189025 | 0.0168648 +/- 0.000241134 |
| 50D double-well product; Koopman (Legendre) | 5e-06 +/- 1.58114e-05 | 5e-06 +/- 1.58114e-05 | 0.05829 +/- 0.00177338 | 5e-06 +/- 1.58114e-05 | 0.05829 +/- 0.00177338 | 0.0187978 +/- 0.00119715 | 0.019733 +/- 0.00130184 |


| Product configuration: particle-coordinate fractions | Floor | Nonpositive | Speed cap | Projection | Any |
|---|---|---|---|---|---|
| 10D double-well product; Koopman (RBF) | 1.5e-06 +/- 2.41523e-06 | 1e-06 +/- 2.10819e-06 | 0.001445 +/- 0.00016408 | 0 +/- 0 | 0.001445 +/- 0.00016408 |
| 10D double-well product; FD | 5e-07 +/- 1.58114e-06 | 5e-07 +/- 1.58114e-06 | 0.001448 +/- 0.000111186 | 0 +/- 0 | 0.001448 +/- 0.000111186 |
| 10D double-well product; Koopman (Legendre) | 0 +/- 0 | 0 +/- 0 | 0.001236 +/- 0.000147588 | 0 +/- 0 | 0.001236 +/- 0.000147588 |
| 50D double-well product; Koopman (RBF) | 8e-07 +/- 1.31656e-06 | 7e-07 +/- 1.05935e-06 | 0.0014104 +/- 3.47537e-05 | 0 +/- 0 | 0.0014104 +/- 3.47537e-05 |
| 50D double-well product; FD | 7e-07 +/- 1.05935e-06 | 7e-07 +/- 1.05935e-06 | 0.0014125 +/- 4.13206e-05 | 0 +/- 0 | 0.0014125 +/- 4.13206e-05 |
| 50D double-well product; Koopman (Legendre) | 1e-07 +/- 3.16228e-07 | 1e-07 +/- 3.16228e-07 | 0.0011988 +/- 3.59716e-05 | 1e-07 +/- 3.16228e-07 | 0.0011988 +/- 3.59716e-05 |


| Alanine case | Seed | Status | Floor | Nonpositive | Speed cap | Projection | Any | Full cloud SW2 | Unaffected SW2 |
|---|---|---|---|---|---|---|---|---|---|
| cost_BKT_seed1101 | 1101 | ok | 0.001 | 0.001 | 0.005 | 0 | 0.005 | 0.0418771 | 0.040564 |
| cost_BKT_seed1102 | 1102 | ok | 0.001 | 0.001 | 0.004 | 0 | 0.004 | 0.0578643 | 0.0589281 |
| cost_BKT_seed1103 | 1103 | ok | 0.002 | 0.002 | 0.008 | 0 | 0.008 | 0.0793518 | 0.0777545 |
| cost_LAWGD_seed1101 | 1101 | ok | 0 | 0 | 0 | 0 | 0 | 0.0390947 | 0.0390947 |
| cost_LAWGD_seed1102 | 1102 | ok | 0 | 0 | 0 | 0 | 0 | 0.0581399 | 0.0581399 |
| cost_LAWGD_seed1103 | 1103 | ok | 0 | 0 | 0 | 0 | 0 | 0.0800572 | 0.0800572 |
| iid_seed1101 | 1101 | ok | 0 | 0 | 0.002 | 0 | 0.002 | 0.0342785 | 0.034421 |
| iid_seed1102 | 1102 | ok | 0 | 0 | 0.004 | 0 | 0.004 | 0.0755378 | 0.0748402 |
| iid_seed1103 | 1103 | ok | 0.001 | 0.001 | 0.007 | 0 | 0.007 | 0.0641764 | 0.0634059 |
| rbf_collapse_seed301 | 301 | ok | 0.026 | 0.026 | 0.026 | 0 | 0.026 | 0.0885164 | 0.103769 |
| rbf_collapse_seed302 | 302 | ok | 0.023 | 0.023 | 0.023 | 0 | 0.023 | 0.0877488 | 0.103005 |
| rbf_collapse_seed303 | 303 | ok | 0.018 | 0.018 | 0.018 | 0 | 0.018 | 0.0922651 | 0.102276 |
| rbf_control_seed901 | 901 | ok | 0.02 | 0.02 | 0.02 | 0 | 0.02 | 0.129344 | 0.158455 |
| rbf_control_seed902 | 902 | ok | 0.024 | 0.024 | 0.024 | 0 | 0.024 | 0.0983078 | 0.137478 |
| rbf_control_seed903 | 903 | ok | 0.024 | 0.024 | 0.025 | 0 | 0.025 | 0.113633 | 0.147856 |
| rbf_control_seed904 | 904 | ok | 0.02 | 0.019 | 0.02 | 0 | 0.02 | 0.0860193 | 0.107689 |
| rbf_control_seed905 | 905 | ok | 0.027 | 0.027 | 0.028 | 0 | 0.028 | 0.0767121 | 0.0949613 |
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

### Reproduction and protocol notes

503 endpoint/scalar checks were recorded; 4 did not satisfy the requested reproduction check (tolerance 1e-12, with missing completed endpoints also flagged). B1 deliberately changes the mode set; its new endpoint is not expected to equal the legacy endpoint.

The separate saved-array audit recomputed 774 endpoint distances and checked 3585 masks, including their unions and reported fractions. The maximum absolute difference in the full or filtered distances was 8.88e-16.

The unchanged alanine figure data were separately verified at all 1593 stored checkpoints over 9 curves; the maximum saved-metric difference was 0. Their stored and current numerical-code fingerprints are reported separately because the B4 observations change the source code. Solver reproduction is covered by the checks above.

Hardware: Intel(R) Core(TM) i9-14900K, 24 physical cores, 32 logical processors, 63.7 GiB RAM. All numerical stages use one BLAS thread. Products retain eight coordinate workers per repetition. The queue may run four independent synthetic repetitions or two product repetitions concurrently; the equal-data comparison and alanine cost measurements run alone. Concurrent timings are descriptive. Stage wall times include the task's input/metric work but exclude the final archive repacking. Only the dedicated equal-data and alanine cost runs give freshly measured sampler costs; other elapsed fields may include cache access.

| Task | Run | Check |
|---|---|---|
| alanine_original_assignment_refit | rotation_fit0_eval2_seed1101 | {'endpoint_bitwise_equal': False, 'endpoint_max_absolute_difference': 4.518925985852462e-06, 'max_checkpoint_cloud_difference': 7.089551102490432e-05, 'max_checkpoint_sw2_difference': 3.551418938790851e-08, 'requested_horizon_completed': True, 'passes_1e12': False, 'scope': 'Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.'} |
| alanine_original_assignment_refit | rotation_fit0_eval2_seed1102 | {'endpoint_bitwise_equal': False, 'endpoint_max_absolute_difference': 3.822091440675024e-06, 'max_checkpoint_cloud_difference': 0.000850465561576641, 'max_checkpoint_sw2_difference': 1.3822372150334994e-07, 'requested_horizon_completed': True, 'passes_1e12': False, 'scope': 'Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.'} |
| alanine_original_assignment_refit | rotation_fit0_eval2_seed1103 | {'endpoint_bitwise_equal': False, 'endpoint_max_absolute_difference': 7.1358525630671465e-06, 'max_checkpoint_cloud_difference': 4.5597218975679255e-05, 'max_checkpoint_sw2_difference': 2.059280550248399e-08, 'requested_horizon_completed': True, 'passes_1e12': False, 'scope': 'Original trajectory assignment with the requested single-thread spectrum refit, compared with the archived spectrum and clouds. This is a refit sensitivity check, not an instrumentation-only comparison.'} |
| alanine_single_thread_refit | spectrum_fit0 | {'maximum_eigenvalue_absolute_difference': 1.2153662964919931e-08, 'maximum_eigenvalue_relative_difference': 8.284119113814352e-10, 'eigenvalues_above_absolute_tolerance': 246, 'lambda1_absolute_difference': 1.1412199310556481e-12, 'passes_1e12': False, 'scope': 'Requested single-thread refit versus archived spectrum. Cost transports retain archived eigenpairs; role rotations use the refit. Eigenvector signs are not compared as numerical errors.'} |


- B5 was not run.
- Rank scans use the first source seed; the four-well Legendre r=32 instability additionally has ten realisations.
- The listed B2 OU extension concerns the 10D experiment. The original 1D rank, time and particle-count curves retain their single-cloud design; B4 adds the requested r=40 path diagnostics.
- Products preserve eight independent coordinate workers and one BLAS thread; their timings are descriptive.
- The product correction excludes index s=6, whose source seed 7 coincided with the fixed target seed. Current summaries use s=0--5,7--10, including the new source seed 11 and training seed 1011. Original index-6 records remain historical audit inputs and are absent from current aggregates. Every active source seed differs from target seed 7; first-coordinate rank-order checks are recorded.
- Independent synthetic repetitions may run in four processes (two for products). The equal-data and alanine cost stages run alone. Concurrent timing records are not sampler-speed comparisons.
- The three alanine spectra are fitted sequentially. After fitting, the eighteen independent role-rotation transports may run in four single-BLAS-thread processes; those transport timings are descriptive.
- The generic 64-direction, seed-0 metric and ten-pair reference rule applies to the synthetic empirical-target tests. Alanine preserves its archived 32 directions (seed 2026) in the four-dimensional periodic embedding and the three paired reference designs; analytic OU uses the Gaussian reference. These existing exceptions were not silently changed.
- Product and rotated-OU safeguards act on one-dimensional factors: their ratio floors are factor-wise, and the reported particle fraction is the union over coordinates.
- Fixed-step notebook transports retain int(round(T/h)) full steps. Requested and effective horizons can therefore differ by at most half a step. In the 10D/50D products, requested T=10.685414859800558 gives 534 steps of h=0.02 and effective time 10.68. The main 2D and equal-data horizons are already rounded to the step grid; adaptive alanine runs target s=8 exactly.
- Product projections occur only at completed steps. Boxed 2D/10D double wells project the trial arguments of RK stages 2--4 and each completed endpoint; stage 1 uses the stored state, and the initial source is not pre-projected. Full-plane multiwells and OU have no such projection.
- The prescribed 10D source retains harmonic-coordinate variance 0.5. At positive coupling its full-space density ratio is unbounded; B1 fixes independence of the selected modes, while this source/domain limitation remains.
- All adaptive RHS evaluations are observed, including rejected and dense-output stages. Torus wrapping is not a boundary projection.
- Safeguard fractions monitor evaluated numerical stages, not exact continuous-time hitting probabilities. Projection counts refer to explicit clipping and do not certify containment in a theoretical admissible region.
- Six ordered trajectory pairs share three fits and three evaluation trajectories; their sample SD is descriptive, not an independent-data standard error.
- Role rotations jointly change the fitted spectrum, training-derived source and basin partition, and evaluation trajectory. Their spread does not isolate spectral estimation error alone.
- The latest manuscript source is not present in this checkout. Numerical changes are indexed by experiment and stored entry; exact section/table placement requires the current manuscript.

Double-well and multiwell repetitions use training seed 100+s and source seed 500+s, with target seed 7 fixed. Exceptions are analytic FD (no learned trajectory), analytic OU (source seeds 700--709 in 10D), separable products (training 1001+s, source 1+s), matched OU paths (its retained SeedSequence convention), and alanine (the explicitly recorded MD assignments and designs). Thus the blanket seed statement does not apply to every experiment.

| Task execution | Wall seconds |
|---|---|
| B1/B2/B4: 10D double wells | 7139.39 |
| B2/B4: 2D double wells | 1033.65 |
| B3(a)/B4: alanine costs | 3631 |
| B3(c)/B4: iid control | 211.139 |
| B4: retained alanine RBF cases | 142.853 |
| B3(b)/B4: trajectory rotations | 1188.41 |
| B2: equal-data comparison | 2058.87 |
| B2/B4: four and nine wells | 1295.27 |
| B2/B4: OU | 116.605 |
| B2/B4: 10D product | 2116.92 |
| B2/B4: 50D product | 10170.2 |

Shared numerical work is timed once under its joint task label. B1, B2 and B4 use some of the same transports, so their execution times cannot be added as independent costs. Cache-only resumes retain the original measured work and are listed separately in the execution history.


## Group-B follow-up

The optional confined four- and nine-well runs were not performed. All unconfined multiwell results remain unchanged. This follow-up corrects the product seed dependence and diagnoses the three distinct integrations fitted on trajectory 3. Trajectories are numbered 1--3 here; JSON indices remain 0--2.

### Product seed correction

Current indices are s=0--5,7--10, with source seed 1+s and training seed 1001+s. Index 6 is excluded because source and target both used seed 7. Index 10 uses source 11 and training 1011. The other nine realisations, target seed 7, reference samples and projection directions are unchanged. The six excluded method/system records are historical audit inputs only; they enter no current table or figure.

| Dimension | Spectrum | Previous SW2 mean +/- SD | Corrected SW2 mean +/- SD | Removed s=6 | Added s=10 | Reference |
|---|---|---|---|---|---|---|
| 10 | FD | 0.014392 +/- 0.00211542 | 0.0151089 +/- 0.000259887 | 0.00839933 | 0.0155683 | 0.0156084 +/- 0.00135219 |
| 10 | Koopman (RBF) | 0.0192123 +/- 0.00269586 | 0.0195091 +/- 0.0021055 | 0.0135792 | 0.0165473 | 0.0156084 +/- 0.00135219 |
| 10 | Koopman (Legendre) | 0.0192175 +/- 0.0026997 | 0.0195119 +/- 0.00211656 | 0.0135993 | 0.0165428 | 0.0156084 +/- 0.00135219 |
| 50 | FD | 0.01495 +/- 0.00256235 | 0.0157561 +/- 0.000189025 | 0.00767723 | 0.0157391 | 0.0162215 +/- 0.00080525 |
| 50 | Koopman (RBF) | 0.0179151 +/- 0.00239346 | 0.0187747 +/- 0.00119452 | 0.0117948 | 0.0203913 | 0.0162215 +/- 0.00080525 |
| 50 | Koopman (Legendre) | 0.0179415 +/- 0.00239189 | 0.0187978 +/- 0.00119715 | 0.0118346 | 0.0203981 | 0.0162215 +/- 0.00080525 |

The six mean errors increase by 1.53%--5.39% after removal of the dependent source/target pair. The correction is required by the sampling protocol, independently of its effect on the errors.

The product PDFs retain the first realisation in the marginal histograms and use the corrected ten-realisation mean and sample SD in the marginal-W2 panels. The old-to-new list below explicitly labels changes relative to the previous group-B ten-realisation results.

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
The audit verified that all 42 original alanine files and 54 retained product records are unchanged. Original saved retry checkpoints are bitwise identical, and their floor/cap masks are subsets of the extended masks. The maximum recomputed grid/endpoint diagnostic difference is 0.
Follow-up jobs run concurrently with one BLAS thread each; the product tasks retain eight coordinate workers. Their elapsed times describe this execution and are not sampler speed comparisons.

### Manuscript numbers: old -> new

Entries identify the exact stored numerical quantity. All repeated table values, sample-size summaries, coefficient comparisons, costs, threshold counts, product diagnostics, OU time summaries and the 10D dictionary/rank scan must be taken from the updated report/JSON. Entries beginning with Product seed correction compare the previous group-B ten-realisation result with the corrected ten-realisation result; other entries compare the original pre-revision baseline with the current result. The latest manuscript source was not available in this checkout for a literal cross-reference audit.

| Numerical entry | Old | New |
|---|---|---|
| B_poly9 / Legendre / displayed table statistic | 1.46514 +/- 1.33534 (mean +/- sample SD; 3 realisations) | median 0.477127; 5/10 above ten times the reference mean |
| product_50 / legendre / displayed table statistic | 0.0170652 (one source cloud) | 0.0187978 +/- 0.00119715 (ten source clouds) |
| product_50 / estimated / displayed table statistic | 0.0170181 (one source cloud) | 0.0187747 +/- 0.00119452 (ten source clouds) |
| product_50 / exact / displayed table statistic | 0.0153473 (one source cloud) | 0.0157561 +/- 0.000189025 (ten source clouds) |
| product_10 / legendre / displayed table statistic | 0.0200019 (one source cloud) | 0.0195119 +/- 0.00211656 (ten source clouds) |
| product_10 / estimated / displayed table statistic | 0.0199887 (one source cloud) | 0.0195091 +/- 0.0021055 (ten source clouds) |
| product_10 / exact / displayed table statistic | 0.0149277 (one source cloud) | 0.0151089 +/- 0.000259887 (ten source clouds) |
| A10_beta0.0 / FD / displayed table statistic | 0.0543734 (one source cloud) | 0.0525616 +/- 0.00196185 (ten source clouds) |
| B_poly9 / FD / displayed table statistic | 0.0363959 (one source cloud) | 0.0327742 +/- 0.00294484 (ten source clouds) |
| B_quartic4 / FD / displayed table statistic | 0.023747 (one source cloud) | 0.0235866 +/- 0.00255507 (ten source clouds) |
| results.json/A10_beta0.0/fd/sw | 0.0543734 | 0.0525616 |
| results.json/A10_beta0.0/poly/mean | 0.0700746 | 0.0724255 |
| results.json/A10_beta0.0/poly/std | 0.00333929 | 0.00792988 |
| results.json/A10_beta0.0/poly/sw | [0.07243584945204459, 0.06771338658298917] | [0.07605158527320204, 0.06863260179730753, 0.0657487743827252, 0.09154462294446215, 0.07352638010085483, 0.06523232420803204, 0.07656268020094022, 0.07287464872197574, 0.06716084612840202, 0.06692054708728046] |
| results.json/A10_beta0.0/rbf/mean | 0.057499 | 0.0609666 |
| results.json/A10_beta0.0/rbf/std | 0.00432855 | 0.00204295 |
| results.json/A10_beta0.0/rbf/sw | [0.05443825273076714, 0.06055975303679998] | [0.06135252218580196, 0.0600745858497381, 0.0603362505287361, 0.057969093867249764, 0.06058004246011555, 0.061919933197185445, 0.06126576749283852, 0.06483999668609457, 0.06299872358097333, 0.05832931483912632] |
| results.json/A10_beta0.0/seeds | 2 | 10 |
| results.json/A10_beta0.5/poly/mean | 0.220905 | 0.226882 |
| results.json/A10_beta0.5/poly/std | 0.0103892 | 0.028493 |
| results.json/A10_beta0.5/poly/sw | [0.2135589065911711, 0.22825140999901172] | [0.2098976156982, 0.21839400126815428, 0.2068485485604107, 0.2991119069683609, 0.21615577450935758, 0.24208456062241393, 0.23805013525330632, 0.2003167898738585, 0.2225942126135534, 0.21536427052841112] |
| results.json/A10_beta0.5/rbf/mean | 0.145449 | 0.161302 |
| results.json/A10_beta0.5/rbf/std | 0.0253117 | 0.0337389 |
| results.json/A10_beta0.5/rbf/sw | [0.12755077276079854, 0.1633468981531873] | [0.11185186484412252, 0.16574698210855396, 0.23140020814312098, 0.15614834633936994, 0.15861331965418954, 0.15537947503602267, 0.11372670330009055, 0.17441179108228666, 0.17973244135220795, 0.16600814723515075] |
| results.json/A10_beta0.5/seeds | 2 | 10 |
| results.json/B_poly9/poly/mean | 1.46514 | 0.875562 |
| results.json/B_poly9/poly/std | 1.33534 | 0.993935 |
| results.json/B_poly9/poly/sw | [1.6372745202322363, 2.706057232625716, 0.05207653922148804] | [1.6372745202322363, 2.706057232625716, 0.05207653922148804, 0.04807241906386592, 0.9021773724108698, 1.2565249546886987, 2.037523660258595, 0.035593848387423674, 0.0446563173885512, 0.035664041023746894] |
| results.json/B_poly9/rbf/mean | 0.0610299 | 0.0548159 |
| results.json/B_poly9/rbf/std | 0.00261029 | 0.00631786 |
| results.json/B_poly9/rbf/sw | [0.0626797007300946, 0.05802045820923506, 0.06238954300113843] | [0.0626797007300946, 0.05802045820923506, 0.06238954300113843, 0.059704790572816906, 0.058056392011570375, 0.0466129094176352, 0.04932165041001908, 0.04785171024001371, 0.05568007436887829, 0.047841334275570496] |
| results.json/B_poly9/seeds | 3 | 10 |
| results.json/B_quartic4/poly/mean | 0.0269461 | 0.0263217 |
| results.json/B_quartic4/poly/std | 0.00198069 | 0.00212626 |
| results.json/B_quartic4/poly/sw | [0.027393104566550995, 0.02479217844260736, 0.025256164759296453, 0.029700060165785438, 0.027588854265386063] | [0.027393104566550995, 0.02479217844260736, 0.025256164759296453, 0.029700060165785438, 0.027588854265386063, 0.023757383459167225, 0.025814454649282982, 0.025269484970741857, 0.029525127296319703, 0.024120556440982176] |
| results.json/B_quartic4/rbf/mean | 0.0280856 | 0.0281003 |
| results.json/B_quartic4/rbf/std | 0.00212832 | 0.0024227 |
| results.json/B_quartic4/rbf/sw | [0.02862933623219842, 0.026330059640780938, 0.02610378714217232, 0.03137271669734311, 0.027992290142804827] | [0.02862933623219842, 0.026330059640780938, 0.02610378714217232, 0.03137271669734311, 0.027992290142804827, 0.025726176679557466, 0.02863822258048067, 0.032817183568993956, 0.027834159038523335, 0.025558743654060474] |
| results.json/B_quartic4/seeds | 5 | 10 |
| results.json/_config/seeds | [5, 3, 2] | [10, 10, 10] |
| product_10_results.json/methods/estimated/energy | 0.00520069 | 0.00497058 |
| product_10_results.json/methods/estimated/marginal_w2 | [0.027433713441126144, 0.016268495178714763, 0.020901599631724405, 0.00978132922717004, 0.0166206916212897, 0.010331685325560877, 0.03908376159183636, 0.007671866947358642, 0.03132034532610903, 0.0156962601392145] | [0.014839292034191093, 0.011894010631907485, 0.022834600851959153, 0.017026771942019497, 0.016180693329977708, 0.016950621571155997, 0.0201767527605607, 0.017923342699577557, 0.020132476537553887, 0.02349037465892224] |
| product_10_results.json/methods/estimated/max_marginal | 0.0390838 | 0.0356087 |
| product_10_results.json/methods/estimated/negative_count_tv | 0.01315 | 0.00917 |
| product_10_results.json/methods/estimated/sw | 0.0199887 | 0.0195091 |
| product_10_results.json/methods/exact/energy | 0.00515489 | 0.00471939 |
| product_10_results.json/methods/exact/marginal_w2 | [0.010304471867098567, 0.008104158333780852, 0.01377998911803455, 0.009244701996570634, 0.012101174059222706, 0.009319476872704137, 0.015060596695981216, 0.01464784425050507, 0.012132472208101541, 0.0186346455778161] | [0.010314473903732057, 0.007811852725458787, 0.015185800181561676, 0.009127012424436306, 0.012259482636412014, 0.009744166106542173, 0.01462573792271391, 0.014731127117005383, 0.014326481065455185, 0.018786947404594585] |
| product_10_results.json/methods/exact/max_marginal | 0.0186346 | 0.0187869 |
| product_10_results.json/methods/exact/negative_count_tv | 0.01035 | 0.008045 |
| product_10_results.json/methods/exact/sw | 0.0149277 | 0.0151089 |
| product_10_results.json/methods/legendre/energy | 0.0052048 | 0.00497257 |
| product_10_results.json/methods/legendre/marginal_w2 | [0.027316505753737726, 0.015611485392381259, 0.02062237627646375, 0.009329878879139093, 0.016483241441734835, 0.010523804800563604, 0.03999499788738762, 0.008759013593273014, 0.030554933525431056, 0.015986239271232106] | [0.0147050932914489, 0.012028760311609982, 0.023225250489163025, 0.016903729414967504, 0.015818796250719337, 0.017077586664949792, 0.020144371574710437, 0.017997795910296176, 0.020028484223772285, 0.023365727715751718] |
| product_10_results.json/methods/legendre/max_marginal | 0.039995 | 0.0353526 |
| product_10_results.json/methods/legendre/negative_count_tv | 0.01295 | 0.008995 |
| product_10_results.json/methods/legendre/sw | 0.0200019 | 0.0195119 |
| product_50_results.json/methods/estimated/energy | 0.010649 | 0.0116048 |
| product_50_results.json/methods/estimated/marginal_w2 | [0.011063099863092774, 0.006486871169299771, 0.009937815121354986, 0.011586815611280213, 0.01611371301970381, 0.012256386158469976, 0.008002669859983613, 0.014740699052293782, 0.016696705889778226, 0.009481098743236254, 0.02305275669186585, 0.011095707771491228, 0.01428842551505334, 0.02125973530528743, 0.014170854772883193, 0.010034195185986609, 0.013006084972214789, 0.020182906567478398, 0.009176950310678325, 0.008435716694393079, 0.00912931924462374, 0.011122752063537151, 0.01513936884294614, 0.007494446621570438, 0.007483418316255387, 0.015653874243352038, 0.005755013828320345, 0.016567909418074483, 0.008359338248860667, 0.009783479020547589, 0.012678507430436763, 0.009518321214620047, 0.006132396112705298, 0.019510831560503986, 0.02019801736498768, 0.028351747902397775, 0.006548695134322255, 0.01081262800606727, 0.012427413999235781, 0.018499482729850542, 0.011742180552261871, 0.008931307039688417, 0.025202592368975357, 0.014445055750684563, 0.013926101772770455, 0.015051329466930862, 0.007207908964894715, 0.039342088060933485, 0.013552997829020143, 0.010481903769055154] | [0.013637734622632508, 0.0143214282683959, 0.018104547824076507, 0.013682645024135753, 0.01908443950471485, 0.014791058250071352, 0.016248237384894393, 0.015002929801553735, 0.021530639521864667, 0.018102275068037715, 0.0146847958165786, 0.013110470708859059, 0.01675024810542659, 0.01610169198599607, 0.020646739680549482, 0.020189810323666155, 0.012548995135118812, 0.015012465758022278, 0.015034470389814064, 0.01923850947457037, 0.012486406645265746, 0.01314491676892513, 0.015548641728574985, 0.012140656652139226, 0.011911964644107287, 0.010796886730243977, 0.01527936378882502, 0.016980663661712296, 0.016192707100540733, 0.012077597337782605, 0.015011904688049157, 0.016825976004601083, 0.01792062880523708, 0.015413243964943516, 0.018800292454271783, 0.019216248860267435, 0.013220426480957295, 0.019532312322573086, 0.01472130160065976, 0.014002160675437853, 0.017740710946675446, 0.017056108050948964, 0.019533614616845208, 0.013208478766050491, 0.016383706001563893, 0.01349502401231297, 0.016904146297788573, 0.02089711612110246, 0.01539897567423655, 0.012305022958045735] |
| product_50_results.json/methods/estimated/max_marginal | 0.0393421 | 0.0386993 |
| product_50_results.json/methods/estimated/negative_count_tv | 0.01745 | 0.019095 |
| product_50_results.json/methods/estimated/sw | 0.0170181 | 0.0187747 |
| product_50_results.json/methods/exact/energy | 0.0104668 | 0.0111055 |
| product_50_results.json/methods/exact/marginal_w2 | [0.010304471867098567, 0.008104158333780852, 0.01377998911803455, 0.009244701996570634, 0.012101174059222706, 0.009319476872704137, 0.015060596695981216, 0.01464784425050507, 0.012132472208101541, 0.0186346455778161, 0.009627510017325825, 0.014755583199719974, 0.00880987589527219, 0.010374783705456607, 0.009855366479913084, 0.011038554211184338, 0.010079015670927165, 0.012854081509162911, 0.010146307751255267, 0.006569482930439642, 0.0074601837055115255, 0.009460457895714258, 0.007486311282732185, 0.010154027673254302, 0.010013784611094489, 0.007868487494449952, 0.007352230008008125, 0.007337452539002316, 0.010537194521024446, 0.010691516641339755, 0.008645890607113123, 0.008965637309457583, 0.01618984060154886, 0.0065841648462268395, 0.01110148181484753, 0.012618946062494793, 0.00705044011333416, 0.01792648104491547, 0.010195254225192352, 0.009859999538447952, 0.008839742303368831, 0.008468047451829904, 0.020760701904037195, 0.00993852957410275, 0.008278894364276217, 0.009121045270305096, 0.014470743944466919, 0.009897733599121309, 0.01158605799795407, 0.007987274174075682] | [0.010314473903732057, 0.007811852725458787, 0.015185800181561676, 0.009127012424436306, 0.012259482636412014, 0.009744166106542173, 0.01462573792271391, 0.014731127117005383, 0.014326481065455185, 0.018786947404594585, 0.009689602213505611, 0.013919465882261626, 0.007969216886265262, 0.010018485900896008, 0.010307623516001169, 0.012860454612056477, 0.00915663849556914, 0.012292949928081746, 0.010715217183430058, 0.007239369876922845, 0.008362984620342103, 0.008360717759613414, 0.007952572007676014, 0.0103753235525802, 0.01059639257707679, 0.00914043246569236, 0.008068611852306912, 0.008124154719448811, 0.01133334552984165, 0.008877940108970302, 0.009193570357628309, 0.008172426798111535, 0.019217085382540088, 0.0070635077078232255, 0.011188234770436688, 0.014394713672620107, 0.007351101853072126, 0.01753642793235032, 0.010267459181851868, 0.008106421501037719, 0.008160973753030374, 0.009215171461027698, 0.018567404176783337, 0.00895569575265245, 0.008243288474400205, 0.00890885683658495, 0.014892763493122027, 0.009182799345635883, 0.010387348245746232, 0.00730673830268475] |
| product_50_results.json/methods/exact/max_marginal | 0.0207607 | 0.020056 |
| product_50_results.json/methods/exact/negative_count_tv | 0.0199 | 0.0191 |
| product_50_results.json/methods/exact/sw | 0.0153473 | 0.0157561 |
| product_50_results.json/methods/legendre/energy | 0.0106474 | 0.0116055 |
| product_50_results.json/methods/legendre/marginal_w2 | [0.010852601959981265, 0.006214116217660498, 0.009694674011434605, 0.011288015393463816, 0.01569853573378763, 0.012428635932776402, 0.008668568320591418, 0.014944127232366043, 0.01799801339932041, 0.008944527492874185, 0.022328767669469583, 0.009344016423789408, 0.013032050907414498, 0.021279102652507924, 0.014151237328277725, 0.01072540642648581, 0.012422344438441242, 0.020623037498176046, 0.009491040927161416, 0.008302658997059828, 0.007864831479495214, 0.010823113659399858, 0.01428597010034633, 0.006659072151598018, 0.007451949960046604, 0.015464585291118988, 0.0057312360752144595, 0.01708823334039001, 0.007747813472312597, 0.009882116443319626, 0.013026029092291539, 0.009675697859914342, 0.007489945484621725, 0.019884811913307876, 0.02107297143932849, 0.028853395219894332, 0.006481744646428645, 0.010972420857383276, 0.01250324347399574, 0.018884886195128802, 0.011977986422876057, 0.008633449649974399, 0.025264179215607124, 0.013646110595818503, 0.012028206818778352, 0.014342364838331007, 0.006885604686397275, 0.03925845082331231, 0.013359935742228221, 0.010618195036363342] | [0.013804508548796852, 0.014402117508285284, 0.018216578510859643, 0.013721308641010755, 0.018492812762565862, 0.014781961154494334, 0.016489838762679922, 0.015243508415985018, 0.021654780560812513, 0.017853341632197924, 0.014628693629376818, 0.012714050834049065, 0.016435371150099524, 0.016164058013663874, 0.020882506915774507, 0.020145568998549624, 0.012305800392673968, 0.014956530184668337, 0.015112134499776686, 0.01902932231702561, 0.01234630963111567, 0.012906737823910674, 0.015419763851411342, 0.012028716068544125, 0.012026588670634619, 0.01046666050768814, 0.015074254105983162, 0.017103882743555558, 0.0159288773290811, 0.012313837974495331, 0.015220577762983592, 0.01668405247220018, 0.01821261695683646, 0.015557964546976232, 0.018954335487829717, 0.019052869753069676, 0.013068759590547258, 0.019404580459572697, 0.014780265383972665, 0.014032810398215273, 0.017668089645602916, 0.01691797414374114, 0.019680343301213692, 0.013172024313564238, 0.016219273189979098, 0.013570760188921208, 0.01694245190886061, 0.02107862082863097, 0.015232152812449783, 0.012068081582896514] |
| product_50_results.json/methods/legendre/max_marginal | 0.0392585 | 0.0387271 |
| product_50_results.json/methods/legendre/negative_count_tv | 0.018 | 0.019095 |
| product_50_results.json/methods/legendre/sw | 0.0170652 | 0.0187978 |
| results.json/B_quartic4/sample_size/10000/mean | 0.0542206 | 0.0475355 |
| results.json/B_quartic4/sample_size/10000/median | 0.0509532 | 0.0457758 |
| results.json/B_quartic4/sample_size/10000/n | 5 | 10 |
| results.json/B_quartic4/sample_size/10000/std | 0.0143987 | 0.0127954 |
| results.json/B_quartic4/sample_size/100000/mean | 0.0307358 | 0.029449 |
| results.json/B_quartic4/sample_size/100000/median | 0.0299306 | 0.0296357 |
| results.json/B_quartic4/sample_size/100000/n | 5 | 10 |
| results.json/B_quartic4/sample_size/100000/std | 0.00409217 | 0.0037221 |
| results.json/B_quartic4/sample_size/200000/mean | 0.0280856 | 0.0281003 |
| results.json/B_quartic4/sample_size/200000/median | 0.0279923 | 0.0279132 |
| results.json/B_quartic4/sample_size/200000/n | 5 | 10 |
| results.json/B_quartic4/sample_size/200000/std | 0.00212832 | 0.0024227 |
| results.json/B_poly9/sample_size/10000/mean | 0.101247 | 0.086626 |
| results.json/B_poly9/sample_size/10000/median | 0.115135 | 0.0808079 |
| results.json/B_poly9/sample_size/10000/n | 3 | 10 |
| results.json/B_poly9/sample_size/10000/std | 0.031641 | 0.0240125 |
| results.json/B_poly9/sample_size/100000/mean | 0.0636018 | 0.0561462 |
| results.json/B_poly9/sample_size/100000/median | 0.0621274 | 0.0555335 |
| results.json/B_poly9/sample_size/100000/n | 3 | 10 |
| results.json/B_poly9/sample_size/100000/std | 0.00295803 | 0.00627945 |
| results.json/B_poly9/sample_size/200000/mean | 0.0610299 | 0.0548159 |
| results.json/B_poly9/sample_size/200000/median | 0.0623895 | 0.0568503 |
| results.json/B_poly9/sample_size/200000/n | 3 | 10 |
| results.json/B_poly9/sample_size/200000/std | 0.00261029 | 0.00631786 |
| results.json/A10_beta0.0/sample_size/10000/mean | 0.0711529 | 0.0683851 |
| results.json/A10_beta0.0/sample_size/10000/median | 0.0711529 | 0.067667 |
| results.json/A10_beta0.0/sample_size/10000/n | 2 | 10 |
| results.json/A10_beta0.0/sample_size/10000/std | 0.00114134 | 0.00390213 |
| results.json/A10_beta0.0/sample_size/100000/mean | 0.057499 | 0.0609666 |
| results.json/A10_beta0.0/sample_size/100000/median | 0.057499 | 0.0609229 |
| results.json/A10_beta0.0/sample_size/100000/n | 2 | 10 |
| results.json/A10_beta0.0/sample_size/100000/std | 0.00432855 | 0.00204295 |
| results.json/A10_beta0.0/sample_size/200000/mean | 0.0592283 | 0.0603374 |
| results.json/A10_beta0.0/sample_size/200000/median | 0.0592283 | 0.0611472 |
| results.json/A10_beta0.0/sample_size/200000/n | 2 | 10 |
| results.json/A10_beta0.0/sample_size/200000/std | 0.00251772 | 0.00418302 |
| results.json/A10_beta0.5/sample_size/10000/mean | 0.160034 | 0.14804 |
| results.json/A10_beta0.5/sample_size/10000/median | 0.160034 | 0.153163 |
| results.json/A10_beta0.5/sample_size/10000/n | 2 | 10 |
| results.json/A10_beta0.5/sample_size/10000/std | 0.0136499 | 0.0298243 |
| results.json/A10_beta0.5/sample_size/100000/mean | 0.145449 | 0.161302 |
| results.json/A10_beta0.5/sample_size/100000/median | 0.145449 | 0.16218 |
| results.json/A10_beta0.5/sample_size/100000/n | 2 | 10 |
| results.json/A10_beta0.5/sample_size/100000/std | 0.0253117 | 0.0337389 |
| results.json/A10_beta0.5/sample_size/200000/mean | 0.184562 | 0.189804 |
| results.json/A10_beta0.5/sample_size/200000/median | 0.184562 | 0.185842 |
| results.json/A10_beta0.5/sample_size/200000/n | 2 | 10 |
| results.json/A10_beta0.5/sample_size/200000/std | 0.00706637 | 0.0267543 |
| ou_hd_results.json/time=0.0/adjacent_correlations/mean | [-0.003726937941236489, -0.001506404923954434, -0.013719187113940398, -0.02406924190726167, -0.00708938194049401, 0.00015624761216679293, -0.013318397547850693, 0.004327877333418605, -0.004666809180474541] | [-0.0047956463833775985, 0.0005235956669233703, -0.0012118450410448136, -0.007527188676158469, -0.0004279000909190138, 0.0010985312236687522, 0.001175154384924831, -0.005438637598158971, -0.0002833620101362731] |
| ou_hd_results.json/time=0.0/adjacent_correlations/std | [0.005674968512141342, 0.004468451713776051, 0.009854087143609544, 0.020239034150513566, 0.02912671015121309, 0.009246528219435904, 0.007694398249605183, 0.015538440126675011, 0.013906398374777933] | [0.01248119012949356, 0.009825562987741366, 0.012629806933794745, 0.019246430117950703, 0.018037777376767445, 0.01301643673445365, 0.013896807451757363, 0.02140093065736398, 0.011611398730035347] |
| ou_hd_results.json/time=0.0/covariance_relative_error/mean | 0.701609 | 0.70087 |
| ou_hd_results.json/time=0.0/covariance_relative_error/std | 0.000742539 | 0.00147234 |
| ou_hd_results.json/time=0.0/marginal_w2/mean | [0.6671756072703561, 0.6357932163941548, 0.6388767541092674, 0.6238762841636173, 0.6400438167890706, 0.6340563422529445, 0.6354072602115965, 0.6369696893878282, 0.628391801113971, 0.6636487199166031] | [0.6658985438560159, 0.6376347921676968, 0.632685868537555, 0.630347268528143, 0.6377906254517958, 0.633417059359465, 0.6341793189840804, 0.6358085973492505, 0.6293762265547829, 0.6679726480128994] |
| ou_hd_results.json/time=0.0/marginal_w2/std | [0.002197329895471888, 0.007250986287189226, 0.005357439876493907, 0.0055405436554791165, 0.0027692647255504414, 0.0059113859314830495, 0.0018229974281893887, 0.005694731220355107, 0.012721185475934349, 0.012188775659416262] | [0.006897023269990318, 0.007276347565695196, 0.007604256161256686, 0.006981781157797854, 0.005096458009895772, 0.003352814902476738, 0.008300005534667155, 0.004956876875022599, 0.007154020228104817, 0.00929169510894353] |
| ou_hd_results.json/time=0.0/max_marginal_w2/mean | 0.671417 | 0.671552 |
| ou_hd_results.json/time=0.0/max_marginal_w2/std | 0.00515885 | 0.00646722 |
| ou_hd_results.json/time=0.0/mean_marginal_w2/mean | 0.640424 | 0.640511 |
| ou_hd_results.json/time=0.0/mean_marginal_w2/std | 0.00225905 | 0.0018069 |
| ou_hd_results.json/time=0.0/mean_norm/mean | 1.58203 | 1.58308 |
| ou_hd_results.json/time=0.0/mean_norm/std | 0.00769476 | 0.00595128 |
| ou_hd_results.json/time=0.0/sw2/mean | 0.642629 | 0.642591 |
| ou_hd_results.json/time=0.0/sw2/std | 0.00366706 | 0.00212051 |
| ou_hd_results.json/time=0.5/adjacent_correlations/mean | [0.0700468680109066, 0.07065100780905303, 0.062148578589346824, 0.050835402102032835, 0.06426222352756378, 0.07388723750889843, 0.061267094934841, 0.07613214726362168, 0.07029109643148294] | [0.06712818812415479, 0.07019221622002178, 0.06931085250109251, 0.06302624673802318, 0.06791275233395173, 0.07154784823288267, 0.07138623917677, 0.06373160059020658, 0.0716693952124286] |
| ou_hd_results.json/time=0.5/adjacent_correlations/std | [0.0007227573710745385, 0.006311168795294817, 0.005356692399231534, 0.014730505780294475, 0.018059200353144633, 0.017292670017142842, 0.002764644896479418, 0.013558237995733394, 0.014077664971580124] | [0.009603052818987769, 0.009479447809334476, 0.011781725354631631, 0.014194853400643885, 0.013540002200429762, 0.013770417530812151, 0.010372336663025866, 0.020236259957955482, 0.010999997495985217] |
| ou_hd_results.json/time=0.5/covariance_relative_error/mean | 0.227193 | 0.226532 |
| ou_hd_results.json/time=0.5/covariance_relative_error/std | 0.000660709 | 0.000950404 |
| ou_hd_results.json/time=0.5/marginal_w2/mean | [0.3263864530047411, 0.3199023482096753, 0.3208816587124021, 0.31279426828092566, 0.3223739470461739, 0.31910047351409443, 0.32020561409051235, 0.32020220264497984, 0.3147269672097261, 0.3233194766407914] | [0.3260559538467298, 0.32099185152243526, 0.3173863128542151, 0.31649538138716904, 0.32113717598515323, 0.3184471428677717, 0.3187249822020675, 0.31957534538308613, 0.3157037877416811, 0.32729410797178154] |
| ou_hd_results.json/time=0.5/marginal_w2/std | [0.0019478455818778134, 0.004856449544036936, 0.003344233140159053, 0.0035365959284849586, 0.002118174535544611, 0.004325523769949955, 0.0013965132243536505, 0.004956033135475084, 0.008524215132567273, 0.009545347456936259] | [0.004496459953190429, 0.004985128756124631, 0.004702680013767559, 0.00421308481050172, 0.0030099185867424262, 0.002559295665607786, 0.005599702859250692, 0.00372803233793605, 0.004917060121979429, 0.007080627657286109] |
| ou_hd_results.json/time=0.5/max_marginal_w2/mean | 0.329699 | 0.330447 |
| ou_hd_results.json/time=0.5/max_marginal_w2/std | 0.0038546 | 0.0039582 |
| ou_hd_results.json/time=0.5/mean_marginal_w2/mean | 0.319989 | 0.320181 |
| ou_hd_results.json/time=0.5/mean_marginal_w2/std | 0.00164646 | 0.00118451 |
| ou_hd_results.json/time=0.5/mean_norm/mean | 0.959875 | 0.960551 |
| ou_hd_results.json/time=0.5/mean_norm/std | 0.00506163 | 0.00377983 |
| ou_hd_results.json/time=0.5/sw2/mean | 0.321162 | 0.321294 |
| ou_hd_results.json/time=0.5/sw2/std | 0.00251813 | 0.00144356 |
| ou_hd_results.json/time=1.0/adjacent_correlations/mean | [0.10001588203386984, 0.09868599503310692, 0.09086732962771699, 0.07928348353053566, 0.09220790871574613, 0.10191727394444842, 0.08940110800760293, 0.10411152485443176, 0.10052490657391193] | [0.09706934986815863, 0.09810403598750396, 0.09736116825579418, 0.09095399818330237, 0.09551896434677548, 0.09939981776871971, 0.09917867826856822, 0.09148122220631064, 0.1015807985952081] |
| ou_hd_results.json/time=1.0/adjacent_correlations/std | [0.000833865923866465, 0.006526844250484358, 0.004927697190091618, 0.01438785718828227, 0.017028269748075503, 0.01806670346737022, 0.002254119536824943, 0.013325543884384276, 0.014097394196620705] | [0.009394938331226411, 0.009604126246328878, 0.011933494388669133, 0.013689891427961048, 0.013214088844104079, 0.013832229887335437, 0.010226284835126463, 0.020205042949085834, 0.011028168103952391] |
| ou_hd_results.json/time=1.0/covariance_relative_error/mean | 0.0866284 | 0.0852844 |
| ou_hd_results.json/time=1.0/covariance_relative_error/std | 0.00216303 | 0.00253392 |
| ou_hd_results.json/time=1.0/marginal_w2/mean | [0.18912051660247578, 0.18818207272206924, 0.18830913775877356, 0.1842326882055487, 0.18918789886145324, 0.1877902588330592, 0.1883460505744903, 0.18840657561347887, 0.1853331620145955, 0.18770571015175877] | [0.18893396469682008, 0.18864192634897944, 0.18662897788428412, 0.18621961611630336, 0.1886928520855865, 0.1873952810144799, 0.1875571869770573, 0.1879265418788953, 0.18587872303637726, 0.1896790854687275] |
| ou_hd_results.json/time=1.0/marginal_w2/std | [0.0011398466656633661, 0.002691674837927035, 0.0018882886694466707, 0.001986570442026095, 0.0010731910609079961, 0.002248641889042025, 0.0010432396826249627, 0.0026801783950788755, 0.004954072199617972, 0.005741761276155363] | [0.0026725033974390805, 0.002772237381311474, 0.002677390057278205, 0.002406723323925282, 0.0016223088718355242, 0.0014741189985288923, 0.003018696345092989, 0.0021065690469118355, 0.0028683214567214515, 0.0041007026505555134] |
| ou_hd_results.json/time=1.0/max_marginal_w2/mean | 0.191729 | 0.192135 |
| ou_hd_results.json/time=1.0/max_marginal_w2/std | 0.00223219 | 0.00179208 |
| ou_hd_results.json/time=1.0/mean_marginal_w2/mean | 0.187661 | 0.187755 |
| ou_hd_results.json/time=1.0/mean_marginal_w2/std | 0.00110412 | 0.000786092 |
| ou_hd_results.json/time=1.0/mean_norm/mean | 0.582361 | 0.582791 |
| ou_hd_results.json/time=1.0/mean_norm/std | 0.00327239 | 0.0023872 |
| ou_hd_results.json/time=1.0/sw2/mean | 0.188201 | 0.188308 |
| ou_hd_results.json/time=1.0/sw2/std | 0.00152766 | 0.000884338 |
| ou_hd_results.json/time=2.0/adjacent_correlations/mean | [0.11975599081377797, 0.11596449265863867, 0.10846682525182372, 0.09672359413221789, 0.1094227667466508, 0.11910008759513857, 0.10664673712339805, 0.12137650378271159, 0.12041183482344227] | [0.11686100768415589, 0.11539890970659292, 0.11468901277512092, 0.10818489883819822, 0.11261416718705786, 0.11657985724449452, 0.1163400460339783, 0.10869301291904314, 0.12134060934603771] |
| ou_hd_results.json/time=2.0/adjacent_correlations/std | [0.000968690380283572, 0.006625835690199761, 0.004796582721155769, 0.014302589839002677, 0.016707601576040527, 0.018253379008852228, 0.0020718075459723794, 0.013219600680330729, 0.014033853052448425] | [0.00929999303204977, 0.009649430918357751, 0.011982537336308528, 0.013488531504755102, 0.013118654924902145, 0.01377798753084555, 0.010183986833859836, 0.020186281717738366, 0.010989287327720582] |
| ou_hd_results.json/time=2.0/covariance_relative_error/mean | 0.0458372 | 0.0430288 |
| ou_hd_results.json/time=2.0/covariance_relative_error/std | 0.00521062 | 0.00565139 |
| ou_hd_results.json/time=2.0/marginal_w2/mean | [0.07100437484803895, 0.07123312833745092, 0.07065213465973773, 0.06916457115190405, 0.07099946477743203, 0.07104524429603903, 0.07103065662318586, 0.0718254617702435, 0.07032328400076518, 0.07226294801688636] | [0.07065279308146362, 0.07107732769354594, 0.0703951442649987, 0.07017927711393672, 0.07113899383050577, 0.0708146637990355, 0.07093827977144648, 0.07105407126022396, 0.07027397094735963, 0.07133629004046654] |
| ou_hd_results.json/time=2.0/marginal_w2/std | [0.001088636066715742, 0.0015685185678162969, 0.0010244355582782704, 0.001018739908675088, 0.0007188601607480646, 0.0005828307897521025, 0.0009814305532962447, 0.0009290610077491625, 0.0022359909686305267, 0.0021124158383266215] | [0.0016053801571896977, 0.0013926473822879516, 0.0013676889134306208, 0.0013676728566678392, 0.0010605719978335545, 0.0009460645241229794, 0.0010033911024528044, 0.0009607683098981225, 0.0014696680014255948, 0.0014208920472936852] |
| ou_hd_results.json/time=2.0/max_marginal_w2/mean | 0.0728534 | 0.0726093 |
| ou_hd_results.json/time=2.0/max_marginal_w2/std | 0.00109776 | 0.000786731 |
| ou_hd_results.json/time=2.0/mean_marginal_w2/mean | 0.0709541 | 0.0707861 |
| ou_hd_results.json/time=2.0/mean_marginal_w2/std | 0.000679045 | 0.00054791 |
| ou_hd_results.json/time=2.0/mean_norm/mean | 0.214501 | 0.214687 |
| ou_hd_results.json/time=2.0/mean_norm/std | 0.0015108 | 0.00104108 |
| ou_hd_results.json/time=2.0/sw2/mean | 0.0708563 | 0.0708779 |
| ou_hd_results.json/time=2.0/sw2/std | 0.000473554 | 0.000283222 |
| ou_hd_results.json/time=3.0/adjacent_correlations/mean | [0.12311731839096625, 0.11865629281417515, 0.11118053889335193, 0.09941156561736725, 0.11208219369481391, 0.12174980625752234, 0.10930736539439938, 0.12407129198198086, 0.12379321411669776] | [0.12023338116378672, 0.11810105294088158, 0.11737009591763074, 0.1108480210835944, 0.1152621272955422, 0.11923500352442644, 0.11899433123599001, 0.11138539681665993, 0.12470555909660164] |
| ou_hd_results.json/time=3.0/adjacent_correlations/std | [0.000984803145615771, 0.006641879875280611, 0.004785588072976004, 0.01429822169234422, 0.01667798597729298, 0.018262212558454158, 0.0020503957452019015, 0.013206582939285838, 0.014017353476366304] | [0.009287060790989595, 0.009656055781699, 0.011987566022920393, 0.013463153195310619, 0.013109925319357608, 0.013763957696153092, 0.010179381725642554, 0.02018344515111059, 0.010977630949962115] |
| ou_hd_results.json/time=3.0/covariance_relative_error/mean | 0.0450404 | 0.0421384 |
| ou_hd_results.json/time=3.0/covariance_relative_error/std | 0.00547444 | 0.0058722 |
| ou_hd_results.json/time=3.0/marginal_w2/mean | [0.03240617304574179, 0.03264183307400948, 0.031358929584421734, 0.02969443820067079, 0.031646611266163895, 0.032271636126431434, 0.03176695561718826, 0.03384191952193766, 0.03204040998899565, 0.03607432024911699] | [0.031515662503166585, 0.031955872426636486, 0.03154078002615654, 0.03111933857717089, 0.032121808168227364, 0.03193495894947786, 0.03206801815634919, 0.032274844577397425, 0.03150768739373087, 0.03269814023785156] |
| ou_hd_results.json/time=3.0/marginal_w2/std | [0.0023337113376017166, 0.002996982229259572, 0.0015163450619592458, 0.0014411656017852832, 0.0015974560349223859, 0.0013925994440676178, 0.0015985132386792625, 0.002280872827811528, 0.0031232503406647826, 0.0042037515373324315] | [0.00268140554139538, 0.002497691514582552, 0.0018620515143514995, 0.00203786775070814, 0.0021743136083643144, 0.0020172330714234243, 0.0020755586520555844, 0.001962578454695958, 0.002504918372320582, 0.0031452327742818105] |
| ou_hd_results.json/time=3.0/max_marginal_w2/mean | 0.0365171 | 0.0351419 |
| ou_hd_results.json/time=3.0/max_marginal_w2/std | 0.00372066 | 0.00222729 |
| ou_hd_results.json/time=3.0/mean_marginal_w2/mean | 0.0323743 | 0.0318737 |
| ou_hd_results.json/time=3.0/mean_marginal_w2/std | 0.000990077 | 0.000925833 |
| ou_hd_results.json/time=3.0/mean_norm/mean | 0.0791729 | 0.0792688 |
| ou_hd_results.json/time=3.0/mean_norm/std | 0.000867155 | 0.000577392 |
| ou_hd_results.json/time=3.0/sw2/mean | 0.0318406 | 0.0317877 |
| ou_hd_results.json/time=3.0/sw2/std | 0.000227372 | 0.000195778 |
| ou_hd_results.json/time=4.0/adjacent_correlations/mean | [0.12361337174387993, 0.11903061214071677, 0.11155097789381536, 0.09977807383296938, 0.11244516983169967, 0.12211129844782294, 0.1096707370937003, 0.12444654930102932, 0.12429168919944318] | [0.12073092925346333, 0.11847728726827607, 0.11773656026415898, 0.11121148202970117, 0.11562401309864959, 0.11959739338919644, 0.11935699568291476, 0.11176060379130577, 0.12520176351665313] |
| ou_hd_results.json/time=4.0/adjacent_correlations/std | [0.0009866635543885132, 0.006644377280055555, 0.004784649115349443, 0.014298106720841084, 0.0166748088169206, 0.01826243158533111, 0.0020476399962417726, 0.013205028044776725, 0.014014788246399675] | [0.009285367876141985, 0.009657191360182026, 0.011988358692116258, 0.013459793075618827, 0.013108940688904199, 0.013761926020520862, 0.010178824413453018, 0.020183121506388006, 0.010975670304540502] |
| ou_hd_results.json/time=4.0/covariance_relative_error/mean | 0.0450334 | 0.042127 |
| ou_hd_results.json/time=4.0/covariance_relative_error/std | 0.00549844 | 0.00588713 |
| ou_hd_results.json/time=4.0/marginal_w2/mean | [0.022572403877186193, 0.02279426607982486, 0.02099277073073148, 0.018629609909106875, 0.021308512108441313, 0.022259981718051835, 0.021355497061180465, 0.024414797235159255, 0.022056886860003944, 0.027574495003195948] | [0.021143797964039666, 0.021677902968458083, 0.021310574271059646, 0.02063598944697802, 0.021952157490318376, 0.021758377525889, 0.021849285700551436, 0.022215751527722222, 0.021191994109557664, 0.02273812566615657] |
| ou_hd_results.json/time=4.0/marginal_w2/std | [0.0033229450449837224, 0.0042966181239228515, 0.002232452007731226, 0.002064326236210915, 0.002374170904579092, 0.002019241014931852, 0.0022090247076346787, 0.0032865477366122893, 0.004428521271815497, 0.005661559595925821] | [0.0037610866506137533, 0.003687430329425967, 0.0025902948914795416, 0.0029251561685460885, 0.00315198156543796, 0.0028932007907996795, 0.0032795316082205547, 0.0028553909751860783, 0.003689537729856097, 0.004473204501182271] |
| ou_hd_results.json/time=4.0/max_marginal_w2/mean | 0.0281458 | 0.0262665 |
| ou_hd_results.json/time=4.0/max_marginal_w2/std | 0.00512767 | 0.00303682 |
| ou_hd_results.json/time=4.0/mean_marginal_w2/mean | 0.0223959 | 0.0216474 |
| ou_hd_results.json/time=4.0/mean_marginal_w2/std | 0.00129118 | 0.0012768 |
| ou_hd_results.json/time=4.0/mean_norm/mean | 0.0293901 | 0.0294524 |
| ou_hd_results.json/time=4.0/mean_norm/std | 0.000636828 | 0.000432149 |
| ou_hd_results.json/time=4.0/sw2/mean | 0.0216752 | 0.0215754 |
| ou_hd_results.json/time=4.0/sw2/std | 0.000546077 | 0.00037597 |
| ou_hd_results.json/time=6.0/adjacent_correlations/mean | [0.12369126338972077, 0.11908748798260554, 0.11160566862003418, 0.09983204128422334, 0.11249864500385844, 0.12216454495956804, 0.10972441349337947, 0.12450361269280587, 0.12436989549608053] | [0.12080902704577783, 0.11853448888553239, 0.11779070937974354, 0.11126502022513143, 0.11567737889266028, 0.11965077660131022, 0.11941056239914905, 0.11181768814115026, 0.12527961198571252] |
| ou_hd_results.json/time=6.0/adjacent_correlations/std | [0.0009869137282806876, 0.006644791365829738, 0.00478457630584383, 0.014298121620346733, 0.016674402178928092, 0.018262379119829506, 0.0020472437031392207, 0.013204807800537304, 0.014014397208958642] | [0.009285117708608738, 0.009657399824744917, 0.011988512834699799, 0.013459281853679903, 0.013108802702855093, 0.013761632912954683, 0.010178747837830081, 0.020183080771461442, 0.01097534519021483] |
| ou_hd_results.json/time=6.0/covariance_relative_error/mean | 0.0450339 | 0.042127 |
| ou_hd_results.json/time=6.0/covariance_relative_error/std | 0.00550187 | 0.00588906 |
| ou_hd_results.json/time=6.0/marginal_w2/mean | [0.020644742904911275, 0.02084788827742841, 0.018869694177786837, 0.016206899730558232, 0.01918873670907848, 0.02023388578198981, 0.019157208628268328, 0.02255125190271993, 0.020002672565001437, 0.02596298443280941] | [0.018998843460354003, 0.019552303644484716, 0.019203327670601372, 0.018423568244672606, 0.019867126852994594, 0.019670924230177387, 0.019706389718108307, 0.0201578254375957, 0.019022274580844895, 0.020708750015255246] |
| ou_hd_results.json/time=6.0/marginal_w2/std | [0.0036272926257526587, 0.004724380882533445, 0.002538248482707647, 0.0022874701021529395, 0.0026105453733501495, 0.00216582303983927, 0.0023920669615053233, 0.003561517433721844, 0.004868338556550637, 0.006021552267861582] | [0.004120538893461844, 0.004116901922713301, 0.0028575173333857504, 0.003258172810995726, 0.0034632290103831856, 0.0031564664116048974, 0.0037239376275202164, 0.0031296668566560353, 0.004124558627884023, 0.004865690425966854] |
| ou_hd_results.json/time=6.0/max_marginal_w2/mean | 0.0265583 | 0.0245741 |
| ou_hd_results.json/time=6.0/max_marginal_w2/std | 0.00548474 | 0.00323436 |
| ou_hd_results.json/time=6.0/mean_marginal_w2/mean | 0.0203666 | 0.0195311 |
| ou_hd_results.json/time=6.0/mean_marginal_w2/std | 0.00138097 | 0.00138472 |
| ou_hd_results.json/time=6.0/mean_norm/mean | 0.00435451 | 0.00439676 |
| ou_hd_results.json/time=6.0/mean_norm/std | 0.000529421 | 0.000376845 |
| ou_hd_results.json/time=6.0/sw2/mean | 0.0196097 | 0.019495 |
| ou_hd_results.json/time=6.0/sw2/std | 0.000685321 | 0.000453983 |
| ou_hd_uncoupled_results.json/time=0.0/adjacent_correlations/mean | [-0.003726937941236489, -0.001506404923954434, -0.013719187113940398, -0.02406924190726167, -0.00708938194049401, 0.00015624761216679293, -0.013318397547850693, 0.004327877333418605, -0.004666809180474541] | [-0.0047956463833775985, 0.0005235956669233703, -0.0012118450410448136, -0.007527188676158469, -0.0004279000909190138, 0.0010985312236687522, 0.001175154384924831, -0.005438637598158971, -0.0002833620101362731] |
| ou_hd_uncoupled_results.json/time=0.0/adjacent_correlations/std | [0.005674968512141342, 0.004468451713776051, 0.009854087143609544, 0.020239034150513566, 0.02912671015121309, 0.009246528219435904, 0.007694398249605183, 0.015538440126675011, 0.013906398374777933] | [0.01248119012949356, 0.009825562987741366, 0.012629806933794745, 0.019246430117950703, 0.018037777376767445, 0.01301643673445365, 0.013896807451757363, 0.02140093065736398, 0.011611398730035347] |
| ou_hd_uncoupled_results.json/time=0.0/covariance_relative_error/mean | 0.750007 | 0.749693 |
| ou_hd_uncoupled_results.json/time=0.0/covariance_relative_error/std | 0.000652511 | 0.00142923 |
| ou_hd_uncoupled_results.json/time=0.0/marginal_w2/mean | [0.7083664834471529, 0.7086496028923287, 0.712166667726894, 0.6985005738794284, 0.7131398141998221, 0.7076428840930812, 0.7095050178535219, 0.7104803077967593, 0.7012368344889172, 0.7045819235424537] | [0.7071018771707864, 0.7104427315160274, 0.7061141533991163, 0.7046692913910968, 0.711092060872182, 0.7067676919365473, 0.707688399125961, 0.7090269928545759, 0.7024594362963253, 0.7090601489895507] |
| ou_hd_uncoupled_results.json/time=0.0/marginal_w2/std | [0.0020193940683919066, 0.0073270904483259906, 0.006104649162836168, 0.005591200890277776, 0.003159271885502891, 0.006045797564590791, 0.0018959796148494885, 0.006381540632943715, 0.011232664542010674, 0.012191339129618044] | [0.006564863614812415, 0.0069283043660847005, 0.007560521982177608, 0.006642471562461856, 0.005416573126806427, 0.0034339363525927053, 0.008196573524551028, 0.004982206343763212, 0.006527691686126661, 0.009166190318847292] |
| ou_hd_uncoupled_results.json/time=0.0/max_marginal_w2/mean | 0.718022 | 0.718472 |
| ou_hd_uncoupled_results.json/time=0.0/max_marginal_w2/std | 0.00122139 | 0.00205295 |
| ou_hd_uncoupled_results.json/time=0.0/mean_marginal_w2/mean | 0.707427 | 0.707442 |
| ou_hd_uncoupled_results.json/time=0.0/mean_marginal_w2/std | 0.0021218 | 0.00178372 |
| ou_hd_uncoupled_results.json/time=0.0/mean_norm/mean | 1.58203 | 1.58308 |
| ou_hd_uncoupled_results.json/time=0.0/mean_norm/std | 0.00769476 | 0.00595128 |
| ou_hd_uncoupled_results.json/time=0.0/sw2/mean | 0.708378 | 0.708331 |
| ou_hd_uncoupled_results.json/time=0.0/sw2/std | 0.00344467 | 0.00202554 |
| ou_hd_uncoupled_results.json/time=0.5/adjacent_correlations/mean | [-0.003737186502897158, -0.0017053387247991587, -0.01375118995657936, -0.02414100228709831, -0.006805295083102733, -0.0002583473525219736, -0.013164313744659777, 0.004151971565977367, -0.004735121594308648] | [-0.004900636686237582, 0.0004469656641205482, -0.0012580760125533359, -0.00755994114893409, -0.00027146654916582105, 0.001104232451511864, 0.001152742664285974, -0.00527943469825308, -0.00019210571795366915] |
| ou_hd_uncoupled_results.json/time=0.5/adjacent_correlations/std | [0.00533776137741533, 0.0037901850138262598, 0.009934333677898788, 0.02016609161428807, 0.029111661567631248, 0.009405757070498823, 0.007760203635817165, 0.01568694487222617, 0.013868636921591933] | [0.01257498259172463, 0.009819769109366541, 0.01268265574730896, 0.01920629232374491, 0.01801108501659022, 0.013292916181092839, 0.01388385192965038, 0.021163381951345626, 0.011803769574724312] |
| ou_hd_uncoupled_results.json/time=0.5/covariance_relative_error/mean | 0.278695 | 0.278289 |
| ou_hd_uncoupled_results.json/time=0.5/covariance_relative_error/std | 0.000484352 | 0.000634872 |
| ou_hd_uncoupled_results.json/time=0.5/marginal_w2/mean | [0.3392617183483185, 0.33993044608821216, 0.34114005571843836, 0.3319417370869084, 0.342592621838089, 0.338777372459983, 0.3379241126514072, 0.34039121591295807, 0.33630828806409685, 0.33926088638163093] | [0.33865473021290915, 0.3406515850131276, 0.3382322338413545, 0.3353355718322458, 0.3408554956459749, 0.3386930895293484, 0.3385917804054464, 0.3403773302447729, 0.3364107799994759, 0.3403934482631218] |
| ou_hd_uncoupled_results.json/time=0.5/marginal_w2/std | [0.0022872530522468066, 0.003510945237213011, 0.0011526000341393798, 0.0021683711073014742, 0.0003266703457556372, 0.0029357412025063485, 0.0013149916579599933, 0.001073192288452361, 0.009548573493782596, 0.005945409451458842] | [0.004868980100584516, 0.004402046943379283, 0.003776382425997257, 0.004073309995045177, 0.002448975288724097, 0.0020743041607428313, 0.004232189306076378, 0.0025929828572368308, 0.005260821105714495, 0.00499642529866181] |
| ou_hd_uncoupled_results.json/time=0.5/max_marginal_w2/mean | 0.344276 | 0.345326 |
| ou_hd_uncoupled_results.json/time=0.5/max_marginal_w2/std | 0.00265467 | 0.00263107 |
| ou_hd_uncoupled_results.json/time=0.5/mean_marginal_w2/mean | 0.338753 | 0.33882 |
| ou_hd_uncoupled_results.json/time=0.5/mean_marginal_w2/std | 0.00149593 | 0.00107721 |
| ou_hd_uncoupled_results.json/time=0.5/mean_norm/mean | 0.959919 | 0.960426 |
| ou_hd_uncoupled_results.json/time=0.5/mean_norm/std | 0.00489367 | 0.0036791 |
| ou_hd_uncoupled_results.json/time=0.5/sw2/mean | 0.33994 | 0.339831 |
| ou_hd_uncoupled_results.json/time=0.5/sw2/std | 0.002623 | 0.00140097 |
| ou_hd_uncoupled_results.json/time=1.0/adjacent_correlations/mean | [-0.003739964631224699, -0.0017072721268075644, -0.013750135630823807, -0.02413915260040257, -0.006804389000904896, -0.00025971646635445457, -0.013164102694157206, 0.004148678393882422, -0.004732949741103901] | [-0.004903905609557278, 0.0004458818847386225, -0.00125960024501139, -0.007561332842050056, -0.00027226782477059706, 0.0011061027918170354, 0.0011515174211265643, -0.005277768555642523, -0.00019016509049063517] |
| ou_hd_uncoupled_results.json/time=1.0/adjacent_correlations/std | [0.005337413081496331, 0.0037902101982128576, 0.00993499297005614, 0.020166365336248483, 0.029110900426398415, 0.009409004864991707, 0.007759488461611704, 0.01568524797342992, 0.013865396018654226] | [0.012576031669147121, 0.00982067124792862, 0.012682144941800092, 0.019203760727694665, 0.01801139342849486, 0.013297933815153101, 0.013883728772224603, 0.021159645206512017, 0.011805014739350883] |
| ou_hd_uncoupled_results.json/time=1.0/covariance_relative_error/mean | 0.110231 | 0.109376 |
| ou_hd_uncoupled_results.json/time=1.0/covariance_relative_error/std | 0.0018158 | 0.00162499 |
| ou_hd_uncoupled_results.json/time=1.0/marginal_w2/mean | [0.19245835454403767, 0.1931769237392178, 0.19357168944087003, 0.18778399495022233, 0.19466431494510691, 0.19230572158874182, 0.19129059454616185, 0.19327870946379855, 0.19082825214616173, 0.19285223480294125] | [0.1920699761227032, 0.19342372355432588, 0.19189599064673274, 0.18983736656766187, 0.19346127663267598, 0.19216555951073203, 0.1919691245235921, 0.19333033631574287, 0.1908244018293201, 0.19335784906160716] |
| ou_hd_uncoupled_results.json/time=1.0/marginal_w2/std | [0.001593611529818578, 0.001984424935251395, 0.0006740248576572623, 0.0010838122379741224, 0.00017533958839797953, 0.001878042481739715, 0.0009713351741861016, 0.00019232542582882617, 0.00629996711752445, 0.0036005711549014965] | [0.0031599894122259866, 0.002860545163301195, 0.0023641469847847036, 0.0026492964893866625, 0.0016388891459063976, 0.0014287911796959656, 0.0025629531111801547, 0.001596378070389665, 0.003530369077735863, 0.003080838499704329] |
| ou_hd_uncoupled_results.json/time=1.0/max_marginal_w2/mean | 0.195752 | 0.19643 |
| ou_hd_uncoupled_results.json/time=1.0/max_marginal_w2/std | 0.00203419 | 0.00181711 |
| ou_hd_uncoupled_results.json/time=1.0/mean_marginal_w2/mean | 0.192221 | 0.192234 |
| ou_hd_uncoupled_results.json/time=1.0/mean_marginal_w2/std | 0.00100752 | 0.000698852 |
| ou_hd_uncoupled_results.json/time=1.0/mean_norm/mean | 0.582406 | 0.582649 |
| ou_hd_uncoupled_results.json/time=1.0/mean_norm/std | 0.00308422 | 0.0022702 |
| ou_hd_uncoupled_results.json/time=1.0/sw2/mean | 0.193375 | 0.193272 |
| ou_hd_uncoupled_results.json/time=1.0/sw2/std | 0.00171287 | 0.000906943 |
| ou_hd_uncoupled_results.json/time=2.0/adjacent_correlations/mean | [-0.0037404254312989765, -0.0017075139573961718, -0.013749954756129392, -0.024138969784642306, -0.0068042591105024015, -0.000259883028000485, -0.013164158276750451, 0.004148135749998464, -0.004732486493719595] | [-0.004904429715712736, 0.00044576098812569283, -0.001259879212320561, -0.007561618635549891, -0.00027246864927289347, 0.0011064436728354522, 0.0011513391177425847, -0.005277472867345952, -0.00018984918313505662] |
| ou_hd_uncoupled_results.json/time=2.0/adjacent_correlations/std | [0.005337631419190598, 0.00379039313667021, 0.00993516090598817, 0.020166492885965254, 0.029110551763800997, 0.009409567932954414, 0.00775923084706107, 0.015684819905244608, 0.013864852986949946] | [0.012576227401583881, 0.009820770642198306, 0.012682057452638888, 0.019203286786918173, 0.018011394892708452, 0.013298793872460028, 0.013883688314668964, 0.021159095224230602, 0.011805119082053022] |
| ou_hd_uncoupled_results.json/time=2.0/covariance_relative_error/mean | 0.0465287 | 0.0444708 |
| ou_hd_uncoupled_results.json/time=2.0/covariance_relative_error/std | 0.00486024 | 0.00463547 |
| ou_hd_uncoupled_results.json/time=2.0/marginal_w2/mean | [0.06996448610680206, 0.07119282050602617, 0.0704589039112458, 0.0683545087556546, 0.07100420025967417, 0.07046750526270244, 0.06919631111486323, 0.07074022087049006, 0.06949486027952693, 0.07058377519207215] | [0.06974976279998041, 0.07067297333906826, 0.0699659471073639, 0.06910927993870146, 0.07039084916430473, 0.06992587264702828, 0.06962474220030038, 0.07062633393310716, 0.06954995678805496, 0.07075879709918578] |
| ou_hd_uncoupled_results.json/time=2.0/marginal_w2/std | [0.0005807585279475272, 0.000825029940141147, 0.0005857682320533779, 0.0002224428738529184, 0.0007601022840714856, 0.0012753736068372547, 0.0005144021508196844, 0.0006210692036185474, 0.002349035669184993, 0.0016095768756987166] | [0.0012055722337996548, 0.0014751673217416304, 0.001168381526676655, 0.0014136748585956765, 0.0009054723024472765, 0.0009217146038636904, 0.0008963952911023866, 0.0007370889790113302, 0.0014844157399429424, 0.0011950956043273045] |
| ou_hd_uncoupled_results.json/time=2.0/max_marginal_w2/mean | 0.0718975 | 0.072036 |
| ou_hd_uncoupled_results.json/time=2.0/max_marginal_w2/std | 0.000693807 | 0.000796674 |
| ou_hd_uncoupled_results.json/time=2.0/mean_marginal_w2/mean | 0.0701458 | 0.0700375 |
| ou_hd_uncoupled_results.json/time=2.0/mean_marginal_w2/std | 0.000505782 | 0.000305708 |
| ou_hd_uncoupled_results.json/time=2.0/mean_norm/mean | 0.214533 | 0.214526 |
| ou_hd_uncoupled_results.json/time=2.0/mean_norm/std | 0.00130875 | 0.000902497 |
| ou_hd_uncoupled_results.json/time=2.0/sw2/mean | 0.0719225 | 0.0718072 |
| ou_hd_uncoupled_results.json/time=2.0/sw2/std | 0.000634949 | 0.000334016 |
| ou_hd_uncoupled_results.json/time=3.0/adjacent_correlations/mean | [-0.0037404438097425174, -0.0017075215481441202, -0.013749948148117641, -0.024138966497451796, -0.006804254469015739, -0.00025988876054807916, -0.013164162807667567, 0.004148114746782607, -0.004732466097757136] | [-0.004904450409485688, 0.0004457585134595236, -0.0012598909773872883, -0.007561631751141748, -0.0002724781646734634, 0.0011064579085171312, 0.0011513320601009708, -0.00527746004684655, -0.00018983616045418418] |
| ou_hd_uncoupled_results.json/time=3.0/adjacent_correlations/std | [0.00533764755879205, 0.003790404716448586, 0.00993516964235438, 0.020166499072715324, 0.029110530677916108, 0.00940959140526899, 0.007759216526536481, 0.01568479877975436, 0.013864832407603982] | [0.01257623603042404, 0.009820773238652285, 0.012682054394687614, 0.019203266020687514, 0.01801139319022386, 0.01329883014704207, 0.013883685869100238, 0.02115907572024459, 0.011805122432722144] |
| ou_hd_uncoupled_results.json/time=3.0/covariance_relative_error/mean | 0.0446815 | 0.0425216 |
| ou_hd_uncoupled_results.json/time=3.0/covariance_relative_error/std | 0.00512388 | 0.00493579 |
| ou_hd_uncoupled_results.json/time=3.0/marginal_w2/mean | [0.029251382995895286, 0.03173812314279085, 0.02978064473067245, 0.02882441870625291, 0.029941732023547784, 0.030550435387089358, 0.028320691455063274, 0.030470034321111866, 0.02919913921796448, 0.03034992981955138] | [0.029021288196405072, 0.030273094332937477, 0.0297260103776474, 0.029242597601290832, 0.02948803386211856, 0.029337541669415462, 0.028760542531938882, 0.0301067266407139, 0.029392992262834493, 0.030537252897936323] |
| ou_hd_uncoupled_results.json/time=3.0/marginal_w2/std | [0.00020682503647408325, 0.0028983976219514075, 0.0010050755329221043, 0.0011328706689372155, 0.0016717157863269463, 0.002518815181250911, 0.000480396866551875, 0.0013745192503260728, 0.000719117553189142, 0.0012837430110251681] | [0.0007854479250216898, 0.0023327947280208142, 0.001482832112833643, 0.0017305120735905647, 0.0012165708272152181, 0.0016931459079370106, 0.0006799237726122977, 0.0015256053833528952, 0.0011118707711550927, 0.0009109056113316191] |
| ou_hd_uncoupled_results.json/time=3.0/max_marginal_w2/mean | 0.0332025 | 0.0323931 |
| ou_hd_uncoupled_results.json/time=3.0/max_marginal_w2/std | 0.00171255 | 0.00132305 |
| ou_hd_uncoupled_results.json/time=3.0/mean_marginal_w2/mean | 0.0298427 | 0.0295886 |
| ou_hd_uncoupled_results.json/time=3.0/mean_marginal_w2/std | 0.000399079 | 0.000281939 |
| ou_hd_uncoupled_results.json/time=3.0/mean_norm/mean | 0.0791968 | 0.0790984 |
| ou_hd_uncoupled_results.json/time=3.0/mean_norm/std | 0.000655101 | 0.000419117 |
| ou_hd_uncoupled_results.json/time=3.0/sw2/mean | 0.0334419 | 0.0332693 |
| ou_hd_uncoupled_results.json/time=3.0/sw2/std | 0.000319473 | 0.000241324 |
| ou_hd_uncoupled_results.json/time=4.0/adjacent_correlations/mean | [-0.0037404446846402654, -0.0017075218753758326, -0.013749947851873218, -0.024138966413353034, -0.006804254258528575, -0.00025988902407986643, -0.013164163057375755, 0.004148113763882099, -0.004732465103520738] | [-0.004904451394035105, 0.00044575844117579835, -0.001259891545620287, -0.007561632404995812, -0.00027247863903461666, 0.0011064585961890906, 0.0011513317196054228, -0.0052774594161070715, -0.00018983552810691027] |
| ou_hd_uncoupled_results.json/time=4.0/adjacent_correlations/std | [0.00533764844686217, 0.0037904053362949925, 0.009935170095169045, 0.020166499371774057, 0.029110529545226332, 0.009409592541454192, 0.007759215779665447, 0.015684797705967014, 0.013864831458597347] | [0.012576236455979141, 0.009820773341870245, 0.012682054262375304, 0.019203264999280958, 0.01801139307648437, 0.013298831918192455, 0.013883685737382502, 0.021159074836831476, 0.011805122600915449] |
| ou_hd_uncoupled_results.json/time=4.0/covariance_relative_error/mean | 0.0446706 | 0.0425089 |
| ou_hd_uncoupled_results.json/time=4.0/covariance_relative_error/std | 0.00513439 | 0.00495014 |
| ou_hd_uncoupled_results.json/time=4.0/marginal_w2/mean | [0.01769799799439321, 0.0212989979045545, 0.018487893544984414, 0.017591098596156637, 0.018271579333396324, 0.01960840185851292, 0.016368891232013152, 0.019409789170755466, 0.01775583477750931, 0.019302389329967973] | [0.017375403669333316, 0.01906731965832798, 0.01851843786173747, 0.018044787776333466, 0.0178551549145266, 0.017780852982496376, 0.01693047802944055, 0.018780012838578698, 0.018076475802649893, 0.019593132717910487] |
| ou_hd_uncoupled_results.json/time=4.0/marginal_w2/std | [0.00033872780832592566, 0.004581276306376424, 0.0015617867219257498, 0.001964644777023227, 0.002624672016278397, 0.003748581972897296, 0.0006350461747259718, 0.001974518846683736, 0.000282130823730355, 0.0015031261826738034] | [0.0011411732241595532, 0.003505008154463843, 0.0022339658675161415, 0.002435780979290176, 0.0017915485664856971, 0.002592997213907993, 0.0011194068508827042, 0.0024679138660508317, 0.0014974280558451385, 0.0013132039228972905] |
| ou_hd_uncoupled_results.json/time=4.0/max_marginal_w2/mean | 0.0236689 | 0.022384 |
| ou_hd_uncoupled_results.json/time=4.0/max_marginal_w2/std | 0.00244674 | 0.0018726 |
| ou_hd_uncoupled_results.json/time=4.0/mean_marginal_w2/mean | 0.0185793 | 0.0182022 |
| ou_hd_uncoupled_results.json/time=4.0/mean_marginal_w2/std | 0.000413541 | 0.000392502 |
| ou_hd_uncoupled_results.json/time=4.0/mean_norm/mean | 0.0294115 | 0.0292796 |
| ou_hd_uncoupled_results.json/time=4.0/mean_norm/std | 0.000417139 | 0.000266065 |
| ou_hd_uncoupled_results.json/time=4.0/sw2/mean | 0.0239235 | 0.0237106 |
| ou_hd_uncoupled_results.json/time=4.0/sw2/std | 0.000435463 | 0.000337187 |
| ou_hd_uncoupled_results.json/time=6.0/adjacent_correlations/mean | [-0.003740444729815594, -0.0017075218916085537, -0.013749947836987837, -0.024138966410446105, -0.006804254247878669, -0.0002598890375422485, -0.013164163070886338, 0.004148113713502012, -0.004732465051789735] | [-0.004904451444880495, 0.00044575843836435863, -0.0012598915750980423, -0.007561632439330848, -0.0002724786639171215, 0.0011064586318891227, 0.0011513317019035255, -0.0052774593831262226, -0.00018983549517941815] |
| ou_hd_uncoupled_results.json/time=6.0/adjacent_correlations/std | [0.005337648494996281, 0.0037904053696188643, 0.009935170119278918, 0.020166499387202802, 0.029110529484189344, 0.009409592600492197, 0.007759215739872775, 0.0156847976492037, 0.013864831410275332] | [0.012576236478240863, 0.009820773346831282, 0.01268205425584349, 0.019203264945897774, 0.018011393069958914, 0.013298832010576826, 0.013883685730280386, 0.02115907479211551, 0.01180512260992813] |
| ou_hd_uncoupled_results.json/time=6.0/covariance_relative_error/mean | 0.0446741 | 0.0425125 |
| ou_hd_uncoupled_results.json/time=6.0/covariance_relative_error/std | 0.00513543 | 0.00495174 |
| ou_hd_uncoupled_results.json/time=6.0/marginal_w2/mean | [0.015143217251403123, 0.019112952156570048, 0.016091770465456293, 0.015029216516865632, 0.015618812688785844, 0.017227284725587252, 0.013634070364000163, 0.017015874393371294, 0.015177614990944157, 0.016914839193458587] | [0.014775043369584804, 0.01662360705414532, 0.016077472704755267, 0.015569929860467268, 0.015255539051746408, 0.015185479508035426, 0.014238984117221373, 0.016263969900800538, 0.015549916993324874, 0.017271771796614106] |
| ou_hd_uncoupled_results.json/time=6.0/marginal_w2/std | [0.0004416715054024295, 0.005148600797496291, 0.0018086466712409247, 0.0022748787473191308, 0.0030065558156279013, 0.004156322134552713, 0.0007190512234240713, 0.002101453924746771, 0.00036831828327350585, 0.0016247318641098467] | [0.0013387020133670503, 0.003945365597367537, 0.0025619309968214527, 0.0027233883264234033, 0.002021233093267054, 0.0029382859242892572, 0.0013200674873326552, 0.002831869280207935, 0.0016882982963416105, 0.0015178681771823759] |
| ou_hd_uncoupled_results.json/time=6.0/max_marginal_w2/mean | 0.0217765 | 0.0203898 |
| ou_hd_uncoupled_results.json/time=6.0/max_marginal_w2/std | 0.00268389 | 0.0020489 |
| ou_hd_uncoupled_results.json/time=6.0/mean_marginal_w2/mean | 0.0160966 | 0.0156812 |
| ou_hd_uncoupled_results.json/time=6.0/mean_marginal_w2/std | 0.000407916 | 0.000439834 |
| ou_hd_uncoupled_results.json/time=6.0/mean_norm/mean | 0.0043864 | 0.00423532 |
| ou_hd_uncoupled_results.json/time=6.0/mean_norm/std | 0.000304823 | 0.000212159 |
| ou_hd_uncoupled_results.json/time=6.0/sw2/mean | 0.0220691 | 0.0218517 |
| ou_hd_uncoupled_results.json/time=6.0/sw2/std | 0.000494118 | 0.000369173 |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 128, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0287612 | 0.0283141 |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00245796 | 0.00227641 |
| admissible_source/{'beta': 0.25, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 8, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 0.25, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0285354 | 0.0296133 |
| admissible_source/{'beta': 0.25, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00116532 | 0.00254525 |
| admissible_source/{'beta': 0.25, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0543494 | 0.0486371 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.0162333 | 0.013781 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0323128 | 0.0309156 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.0013626 | 0.00366935 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.038288 | 0.0363814 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00270659 | 0.004312 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0293763 | 0.0294545 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.0020215 | 0.00271547 |
| admissible_source/{'beta': 0.25, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 128, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.025}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.025}/sw2_mean | 0.0302126 | 0.0290907 |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.025}/sw2_std | 0.00240188 | 0.00211375 |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0293986 | 0.0282007 |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00254319 | 0.00239512 |
| admissible_source/{'beta': 0.5, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 8, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/sw2_mean | 0.0301057 | 0.029816 |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/sw2_std | 0.00411044 | 0.0037942 |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0293046 | 0.0288063 |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00299427 | 0.00281767 |
| admissible_source/{'beta': 0.5, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/sw2_mean | 0.0528942 | 0.0492038 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/sw2_std | 0.012366 | 0.0119019 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0516388 | 0.0475984 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.0108268 | 0.0110648 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0320745 | 0.0308453 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.0040007 | 0.00390064 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0353347 | 0.0373033 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00772431 | 0.00768544 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/sw2_mean | 0.0318794 | 0.0309135 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.025}/sw2_std | 0.00388577 | 0.00409311 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0318097 | 0.0305498 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00389555 | 0.00425869 |
| admissible_source/{'beta': 0.5, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 128, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.028116 | 0.0266623 |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00264045 | 0.00244187 |
| admissible_source/{'beta': 0.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 8, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.027971 | 0.027761 |
| admissible_source/{'beta': 0.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00269138 | 0.00255831 |
| admissible_source/{'beta': 0.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0525467 | 0.0486142 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00964085 | 0.0142113 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0296132 | 0.0285014 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00190409 | 0.00250153 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0339809 | 0.0345281 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00398616 | 0.00413231 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 5 | 10 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0287649 | 0.0275993 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00317408 | 0.00274004 |
| admissible_source/{'beta': 0.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 128, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0276435 | 0.027169 |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00171799 | 0.00180362 |
| admissible_source/{'beta': 1.0, 'method': 'FD', 'regime': 'S', 'n_pairs': 0, 'r_requested': 8, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 1.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0270154 | 0.0278782 |
| admissible_source/{'beta': 1.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00165309 | 0.00261559 |
| admissible_source/{'beta': 1.0, 'method': 'Legendre', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0433447 | 0.0426916 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'I', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00993445 | 0.00816502 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0280908 | 0.0283753 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 100000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00150476 | 0.00218023 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0419367 | 0.0532305 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 10000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00832298 | 0.0200877 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 16, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 32, 'dt': 0.05}/sw2_std | 0 | unavailable |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/n | 3 | 10 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_mean | 0.0271658 | 0.027251 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 64, 'dt': 0.05}/sw2_std | 0.00176904 | 0.00274179 |
| admissible_source/{'beta': 1.0, 'method': 'RBF', 'regime': 'S', 'n_pairs': 200000, 'r_requested': 96, 'dt': 0.05}/sw2_std | 0 | unavailable |
| data_comparison/{'beta': 0.0, 'method': 'A'}/fit_seconds_mean | 3.36686 | 3.12883 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/fit_seconds_std | 0.143985 | 0.523919 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/hit_count | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/hit_seconds_mean | 5.87333 | 5.66074 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/hit_seconds_std | 0.237785 | 0.538099 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/n_repeats | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/sample_seconds_mean | 6.28734 | 6.32795 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/sample_seconds_std | 0.350822 | 0.128322 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/successful_runs | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/sw2_mean | 0.0287649 | 0.0275993 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/sw2_std | 0.00317408 | 0.00274004 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/total_seconds_mean | 9.6542 | 9.45677 |
| data_comparison/{'beta': 0.0, 'method': 'A'}/total_seconds_std | 0.472036 | 0.521346 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/fit_seconds_mean | 1.32248 | 1.32181 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/fit_seconds_std | 0.0709409 | 0.0623496 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/n_repeats | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/sample_seconds_mean | 47.547 | 46.4364 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/sample_seconds_std | 4.42563 | 1.33247 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/successful_runs | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/sw2_mean | 0.20358 | 0.241766 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/sw2_std | 0.0313032 | 0.100975 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/total_seconds_mean | 48.8694 | 47.7582 |
| data_comparison/{'beta': 0.0, 'method': 'B'}/total_seconds_std | 4.48355 | 1.36339 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/fit_seconds_mean | 1.32248 | 1.32181 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/fit_seconds_std | 0.0709409 | 0.0623496 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/hit_count | 5 | 9 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/hit_seconds_mean | 20.9757 | 20.7082 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/hit_seconds_std | 2.65924 | 2.39684 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/n_repeats | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/sample_seconds_mean | 50.4521 | 52.2958 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/sample_seconds_std | 1.49135 | 1.53228 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/successful_runs | 5 | 10 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/sw2_mean | 0.0354293 | 0.039419 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/sw2_std | 0.00439137 | 0.0129579 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/total_seconds_mean | 51.7745 | 53.6176 |
| data_comparison/{'beta': 0.0, 'method': 'D'}/total_seconds_std | 1.49306 | 1.54576 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/fit_seconds_mean | 3.28595 | 3.24359 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/fit_seconds_std | 0.224023 | 0.0999868 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/hit_count | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/hit_seconds_mean | 5.344 | 5.34458 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/hit_seconds_std | 0.628916 | 0.244858 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/n_repeats | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/sample_seconds_mean | 5.37645 | 5.41934 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/sample_seconds_std | 0.55385 | 0.0871097 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/successful_runs | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/sw2_mean | 0.0318097 | 0.0305498 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/sw2_std | 0.00389555 | 0.00425869 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/total_seconds_mean | 8.6624 | 8.66293 |
| data_comparison/{'beta': 0.5, 'method': 'A'}/total_seconds_std | 0.776769 | 0.162647 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/fit_seconds_mean | 1.27397 | 1.2957 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/fit_seconds_std | 0.397098 | 0.073622 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/n_repeats | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/sample_seconds_mean | 37.0035 | 39.1573 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/sample_seconds_std | 2.39893 | 0.555399 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/successful_runs | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/sw2_mean | 0.239119 | 0.248024 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/sw2_std | 0.0547573 | 0.0661021 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/total_seconds_mean | 38.2775 | 40.453 |
| data_comparison/{'beta': 0.5, 'method': 'B'}/total_seconds_std | 2.68772 | 0.579825 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/fit_seconds_mean | 1.27397 | 1.2957 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/fit_seconds_std | 0.397098 | 0.073622 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/hit_count | 4 | 8 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/hit_seconds_mean | 16.6121 | 16.7509 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/hit_seconds_std | 1.36635 | 1.45485 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/n_repeats | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/sample_seconds_mean | 43.2735 | 44.5982 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/sample_seconds_std | 1.61044 | 0.592039 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/successful_runs | 5 | 10 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/sw2_mean | 0.0446113 | 0.0476963 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/sw2_std | 0.0317633 | 0.0267278 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/total_seconds_mean | 44.5475 | 45.8938 |
| data_comparison/{'beta': 0.5, 'method': 'D'}/total_seconds_std | 1.49615 | 0.632825 |
| a10_sweep/('poly', 3, 16)/energy | 0.031259 | 0.0278192 |
| a10_sweep/('poly', 3, 16)/marginal_w2 | [0.31672202582769143, 0.26822922884713823, 0.266297418463106, 0.2062386761319199, 0.22151903915372256, 0.22912107090977255, 0.24447204820397408, 0.18694235946887505, 0.1837221676022412, 0.18329690805640722] | [0.30676168150485855, 0.28191167132000766, 0.24506982818469433, 0.2106991942365298, 0.24840858586490444, 0.23614130970879213, 0.22086273443969792, 0.252568623937526, 0.1873462016358821, 0.2094530735663086] |
| a10_sweep/('poly', 3, 16)/mass | 0.492 | 0.542 |
| a10_sweep/('poly', 3, 16)/max_marginal | 0.316722 | 0.306762 |
| a10_sweep/('poly', 3, 16)/sw | 0.213559 | 0.209898 |
| a10_sweep/('poly', 4, 16)/energy | 0.0330312 | 0.0305502 |
| a10_sweep/('poly', 4, 16)/marginal_w2 | [0.36334380645456094, 0.23631487312635108, 0.21327381946412557, 0.17242062947860126, 0.21438199292815063, 0.18679642663749693, 0.20009016608235636, 0.1956294403366359, 0.13974113501226987, 0.17543512346457227] | [0.3566838620493784, 0.21365625652428394, 0.18474675400814097, 0.18143564555808658, 0.19963658821702246, 0.19517717587727898, 0.1952763978005245, 0.1882440847594922, 0.1411489231670579, 0.16969850735335631] |
| a10_sweep/('poly', 4, 16)/mass | 0.474 | 0.484 |
| a10_sweep/('poly', 4, 16)/max_marginal | 0.363344 | 0.356684 |
| a10_sweep/('poly', 4, 16)/sw | 0.198971 | 0.191349 |
| a10_sweep/('poly', 3, 32)/energy | 0.0313293 | 0.0215092 |
| a10_sweep/('poly', 3, 32)/marginal_w2 | [0.3036831073565504, 0.33903053650935133, 0.32599084346461843, 0.2625995052493206, 0.2620641414000035, 0.22447830954347278, 0.2662483569376511, 0.24323297709240477, 0.22543564662888282, 0.28565751326457023] | [0.3067150642721449, 0.250915419046079, 0.2360256251944917, 0.19062249155913336, 0.23907948062384515, 0.24000287106600368, 0.215455328474003, 0.24256800300888606, 0.19127433216667755, 0.20527389157750692] |
| a10_sweep/('poly', 3, 32)/mass | 0.568 | 0.558 |
| a10_sweep/('poly', 3, 32)/max_marginal | 0.339031 | 0.306715 |
| a10_sweep/('poly', 3, 32)/sw | 0.25695 | 0.212636 |
| a10_sweep/('poly', 4, 32)/energy | 0.0279405 | 0.0245225 |
| a10_sweep/('poly', 4, 32)/marginal_w2 | [0.34915227931863163, 0.2851536135938704, 0.2500339924901852, 0.2299120811577502, 0.207216191267083, 0.25871487612477995, 0.25988308810978833, 0.1992005822646845, 0.191534104313061, 0.2118141496801606] | [0.33846977547597895, 0.23648238795840243, 0.2344783070652815, 0.22151525474897774, 0.23843811835992107, 0.23790365011913264, 0.23637487768200932, 0.22571061318938443, 0.15527733408984315, 0.20125459723985958] |
| a10_sweep/('poly', 4, 32)/max_marginal | 0.349152 | 0.33847 |
| a10_sweep/('poly', 4, 32)/sw | 0.243121 | 0.219833 |
| a10_sweep/('poly', 3, 64)/energy | 0.024474 | 0.0267739 |
| a10_sweep/('poly', 3, 64)/marginal_w2 | [0.3090820001461629, 0.26899708628574875, 0.30730679845081393, 0.22438840104787763, 0.30250526756293045, 0.277900996040043, 0.280816570945673, 0.30225437659679016, 0.2532769218280106, 0.29736855201421203] | [0.2981978451775188, 0.36149773851617084, 0.31598321126696294, 0.29380700485536904, 0.30300861191122885, 0.31322969258946287, 0.3454144070025979, 0.2867503200320576, 0.2393909049173485, 0.332777093988621] |
| a10_sweep/('poly', 3, 64)/mass | 0.57 | 0.58 |
| a10_sweep/('poly', 3, 64)/max_marginal | 0.309082 | 0.361498 |
| a10_sweep/('poly', 3, 64)/sw | 0.262981 | 0.325046 |
| a10_sweep/('poly', 4, 64)/energy | 0.0224114 | 0.0169784 |
| a10_sweep/('poly', 4, 64)/marginal_w2 | [0.34960929124821655, 0.22293816114674483, 0.26154853728928595, 0.2373786502492455, 0.1745195948420981, 0.23501278372879805, 0.24807437389248713, 0.2516758755818501, 0.19814942551984505, 0.22899898742447786] | [0.32714006404774876, 0.204613316216997, 0.19728126764674825, 0.19275835819690226, 0.19304263937048402, 0.19457151673542714, 0.21810447350127674, 0.17033025459614198, 0.17392497400784254, 0.15910501966033203] |
| a10_sweep/('poly', 4, 64)/mass | 0.559 | 0.554 |
| a10_sweep/('poly', 4, 64)/max_marginal | 0.349609 | 0.32714 |
| a10_sweep/('poly', 4, 64)/sw | 0.243112 | 0.208359 |
| a10_sweep/('rbf', 10, 16)/energy | 0.021676 | 0.0222703 |
| a10_sweep/('rbf', 10, 16)/marginal_w2 | [0.2016746780084409, 0.2044722531388229, 0.2010617902433522, 0.14989660118797407, 0.1342454575920537, 0.13037348714937064, 0.10836487244795483, 0.1406192628416566, 0.08269460250630459, 0.11907463986681842] | [0.20366922139854196, 0.2132648125050885, 0.20501118928577763, 0.15156482058994056, 0.1387748672632912, 0.14238379166146042, 0.1167804148784665, 0.14337479959480995, 0.06528773743699963, 0.10228035186482849] |
| a10_sweep/('rbf', 10, 16)/mass | 0.473 | 0.474 |
| a10_sweep/('rbf', 10, 16)/max_marginal | 0.204472 | 0.213265 |
| a10_sweep/('rbf', 10, 16)/sw | 0.140339 | 0.145123 |
| a10_sweep/('rbf', 8, 16)/energy | 0.0190739 | 0.0177475 |
| a10_sweep/('rbf', 8, 16)/marginal_w2 | [0.2532569446616911, 0.20281713154879005, 0.14460418062818517, 0.1618240192699755, 0.12421359218765116, 0.12457162094546417, 0.11122240828870479, 0.15862313377774895, 0.05774755273744899, 0.07915388813880965] | [0.26016761624854196, 0.15996753853391593, 0.1254822306507258, 0.16657680675801198, 0.12572616045655033, 0.13259592535307552, 0.11777703125142322, 0.13925999316742377, 0.060056000718142204, 0.0679272994868055] |
| a10_sweep/('rbf', 8, 16)/mass | 0.49 | 0.47 |
| a10_sweep/('rbf', 8, 16)/max_marginal | 0.253257 | 0.260168 |
| a10_sweep/('rbf', 8, 16)/sw | 0.127551 | 0.111852 |
| a10_sweep/('rbf', 10, 32)/energy | 0.0226583 | 0.0169889 |
| a10_sweep/('rbf', 10, 32)/marginal_w2 | [0.1748657521942533, 0.20967679796361885, 0.23077687157920748, 0.2346897002773661, 0.1678060777408195, 0.21714364667818814, 0.14974870914113306, 0.16567104146017164, 0.0720088295280532, 0.12923660819129668] | [0.1689549399187243, 0.14717946557270759, 0.18545910173104374, 0.2068560204940633, 0.15252730170016288, 0.16447513200962674, 0.11924755299835345, 0.1221937183332094, 0.08330378948224021, 0.1323653952388524] |
| a10_sweep/('rbf', 10, 32)/mass | 0.505 | 0.506 |
| a10_sweep/('rbf', 10, 32)/max_marginal | 0.23469 | 0.206856 |
| a10_sweep/('rbf', 10, 32)/sw | 0.161925 | 0.132053 |
| a10_sweep/('rbf', 8, 32)/energy | 0.0171306 | 0.01518 |
| a10_sweep/('rbf', 8, 32)/marginal_w2 | [0.2574687541650441, 0.18192657768733309, 0.1273856541904639, 0.19878923729214987, 0.14464510907183634, 0.16603447771208765, 0.11552333619406582, 0.13949930513557146, 0.04465948454895165, 0.10450082329862657] | [0.25503458268842455, 0.15968255599555967, 0.1315155074327407, 0.21922216808022854, 0.13405787622554818, 0.11341822553941341, 0.08152595170584813, 0.08036798546916218, 0.046838389647327804, 0.05140231821279215] |
| a10_sweep/('rbf', 8, 32)/mass | 0.509 | 0.517 |
| a10_sweep/('rbf', 8, 32)/max_marginal | 0.257469 | 0.255035 |
| a10_sweep/('rbf', 8, 32)/sw | 0.123205 | 0.103295 |
| a10_sweep/('rbf', 10, 64)/energy | 0.0194987 | 0.0101358 |
| a10_sweep/('rbf', 10, 64)/marginal_w2 | [0.17037731955807484, 0.19229804707370116, 0.2572015844660485, 0.23251565243649278, 0.15175429025779147, 0.10692647249888773, 0.07214455235152134, 0.11647741892887674, 0.03643105528052495, 0.10252282741666985] | [0.16621603469057544, 0.11266850624449953, 0.10751440019375107, 0.10228131678093387, 0.09181021195495156, 0.12364001622609923, 0.07032386579221596, 0.1005726918615845, 0.05745885369211528, 0.06575291117260626] |
| a10_sweep/('rbf', 10, 64)/mass | 0.497 | 0.505 |
| a10_sweep/('rbf', 10, 64)/max_marginal | 0.257202 | 0.166216 |
| a10_sweep/('rbf', 10, 64)/sw | 0.127601 | 0.0838256 |
| a10_sweep/('rbf', 8, 64)/energy | 0.0102221 | 0.0102803 |
| a10_sweep/('rbf', 8, 64)/marginal_w2 | [0.2719154045101617, 0.11996865304818152, 0.10814242136637213, 0.13628203976044673, 0.08563554364029491, 0.09083984963772927, 0.06568469344952045, 0.07226240251226652, 0.04969854780544049, 0.0930418540629798] | [0.2797037015060883, 0.13512471784612248, 0.13221766263263315, 0.09766254172664482, 0.10090751954941714, 0.10116410550767985, 0.06844619200806752, 0.09649431395209847, 0.055114625405361425, 0.05573928685524525] |
| a10_sweep/('rbf', 8, 64)/mass | 0.497 | 0.499 |
| a10_sweep/('rbf', 8, 64)/max_marginal | 0.271915 | 0.279704 |
| a10_sweep/('rbf', 8, 64)/sw | 0.0838638 | 0.0875645 |
| Product seed correction / 10D / FD / sw / mean | 0.014392 | 0.0151089 |
| Product seed correction / 10D / FD / sw / std | 0.00211542 | 0.000259887 |
| Product seed correction / 10D / FD / sw / median | 0.0150382 | 0.0151027 |
| Product seed correction / 10D / FD / energy / mean | 0.00480532 | 0.00471939 |
| Product seed correction / 10D / FD / energy / std | 0.000740661 | 0.000714092 |
| Product seed correction / 10D / FD / energy / median | 0.00447503 | 0.00446088 |
| Product seed correction / 10D / FD / max_marginal / mean | 0.0183738 | 0.0187869 |
| Product seed correction / 10D / FD / max_marginal / std | 0.00112932 | 0.00138984 |
| Product seed correction / 10D / FD / max_marginal / median | 0.0185257 | 0.0186488 |
| Product seed correction / 10D / FD / negative_count_tv / mean | 0.007605 | 0.008045 |
| Product seed correction / 10D / FD / negative_count_tv / std | 0.00237609 | 0.00151556 |
| Product seed correction / 10D / Koopman (RBF) / sw / mean | 0.0192123 | 0.0195091 |
| Product seed correction / 10D / Koopman (RBF) / sw / std | 0.00269586 | 0.0021055 |
| Product seed correction / 10D / Koopman (RBF) / energy / mean | 0.00501986 | 0.00497058 |
| Product seed correction / 10D / Koopman (RBF) / energy / std | 0.00104798 | 0.00103679 |
| Product seed correction / 10D / Koopman (RBF) / energy / median | 0.00493046 | 0.00492219 |
| Product seed correction / 10D / Koopman (RBF) / max_marginal / mean | 0.0356567 | 0.0356087 |
| Product seed correction / 10D / Koopman (RBF) / max_marginal / std | 0.00549614 | 0.00559294 |
| Product seed correction / 10D / Koopman (RBF) / negative_count_tv / mean | 0.008725 | 0.00917 |
| Product seed correction / 10D / Koopman (RBF) / negative_count_tv / std | 0.00297314 | 0.00213661 |
| Product seed correction / 10D / Koopman (Legendre) / sw / mean | 0.0192175 | 0.0195119 |
| Product seed correction / 10D / Koopman (Legendre) / sw / std | 0.0026997 | 0.00211656 |
| Product seed correction / 10D / Koopman (Legendre) / energy / mean | 0.00502096 | 0.00497257 |
| Product seed correction / 10D / Koopman (Legendre) / energy / std | 0.0010474 | 0.00103688 |
| Product seed correction / 10D / Koopman (Legendre) / energy / median | 0.00493176 | 0.00492537 |
| Product seed correction / 10D / Koopman (Legendre) / max_marginal / mean | 0.0353326 | 0.0353526 |
| Product seed correction / 10D / Koopman (Legendre) / max_marginal / std | 0.00570465 | 0.00566363 |
| Product seed correction / 10D / Koopman (Legendre) / negative_count_tv / mean | 0.00854 | 0.008995 |
| Product seed correction / 10D / Koopman (Legendre) / negative_count_tv / std | 0.00285373 | 0.00202655 |
| Product seed correction / 50D / FD / sw / mean | 0.01495 | 0.0157561 |
| Product seed correction / 50D / FD / sw / std | 0.00256235 | 0.000189025 |
| Product seed correction / 50D / FD / energy / mean | 0.0109914 | 0.0111055 |
| Product seed correction / 50D / FD / energy / std | 0.000966995 | 0.000929625 |
| Product seed correction / 50D / FD / energy / median | 0.0107 | 0.0110142 |
| Product seed correction / 50D / FD / max_marginal / mean | 0.0196882 | 0.020056 |
| Product seed correction / 50D / FD / max_marginal / std | 0.00107201 | 0.000929031 |
| Product seed correction / 50D / FD / max_marginal / median | 0.0198143 | 0.0200628 |
| Product seed correction / 50D / FD / negative_count_tv / mean | 0.018105 | 0.0191 |
| Product seed correction / 50D / FD / negative_count_tv / std | 0.00460172 | 0.0024204 |
| Product seed correction / 50D / Koopman (RBF) / sw / mean | 0.0179151 | 0.0187747 |
| Product seed correction / 50D / Koopman (RBF) / sw / std | 0.00239346 | 0.00119452 |
| Product seed correction / 50D / Koopman (RBF) / sw / median | 0.0187033 | 0.0188975 |
| Product seed correction / 50D / Koopman (RBF) / energy / mean | 0.0114805 | 0.0116048 |
| Product seed correction / 50D / Koopman (RBF) / energy / std | 0.000862475 | 0.000859096 |
| Product seed correction / 50D / Koopman (RBF) / energy / median | 0.0112618 | 0.011747 |
| Product seed correction / 50D / Koopman (RBF) / max_marginal / mean | 0.038394 | 0.0386993 |
| Product seed correction / 50D / Koopman (RBF) / max_marginal / std | 0.00471947 | 0.00469211 |
| Product seed correction / 50D / Koopman (RBF) / max_marginal / median | 0.0384418 | 0.0392486 |
| Product seed correction / 50D / Koopman (RBF) / negative_count_tv / mean | 0.01801 | 0.019095 |
| Product seed correction / 50D / Koopman (RBF) / negative_count_tv / std | 0.00439588 | 0.00283651 |
| Product seed correction / 50D / Koopman (RBF) / negative_count_tv / median | 0.0183 | 0.01915 |
| Product seed correction / 50D / Koopman (Legendre) / sw / mean | 0.0179415 | 0.0187978 |
| Product seed correction / 50D / Koopman (Legendre) / sw / std | 0.00239189 | 0.00119715 |
| Product seed correction / 50D / Koopman (Legendre) / sw / median | 0.0187366 | 0.0189226 |
| Product seed correction / 50D / Koopman (Legendre) / energy / mean | 0.0114816 | 0.0116055 |
| Product seed correction / 50D / Koopman (Legendre) / energy / std | 0.000862905 | 0.000859957 |
| Product seed correction / 50D / Koopman (Legendre) / energy / median | 0.0112524 | 0.0117402 |
| Product seed correction / 50D / Koopman (Legendre) / max_marginal / mean | 0.0384388 | 0.0387271 |
| Product seed correction / 50D / Koopman (Legendre) / max_marginal / std | 0.00485115 | 0.00482756 |
| Product seed correction / 50D / Koopman (Legendre) / max_marginal / median | 0.0379697 | 0.0389728 |
| Product seed correction / 50D / Koopman (Legendre) / negative_count_tv / mean | 0.01804 | 0.019095 |
| Product seed correction / 50D / Koopman (Legendre) / negative_count_tv / std | 0.00391924 | 0.00237667 |
| Product seed correction / 50D / Koopman (Legendre) / negative_count_tv / median | 0.01845 | 0.01915 |


## Files and reproduction

This is the only experiment-results Markdown file. Numerical data are stored in four checksum-verified archives: `outputs/data/ou.zip`, `double_well.zip`, `alanine.zip` and `shared.zip`. The revision records, raw public alanine trajectories needed for role rotations, configuration snapshots and the baseline used for pairing are archive members under `outputs/revision/` in `double_well.zip`. The Git-visible `outputs/revision_results.json` publishes all group-B per-realisation records, summaries and follow-up diagnostics without the large arrays. PDFs remain in `outputs/figures/`.

Use Python 3.11, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.1, threadpoolctl 3.6.0 and Numba 0.64.0. Each numerical process uses one BLAS thread. The queue may run four independent synthetic repetitions concurrently, or two product repetitions with eight coordinate workers each. Alanine role rotations use four independent transport processes after their three spectra have been fitted sequentially. The equal-data comparison and alanine cost measurements run alone. Concurrent elapsed times are descriptive and are not used to rank samplers. Only one managed archive session may be open at a time.

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 --with numba==0.64.0 python -u -B supplementary/revision_queue.py
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 --with numba==0.64.0 python -B supplementary/revision_verify.py
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 --with numba==0.64.0 python -B supplementary/revision_publish.py
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 python -B supplementary/revision_figures.py
python -B supplementary/experiment_store.py verify
```

The queue resumes completed prescribed revision rows; it does not replace failed seeds. Each run retains its configuration and available endpoint; the B4 transports also retain per-path masks, including available masks from failed attempts. For a fresh repetition, use a separate checkout with the corresponding revision result rows absent while preserving the baseline snapshots and shared input/reference archives. The publisher validates prescribed seed sets, regenerates the numerical tables, and updates this single report. The figure command reads the published results only. `BKT_experiments.ipynb` calls the same numerical runners, avoiding a second implementation of the revision protocol.

For the fixed follow-up, run `python -u -B supplementary/revision_followup.py run` in the same pinned environment, then run `revision_verify.py`, `revision_publish.py` and `revision_figures.py --products-only`. It adds product index 10 (source 11, training 1011), excludes the dependent index 6, and performs exactly three distinct alanine integrations with both budgets multiplied by five. Saved follow-up integrations are reused. The original spectra and numerical controls are preserved; the optional confined multiwell study is not run. Do not run two managed archive sessions concurrently.

The unchanged matched OU P/I/S experiment retains its 180 runs, ranks 10, 20, 40, two steps and ten source seeds. Its dedicated runner is `ou_path_validation.py`. The original alanine distribution and convergence figures retain the same three Fourier BKT trajectories at s=8; the RBF failure and control remain explicit limitations. B3 cost repetitions and all six trajectory-role pairs are additions, rather than substitutions for the original figure data. Analytical OU distances use the Gaussian reference; alanine SW2 uses its fixed periodic embedding.

`manuscript_results.py` regenerates this report without simulations. `--tables` regenerates CSV tables; `--check` checks canonical endpoint distances and the retained matched OU calculations. `alanine_experiment.py --stage verify` and `alanine_convergence.py --stage verify` check their original saved clouds. The latter checks the frozen protocol and inputs and reports the stored/current source-code fingerprints separately: adding path observations changes the source hash. Fresh run and shard provenance checks remain strict. The revision audit separately records endpoint and scalar solver-reproduction discrepancies without overwriting the archived baseline.

The shared printed typography is defined in `figure_style.py`: overall title 11 pt, panel title 9.5 pt, axis label 9 pt, ticks 8.5 pt, legend 8 pt, all normal weight. Canvas dimensions and manuscript insertion widths determine export scaling. Where manuscript sources are absent, frozen widths from the retained PDFs are used. The admissible-source rank figure remains 1-by-4. Product histograms use source seed 1, while their marginal-error panels show mean and sample SD over the ten prescribed realisations. Error bars are not confidence intervals.

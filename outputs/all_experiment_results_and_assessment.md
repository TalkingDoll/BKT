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
| 10D OU | Coupling 0 and 0.15; M=5000; 30 modes/coordinate; T=6; h=0.05; seeds 700-702. |
| 2D double wells | beta=0,0.25,0.5,1; M=2000; n=200000; r=64; RBF J=145; FD-201; T=8/lambda1; h=0.05. |
| 4/9 wells | M=2000; n=200000; r=64; RBF/Legendre/FD-201; h=0.02; five/three seeds. |
| 10D double wells | beta=0,0.5; M=1000; n=100000; r=16; RBF J=657; h=0.05; two seeds. |
| 10D/50D double-well products | M=20000; n=200000; r=16 per coordinate; T=10.6854; h=0.02; one fixed cloud. |
| Equal-data comparison | beta=0,0.5; n=200000 shared pairs; M=2000; five paired seeds; common horizon. |

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
| 0.0 | 0.0221 +/- 0.0005 | 0.0262 +/- 0.0026 | 0.0447 +/- 0.0051 |
| 0.15 | 0.0196 +/- 0.0007 | 0.0235 +/- 0.0018 | 0.0450 +/- 0.0055 |


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
| 2D double well product, beta=0 | 0.0281 +/- 0.0026 | 0.0288 +/- 0.0032 | 0.0280 +/- 0.0027 | 0.0397 +/- 0.0076 |
| 2D double well, beta=0.25 | 0.0288 +/- 0.0025 | 0.0294 +/- 0.0020 | 0.0285 +/- 0.0012 | 0.0410 +/- 0.0084 |
| 2D double well, beta=0.5 | 0.0294 +/- 0.0025 | 0.0318 +/- 0.0039 | 0.0293 +/- 0.0030 | 0.0420 +/- 0.0099 |
| 2D double well, beta=1 | 0.0276 +/- 0.0017 | 0.0272 +/- 0.0018 | 0.0270 +/- 0.0017 | 0.0417 +/- 0.0119 |
| 2D four-well product | 0.0237 | 0.0281 +/- 0.0021 | 0.0269 +/- 0.0020 | 0.0433 +/- 0.0083 |
| 2D nine wells | 0.0364 | 0.0610 +/- 0.0026 | 1.4651 +/- 1.3353 | 0.0340 +/- 0.0075 |
| 10D double well product, beta=0 | 0.0544 | 0.0575 +/- 0.0043 | 0.0701 +/- 0.0033 | 0.0590 +/- 0.0042 |
| 10D double well, beta=0.5 | -- | 0.1454 +/- 0.0253 | 0.2209 +/- 0.0104 | 0.0507 +/- 0.0034 |
| 10D double-well product | 0.0149 | 0.0200 | 0.0200 | 0.0156 +/- 0.0014 |
| 50D double-well product | 0.0153 | 0.0170 | 0.0171 | 0.0162 +/- 0.0008 |

Double wells and four wells reach the reference scale; nine wells and coupled 10D remain above it. Nine-well Legendre seed errors are 1.637, 2.706, 0.052. All are retained. The product results rely on separability: the potential is a sum of coordinate potentials and the invariant density is a product. The uncoupled 10D double well has one double-well factor and nine stationary N(0, 0.5) factors; the 10D/50D double-well products have a double-well factor in every coordinate.

| Product | RBF worst marginal W2 | Reference worst marginal W2 | RBF energy | Reference energy | RBF negative-count TV | Reference negative-count TV |
|---|---|---|---|---|---|---|
| 10 | 0.0391 | 0.0260 +/- 0.0055 | 0.0052 | 0.0052 +/- 0.0013 | 0.0132 | 0.0095 +/- 0.0035 |
| 50 | 0.0393 | 0.0297 +/- 0.0045 | 0.0106 | 0.0120 +/- 0.0010 | 0.0175 | 0.0165 +/- 0.0032 |

### Appendix sensitivity results

Rank scans use the first source seed; they retain nonmonotone and unstable results. The complete 2D ranks, paired step checks and safeguard counts remain in the 156-run admissible-source suite.

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
| Koopman (RBF) | 8 | 16 | 0.1276 |
| Koopman (RBF) | 8 | 32 | 0.1232 |
| Koopman (RBF) | 8 | 64 | 0.0839 |
| Koopman (RBF) | 10 | 16 | 0.1403 |
| Koopman (RBF) | 10 | 32 | 0.1619 |
| Koopman (RBF) | 10 | 64 | 0.1276 |
| Koopman (Legendre) | 3 | 16 | 0.2136 |
| Koopman (Legendre) | 3 | 32 | 0.2569 |
| Koopman (Legendre) | 3 | 64 | 0.2630 |
| Koopman (Legendre) | 4 | 16 | 0.1990 |
| Koopman (Legendre) | 4 | 32 | 0.2431 |
| Koopman (Legendre) | 4 | 64 | 0.2431 |

The coupled 10D dictionary comparison uses n=100000 and the first seed. Its horizon changes with the fitted eigenvalue; no configuration reaches the reference.

| System | n=10000 | n=100000 | n=200000 |
|---|---|---|---|
| 2D double well product, beta=0 | 0.0340 +/- 0.0040 | 0.0296 +/- 0.0019 | 0.0288 +/- 0.0032 |
| 2D double well, beta=0.25 | 0.0383 +/- 0.0027 | 0.0323 +/- 0.0014 | 0.0294 +/- 0.0020 |
| 2D double well, beta=0.5 | 0.0353 +/- 0.0077 | 0.0321 +/- 0.0040 | 0.0318 +/- 0.0039 |
| 2D double well, beta=1 | 0.0419 +/- 0.0083 | 0.0281 +/- 0.0015 | 0.0272 +/- 0.0018 |
| 2D four-well product | 0.0542 +/- 0.0144 | 0.0307 +/- 0.0041 | 0.0281 +/- 0.0021 |
| 2D nine wells | 0.1012 +/- 0.0316 | 0.0636 +/- 0.0030 | 0.0610 +/- 0.0026 |
| 10D double well product, beta=0 | 0.0712 +/- 0.0011 | 0.0575 +/- 0.0043 | 0.0592 +/- 0.0025 |
| 10D double well, beta=0.5 | 0.1600 +/- 0.0136 | 0.1454 +/- 0.0253 | 0.1846 +/- 0.0071 |


| 2D beta | Independent I | Same-sample S |
|---|---|---|
| 0.0 | 0.0525 +/- 0.0096 | 0.0288 +/- 0.0032 |
| 0.25 | 0.0543 +/- 0.0162 | 0.0294 +/- 0.0020 |
| 0.5 | 0.0516 +/- 0.0108 | 0.0318 +/- 0.0039 |
| 1.0 | 0.0433 +/- 0.0099 | 0.0272 +/- 0.0018 |

I uses an extra 2000 independent source draws, with coefficients fixed thereafter. The original coupled full-plane Gaussian source violates the bounded-ratio assumption at positive coupling. Variance 0.3 restores this source condition for the four 2D cases; box projection and estimated eigenpairs still prevent verification of every theorem hypothesis.

## Equal-data comparison

| beta | Method | SW2 | Fit + sampling seconds | Reference-threshold hits |
|---|---|---|---|---|
| 0.0 | BKT | 0.0288 +/- 0.0032 | 9.7 +/- 0.5 | 5/5 |
| 0.0 | Drift + Langevin | 0.2036 +/- 0.0313 | 48.9 +/- 4.5 | 0/5 |
| 0.0 | KDE particle flow | 0.0354 +/- 0.0044 | 51.8 +/- 1.5 | 5/5 |
| 0.5 | BKT | 0.0318 +/- 0.0039 | 8.7 +/- 0.8 | 5/5 |
| 0.5 | Drift + Langevin | 0.2391 +/- 0.0548 | 38.3 +/- 2.7 | 0/5 |
| 0.5 | KDE particle flow | 0.0446 +/- 0.0318 | 44.5 +/- 1.5 | 4/5 |


| beta | Independent-target reference SW2 | Crossing threshold |
|---|---|---|
| 0.0 | 0.0397 +/- 0.0076 | 0.0473 |
| 0.5 | 0.0420 +/- 0.0099 | 0.0519 |

All six entries use five paired realisations and report means +/- sample standard deviations. The source is the same as in the main two-dimensional double-well experiments: a cosine-squared first-coordinate bump on [0.4,1.6] and an independent centred Gaussian second coordinate with variance 0.3. Its density ratio is bounded for both coupling values, since 0.3 < 1/(2+beta).

The 200000 trajectory pairs per seed, target clouds, ten-pair reference statistics and 64 projection directions are unchanged. All 30 transports and the ten spectral and ten drift fits were recomputed. Single-thread costs are measured per run and exclude common input generation and metric callbacks; the shared measured drift-fit cost is charged separately to each baseline. The BKT clouds and observation-time errors are checked against the corresponding main variance-0.3 results.

The common horizons are T=10.7 for beta=0 and T=9.4 for beta=0.5. A reference-threshold crossing means SW2 at a prescribed common observation time is no greater than the independent-target-pair reference mean plus one sample standard deviation. The count is not restricted to the terminal observation and does not use the reference mean alone.

Projection of training trajectories, reference samples and transported particles onto the numerical box remains a separate approximation; intermediate RK stages are also projected. The KDE method interacts through its evolving particle density. The fitted-drift Langevin clouds again show widened tails and boundary accumulation; the saved endpoint diagnostics do not isolate the causes. These comparisons concern the stated fitted models and discretisations, not a general ranking of the methods.

### Manuscript integration

The table above and [updated comparison figure](figures/fig_data_comparison.pdf) replace the equal-data values in Section 5 and Appendix D.2. The manuscript text and its figure copy are left for author integration. Remove the old variance-0.5 source qualification and retain the description of box projection. The figure displays errors, while costs are given in the text and table; adjust the caption accordingly. The unified variance-0.3 statement applies to the two-dimensional V_beta experiments; the uncoupled ten-dimensional experiment retains nine stationary Gaussian coordinates of variance 0.5.

Suggested interpretation (all prescribed realisations retained):

> Under this fixed protocol, BKT has the smallest mean terminal sliced Wasserstein distance and the lowest mean fitting-plus-sampling cost at both coupling values.
> At beta=0, the numbers of realisations that cross the reference threshold are BKT 5/5, Drift + Langevin 0/5, KDE particle flow 5/5.
> At beta=0.5, the numbers of realisations that cross the reference threshold are BKT 5/5, Drift + Langevin 0/5, KDE particle flow 4/5.
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

The current manuscript retains eleven figure PDFs, one experiment report, fixed configurations and four checksum-verified archives. Koopman (RBF) and Koopman (Legendre) describe the dictionary used for the reversible gEDMD generator estimate; every such curve uses the same BKT transport formula.

Data attribution: the [mdshare alanine page](https://markovmodel.github.io/mdshare/ALA2/) documents the simulations and publication credits, including Nueske et al. (2017), cited in the manuscript. The Computational Molecular Biology Group, Freie Universitaet Berlin, supplies the data under the [mdshare CC BY 4.0 terms](https://markovmodel.github.io/mdshare/). Retained arrays use float64 conversion and the fixed subsampling described above.

The equal-data comparison now contains 30 freshly computed variance-0.3 transports with individual fit and sampling times. Its source-independent inputs are checked against the previous protocol, and its ten BKT results are checked against the main variance-0.3 experiment. Other retained numerical experiments are unchanged. The earlier reproduction audit checked all 156 admissible-source endpoints and 112 notebook transport caches, reran all 180 matched OU transports, and checked 155 synthetic and 44 alanine table entries. The paired alanine archive contains 1593 BKT/LAWGD/KDE checkpoints; their SW2 and basin TV are checked against the saved clouds by the verification command.

The alanine distribution summary uses the three BKT endpoints at s=8 from the convergence archive, with their original sources and evaluation clouds. The saved input file contains only the 256 retained eigenpairs and the three source/reference designs needed by this experiment. No independent set of Fourier transport results is used for the distribution figure. The RBF controls remain as explicit limitations.

Reference distances describe sampling variability and are not lower bounds for transport. In the equal-data comparison, a reference-threshold crossing uses the reference mean plus one sample standard deviation at a prescribed observation time. The two-dimensional admissible source has harmonic variance 0.3; the uncoupled ten-dimensional source has nine stationary harmonic coordinates of variance 0.5.

FD-201 uses a 201-by-201 grid for two-dimensional systems; the high-dimensional FD comparisons use separable one-dimensional factors. Separable high-dimensional experiments do not establish performance on general coupled targets. The nine-well and coupled-10D limitations remain. The angular-marginal example does not test physical molecular kinetics.

The same-sample comparison requires the stated common-region assumptions. Its coefficient factor is Delta_M = M^(-1/2) sum_k sqrt(Var(phi_k)); bounded individual variances give O(r/sqrt(M)), with possible additional rank dependence in the stability factor. Initial empirical coefficients do not imply exact spectral moments of the transported particles. These numerical checks do not constitute an independent proof review.

## Files and reproduction

This is the only Markdown document for experiment results, limitations, fixed protocols, reproduction commands and figure conventions. One notebook, fixed supplementary runners, four checksum-verified archives and PDF figures form the retained package.

[OU data](data/ou.zip) | [Double/multiwell data](data/double_well.zip) | [Alanine inputs, parameters and results](data/alanine.zip) | [Shared references and results](data/shared.zip).

[OU](figures/fig_ou.pdf), [10D OU](figures/fig_ou10.pdf), [10D OU marginals](figures/fig_ou10_marginals.pdf), [matched paths](figures/fig_ou_path_comparison.pdf), [double-well ranks](figures/fig_admissible_source_ranks.pdf), [coefficient regimes](figures/fig_admissible_source_coefficients.pdf), [equal-data comparison](figures/fig_data_comparison.pdf), [10D double-well product](figures/fig_hd10_dictionaries.pdf), [50D double-well product](figures/fig_hd50_dictionaries.pdf), [256-mode alanine distribution](figures/fig_alanine.pdf), [three-method alanine convergence](figures/fig_alanine_convergence.pdf).

### Environment and data

Run from the project root with Python 3.11, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.1 and threadpoolctl 3.6.0. The additional alanine KDE implementation also requires Numba 0.64.0. `uv run --with ...` can supply these versions without changing a global environment.

Four archives under `outputs/data/` contain the numerical inputs, parameters and results:

| Archive | Contents |
|---|---|
| `ou.zip` | 1D/10D OU, matched P/I/S paths and numerical diagnostics |
| `double_well.zip` | Double/multiwell and product systems, manuscript sensitivity studies and equal-data comparison |
| `alanine.zip` | Dataset, 256-mode Fourier inputs, RBF diagnostics and paired BKT/LAWGD/KDE trajectories with their periodic target-score fit |
| `shared.zip` | Notebook result index, shared reference data and implementation checks |

`catalog.json` and each archive manifest record member paths, sizes and SHA-256 hashes. The synthetic runners unpack the required data and verify/repack on exit; the alanine verification and plotting routines read the archives directly. Only one independent unpacked data session may be open at a time. The notebook keeps its session open until its final cell or kernel exit; close it manually with `experiment_store.close_notebook_store()` if needed. A setup cell reopens it.

```powershell
python -B supplementary/experiment_store.py verify
python -B supplementary/experiment_store.py list alanine
python -B supplementary/experiment_store.py read outputs/alanine/config.json
uv run --with numpy==2.4.6 python -B supplementary/manuscript_results.py
```

The report command reads saved data directly and runs no experiments. It is the only report generator. `--tables` exports the current manuscript CSV tables, using the admissible-source 2D results and including the coupled-10D limitation. PDFs remain in `outputs/figures/`; plotting reads saved arrays and shares the notebook font sizes and spacing.

For a numerical consistency check without changing saved results:

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/manuscript_results.py --check
```

This checks all 156 admissible-source and 30 equal-data endpoint clouds and reruns all 180 matched OU transports, residual integrals and safeguard counts. The alanine checks below cover its saved clouds and spectrum/transport reproduction separately.

### Synthetic systems

`BKT_experiments.ipynb` contains the numerical definitions, fixed main configurations and manuscript sensitivity studies. Run cells in order to reproduce. Existing compatible caches are reused. The main training sizes are frozen; the appendix rank, sample-size, time and particle-count studies are intentional manuscript results. The obsolete original-source 2D scans and their plotting cells have been removed. Four compact original-source entries in the shared result index supply only the references, horizons and parity values required by the retained supplementary runners; the current 2D results come from `admissible_source`.

| Additional study | Fixed parameters | Runner | Plotting from saved data |
|---|---|---|---|
| Matched OU paths | `ou_path_config.json` | `ou_path_validation.py` | `plot_ou_path_validation.py` |
| Admissible 2D source and I/S coefficients | `admissible_source_config.json` | `run_admissible_source.py` | `plot_admissible_source.py` |
| Equal-data comparison | `data_comparison_config.json` | `run_data_comparison.py` | `plot_data_comparison.py` |

All paths in the table are under `supplementary/`. The last two runners accept `--resume`; completed matching runs are reused. The equal-data runner also requires matching numerical-code and runtime provenance, saved endpoint checksums and individual timings; variance-0.5 records cannot be resumed under the current protocol. The OU runner refuses to overwrite completed runs. `audit_source_assumptions.py` checks the source/domain assumptions, and `diagnose_data_comparison_endpoints.py` checks the retained comparison endpoints.

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 python -B supplementary/ou_path_validation.py --check
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/run_admissible_source.py --resume
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/run_data_comparison.py --resume
```

For a fresh equal-data reproduction, retain the canonical comparison archive and shared training/reference caches, then append `--output-directory tmp/equal_data_reproduction` to the comparison command, using a previously unused directory and omitting `--resume`. The canonical source-independent input records are required for provenance checks, while every fit and transport is recomputed in the new directory. For other completed synthetic studies, use a separate workspace with that study's saved outputs absent but its shared input caches retained. No parameter search is performed.

### Alanine reproduction

The distribution and convergence figures use the same 256-mode BKT trajectories, the same three source/reference designs and the same endpoint s=8. `alanine_experiment.py` verifies the inputs, reproduces the spectral transport, plots the distribution figure and retains the RBF diagnostics. `alanine_convergence.py` handles the paired BKT/LAWGD/KDE trajectories. The archive retains only the inputs and results needed by these experiments; its RBF file includes all eight diagnostic realisations.

The five members under `outputs/alanine/` are `config.json`, `dataset.npz`, `results.npz`, `lawgd_convergence.npz` and `rbf_diagnostic.npz`. Despite its filename, `results.npz` contains the shared spectral inputs and three source/reference designs; the trajectory arrays and endpoint distribution summary are stored together in `lawgd_convergence.npz`. The 3249 dictionary functions are needed to estimate the retained 256 eigenpairs and are not 3249 transported modes.

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --stage verify
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --stage reproduce --seed 1101 --refit
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --case rbf --stage verify
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --case rbf --stage reproduce --seed 301
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 --with matplotlib==3.11.1 python -B supplementary/alanine_experiment.py --stage plot
```

`verify` recalculates metrics from saved clouds. `reproduce` reruns transport and checks against retained results; omit `--seed` for every seed. Fourier `--refit` rebuilds the spectrum; the small RBF spectrum is always refitted during reproduction. Retained particle arrays are not overwritten.

The alanine distribution PDF uses seed 1101 at s=8 for the angle panels and all three paired seeds for SW2. The coefficients are empirical moments of the initial particles, as in the convergence figure. There is no overall title or seed subtitle. The source-design and evaluation caveats appear in the Alanine section above and notebook notes.

The paired convergence figure uses `supplementary/alanine_convergence.py` and `supplementary/alanine_baselines.py`; its complete protocol is in [Three-method alanine convergence](#three-method-alanine-convergence). All nine prescribed runs reach s=8. The archive member `outputs/alanine/lawgd_convergence.npz` retains their checkpoint clouds, parameters, provenance, fixed target-score fit and numerical checks. BKT/LAWGD arrays reuse the s <= 8 prefixes of the original s=10 trajectories, recorded under `reused_from.original_horizon`; KDE is computed directly through s=8. The runner reproduces simulations or plots retained data:

```powershell
python -B supplementary/alanine_convergence.py --stage run --seed 1101
python -B supplementary/alanine_convergence.py --stage run --seed 1102
python -B supplementary/alanine_convergence.py --stage run --seed 1103
python -B supplementary/alanine_convergence.py --stage collect
python -B supplementary/alanine_convergence.py --stage verify
python -B supplementary/alanine_convergence.py --stage plot
python -B supplementary/experiment_store.py pack alanine
python -B supplementary/manuscript_results.py
```

Run these commands in the pinned environment above, including Numba 0.64.0. `run` writes temporary per-seed shards; `collect` verifies and merges them with the fitted-score metadata and KDE numerical checks into one result file. The retained archive contains the merged file, so `verify` and `plot` work directly from the archive. Temporary shards are unnecessary after the verified merge is archived. BKT/LAWGD spectral settings and the source/reference designs are retained; KDE has its own recorded periodic density estimates and integration controls.

By default, matching archived BKT/LAWGD trajectories are reused and new KDE trajectories are computed. With fresh temporary shards, add `--recompute-spectral` to rerun the spectral transports too. `--method KDE` selects only KDE. Compatible archived KDE checks are retained during collection.

`fig_alanine_convergence.pdf` uses one panel, a logarithmic error axis, the normalized interval [0, 8], and mean +/- sample SD over three paired designs. `ALANINE_DISPLAY_HORIZON` and `ALANINE_METHOD_LABELS` in `manuscript_results.py` define the shared report/figure window and labels. At its current manuscript insertion width of 0.62 textwidth it matches the printed font sizes of `fig_alanine.pdf`; there is no overall title or seed subtitle.

### Figure typography

`PAPER_FONT_SIZES` in `supplementary/figure_style.py` specifies the actual printed sizes for all manuscript figures: overall titles 11 pt, panel titles 9.5 pt, axis labels 9 pt, ticks 8.5 pt and legends 8 pt. Fonts are DejaVu Sans with normal weight. The plotting functions compensate for each canvas width and its current LaTeX insertion width, read from the manuscript files, so the number of panels does not reduce the printed font size. Subplot dimensions may differ.

Regenerate the affected PDFs after changing an insertion width. Manuscript PDFs export the full canvas without tight cropping, which would change the scaling calculation. The admissible-source rank figure uses a 1-by-4 layout; compact panels use shorter axis labels and fewer major tick labels, with every data point retained. Plot margins, title spacing and legend rows accommodate the printed sizes.

# Manuscript experiment results

Retained results include favorable and unfavorable manuscript cases. Every repeated summary includes all prescribed seeds and uses sample standard deviations. Alanine retains one 256-mode Fourier experiment with distribution and convergence figures.

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
| 10D double well product | beta=0; M=1000; n=100000; r=16; RBF J=657; h=0.05; ten seeds; independent mode selection. |
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
| 10D double-well product | 0.0151 +/- 0.0003 | 0.0195 +/- 0.0021 | 0.0195 +/- 0.0021 | 0.0156 +/- 0.0014 |
| 50D double-well product | 0.0158 +/- 0.0002 | 0.0188 +/- 0.0012 | 0.0188 +/- 0.0012 | 0.0162 +/- 0.0008 |

The table summarizes ten prescribed realisations per repeated cell. Reference distances measure finite-sample variability. Nine-well Legendre seed errors are 1.637, 2.706, 0.052, 0.048, 0.902, 1.257, 2.038, 0.036, 0.045, 0.036. All are retained. The product results rely on separability: the potential is a sum of coordinate potentials and the invariant density is a product. The uncoupled 10D double well has one double-well factor and nine stationary N(0, 0.5) factors; the 10D/50D double-well products have a double-well factor in every coordinate.
The 10D/50D product summaries use ten indices s=0--5,7--10. Source seed 1+s differs from target seed 7 for every realisation; training seed is 1001+s. All methods share the target, reference statistics and projection directions.

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


| System | n=10000 | n=100000 | n=200000 |
|---|---|---|---|
| 2D double well product, beta=0 | 0.0345 +/- 0.0041 | 0.0285 +/- 0.0025 | 0.0276 +/- 0.0027 |
| 2D double well, beta=0.25 | 0.0364 +/- 0.0043 | 0.0309 +/- 0.0037 | 0.0295 +/- 0.0027 |
| 2D double well, beta=0.5 | 0.0373 +/- 0.0077 | 0.0308 +/- 0.0039 | 0.0305 +/- 0.0043 |
| 2D double well, beta=1 | 0.0532 +/- 0.0201 | 0.0284 +/- 0.0022 | 0.0273 +/- 0.0027 |
| 2D four-well product | 0.0475 +/- 0.0128 | 0.0294 +/- 0.0037 | 0.0281 +/- 0.0024 |
| 2D nine wells | 0.0866 +/- 0.0240 | 0.0561 +/- 0.0063 | 0.0548 +/- 0.0063 |
| 10D double well product, beta=0 | 0.0684 +/- 0.0039 | 0.0610 +/- 0.0020 | 0.0603 +/- 0.0042 |


| 2D beta | Independent I | Same-sample S |
|---|---|---|
| 0.0 | 0.0486 +/- 0.0142 | 0.0276 +/- 0.0027 |
| 0.25 | 0.0486 +/- 0.0138 | 0.0295 +/- 0.0027 |
| 0.5 | 0.0476 +/- 0.0111 | 0.0305 +/- 0.0043 |
| 1.0 | 0.0427 +/- 0.0082 | 0.0273 +/- 0.0027 |

I uses an extra 2000 independent source draws, with coefficients fixed thereafter. Harmonic-coordinate variance 0.3 satisfies the bounded-ratio source condition for all four 2D cases; box projection and estimated eigenpairs still prevent verification of every theorem hypothesis.

### Evaluation clouds and reference-normalized errors

For each double-well, multi-well and product system listed below, every transported cloud is compared with the same fixed target cloud (seed 7). Its size equals the number M of transported particles. The reference mean and sample standard deviation use ten independent target-target pairs, with seeds (310000+2b, 310001+2b), b=0,...,9; both clouds in each pair also have size M. The fixed evaluation cloud is not reused as the first member of these reference pairs.


| System | Transported M | Evaluation target size | Size of each reference cloud |
|---|---|---|---|
| 2D double wells, beta=0,0.25,0.5,1 | 2000 | 2000 | 2000 |
| 2D four wells | 2000 | 2000 | 2000 |
| 2D nine wells | 2000 | 2000 | 2000 |
| 10D double well product, beta=0 | 1000 | 1000 | 1000 |
| 10D independent double-well product | 20000 | 20000 | 20000 |
| 50D independent double-well product | 20000 | 20000 | 20000 |


| beta | S: FD-201 / reference mean | S: Koopman (RBF) / reference mean | I: Koopman (RBF) / reference mean |
|---|---|---|---|
| 0.0 | 0.672206 | 0.695829 | 1.225653 |
| 0.25 | 0.689928 | 0.717714 | 1.185136 |
| 0.5 | 0.671428 | 0.727357 | 1.133267 |
| 1.0 | 0.651379 | 0.653344 | 1.023532 |

Ratios use the unrounded ten-realisation mean error divided by the unrounded reference mean, at n=200000, r=64 and h=0.05. The observed range is 0.651379--0.727357 for S across the two spectra, and 1.023532--1.225653 for I with Koopman (RBF). Rounded to two decimal places, these ranges are 0.65--0.73 and 1.02--1.23. The broader interval 0.64--0.74 contains the S values but is not their observed minimum and maximum.

## Equal-data comparison

| beta | Method | SW2 | Fit seconds | Fit + sampling seconds | Reference-threshold hits |
|---|---|---|---|---|---|
| 0.0 | BKT | 0.0276 +/- 0.0027 | 3.1288 | 9.5 +/- 0.5 | 10/10 |
| 0.0 | KDE particle flow | 0.0394 +/- 0.0130 | 1.3218 | 53.6 +/- 1.5 | 9/10 |
| 0.5 | BKT | 0.0305 +/- 0.0043 | 3.2436 | 8.7 +/- 0.2 | 10/10 |
| 0.5 | KDE particle flow | 0.0477 +/- 0.0267 | 1.2957 | 45.9 +/- 0.6 | 8/10 |


| beta | Independent-target reference SW2 | Crossing threshold |
|---|---|---|
| 0.0 | 0.0397 +/- 0.0076 | 0.0473 |
| 0.5 | 0.0420 +/- 0.0099 | 0.0519 |

All four entries use ten paired realisations and report means +/- sample standard deviations. The source is the same as in the main two-dimensional double-well experiments: a cosine-squared first-coordinate bump on [0.4,1.6] and an independent centred Gaussian second coordinate with variance 0.3. Its density ratio is bounded for both coupling values, since 0.3 < 1/(2+beta).

The protocol uses 200000 trajectory pairs per seed, ten-pair reference statistics and 64 projection directions. Each of the 40 retained transports has measured fitting and sampling costs. Single-thread costs exclude common input generation and metric callbacks; the measured drift-fit cost is included in the KDE particle-flow total. The BKT clouds and observation-time errors are checked against the corresponding main variance-0.3 results.

The common horizons are T=10.7 for beta=0 and T=9.4 for beta=0.5. A reference-threshold crossing means SW2 at a prescribed common observation time is no greater than the independent-target-pair reference mean plus one sample standard deviation. The count is not restricted to the terminal observation and does not use the reference mean alone.

Projection of training trajectories, reference samples and transported particles onto the numerical box remains a separate approximation; intermediate RK stages are also projected. The KDE method interacts through its evolving particle density. These comparisons concern the stated fitted models and discretisations, not a general ranking of the methods.

The [comparison figure](figures/fig_data_comparison.pdf) displays errors; costs are given in the table. Both two-dimensional comparison cases use harmonic-coordinate variance 0.3.

Suggested interpretation (all prescribed realisations retained):

> Under this fixed protocol, BKT has the smallest mean terminal sliced Wasserstein distance and the lowest mean fitting-plus-sampling cost at both coupling values.
> At beta=0, the numbers of realisations that cross the reference threshold are BKT 10/10, KDE particle flow 9/10.
> At beta=0.5, the numbers of realisations that cross the reference threshold are BKT 10/10, KDE particle flow 8/10.
> The threshold is the independent-target reference mean plus one sample standard deviation; these finite-sample comparisons do not establish a general ordering of the methods.

For these saved realisations, the terminal-distance counts below the threshold equal the checkpoint-crossing counts in the table. Fit time means eigenpair estimation for BKT and finite-lag drift estimation for KDE particle flow. Timings are the original single-thread measurements; no timings were remeasured for this report revision.

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
Fresh single-thread transport wall times to s=8 are 72.4349 +/- 2.8827 s for BKT, 70.2462 +/- 3.9356 s for LAWGD and 1056.3980 +/- 144.7780 s for KDE; estimation and initial moments are recorded in the fixed-configuration details. BKT and LAWGD have comparable full-horizon costs in this test. Earlier settling in normalized flow time does not by itself establish a lower total computational cost.


Fourier/BKT reproduction check, seed 1101 (spectrum refitted: True): endpoint wrapped RMS difference 1.46e-16 rad; absolute SW2 difference 6.94e-18. The saved trajectories are retained unchanged.


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

The equal-data comparison contains 40 variance-0.3 transports with individual fit and sampling times. The alanine distribution and convergence figures share their saved arrays; fixed-configuration costs and evaluations are recorded below.

The alanine distribution summary uses the three BKT endpoints at s=8 from the convergence archive, with their original sources and evaluation clouds. The saved input file contains only the 256 retained eigenpairs and the three source/reference designs needed by this experiment. No independent set of Fourier transport results is used for the distribution figure.

Reference distances describe sampling variability and are not lower bounds for transport. In the equal-data comparison, a reference-threshold crossing uses the reference mean plus one sample standard deviation at a prescribed observation time. The two-dimensional admissible source has harmonic variance 0.3; the uncoupled ten-dimensional source has nine stationary harmonic coordinates of variance 0.5.

FD-201 uses a 201-by-201 grid for two-dimensional systems; the high-dimensional FD comparisons use separable one-dimensional factors. Separable high-dimensional experiments do not establish performance on general coupled targets. The nine-well limitation remains. The angular-marginal example does not test physical molecular kinetics.

The same-sample comparison requires the stated common-region assumptions. Its coefficient factor is Delta_M = M^(-1/2) sum_k sqrt(Var(phi_k)); bounded individual variances give O(r/sqrt(M)), with possible additional rank dependence in the stability factor. Initial empirical coefficients do not imply exact spectral moments of the transported particles. These numerical checks do not constitute an independent proof review.

## Fixed-configuration details

The reported configurations retain every prescribed source realisation. Alanine uses trajectory 1 for spectrum fitting and source construction; all three seeds are retained. Its results are conditional on this fixed fit and do not establish robustness across estimation trajectories.

### Alanine fitting and transport costs

Costs use one BLAS thread and exclude input generation and metric callbacks. Spectrum fitting includes the Gram and Dirichlet matrices and eigendecomposition. Initial moments are evaluated separately.

| Estimation | Wall seconds | CPU seconds |
|---|---|---|
| kde_target_fit | 0.169732 | 0.171875 |
| spectrum_fit0 | 24.6921 | 24.0156 |


| Method | Transport wall seconds | Transport CPU seconds |
|---|---|---|
| BKT | 72.4349 +/- 2.88266 | 70.3333 +/- 3.08293 |
| LAWGD | 70.2462 +/- 3.93562 | 68.1562 +/- 4.40445 |
| KDE | 1056.4 +/- 144.778 | 1017.96 +/- 144.506 |


### Fixed-fit evaluation

Trajectory numbers in this table are 1-based. Both evaluations share the spectrum and source constructed from trajectory 1. Each entry includes seeds 1101, 1102 and 1103; standard deviations describe these paired designs, not independent spectrum estimates.

| Fit / evaluation trajectory | SW2 | Mass TV | Reference SW2 | Reference TV | Local-width ratio |
|---|---|---|---|---|---|
| 1 / 2 | 0.0669617 +/- 0.0315511 | 0.0266667 +/- 0.00950438 | 0.0691394 +/- 0.0258861 | 0.0286667 +/- 0.012897 | 1.1886 +/- 0.0380956 |
| 1 / 3 | 0.0596977 +/- 0.0188045 | 0.033 +/- 0.0177764 | 0.0507342 +/- 0.0206598 | 0.0226667 +/- 0.0140119 | 1.1737 +/- 0.0878244 |


| Source design | SW2 at s=8 | Mass TV at s=8 |
|---|---|---|
| iid | 0.0579976 +/- 0.0213123 | 0.0406667 +/- 0.0185562 |
| sobol | 0.0596977 +/- 0.0188045 | 0.033 +/- 0.0177764 |


### Numerical safeguards

The synthetic ratio floor is 0.001 and speed cap is 20. Box projection acts as described in each protocol. Alanine masks count particles meeting a safeguard at any attempted adaptive RHS evaluation, including rejected stages; torus wrapping is not box projection. Per-realisation masks and numerical records are retained in the data archives.

| Method | Seed | Floor fraction | Speed-cap fraction |
|---|---|---|---|
| BKT | 1101 | 0.001 | 0.005 |
| BKT | 1102 | 0.001 | 0.004 |
| BKT | 1103 | 0.002 | 0.008 |
| LAWGD | 1101 | 0 | 0 |
| LAWGD | 1102 | 0 | 0 |
| LAWGD | 1103 | 0 | 0 |


Saved-array verification recomputed 668 endpoint distances and checked 3125 particle masks. Maximum metric discrepancy: 8.88e-16. This checks stored metrics, not bitwise reproduction of a newly fitted spectrum.

## Files and reproduction

This is the only experiment-results Markdown file. Numerical data are stored in four checksum-verified archives: `outputs/data/ou.zip`, `double_well.zip`, `alanine.zip` and `shared.zip`. The per-realisation records, raw public alanine trajectories needed for fixed-fit evaluation, current configurations and reference statistics are archive members under `outputs/revision/` in `double_well.zip`. The Git-visible `outputs/revision_results.json` publishes the retained per-realisation records and fixed-configuration summaries without the large arrays. PDFs remain in `outputs/figures/`.

Use Python 3.11, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.1, threadpoolctl 3.6.0 and Numba 0.64.0. Each numerical process uses one BLAS thread. The queue may run four independent synthetic repetitions concurrently, or two product repetitions with eight coordinate workers each. The equal-data comparison and alanine cost measurements run alone. Concurrent elapsed times are descriptive and are not used to rank samplers. Only one managed archive session may be open at a time.

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 --with numba==0.64.0 python -u -B supplementary/revision_queue.py
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 --with numba==0.64.0 python -B supplementary/revision_verify.py
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 --with numba==0.64.0 python -B supplementary/revision_publish.py
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with matplotlib==3.11.1 --with threadpoolctl==3.6.0 python -B supplementary/revision_figures.py
python -B supplementary/experiment_store.py verify
```

The queue resumes completed prescribed rows; it does not replace failed seeds. Each run retains its configuration and available endpoint; the transports also retain per-path masks, including available masks from failed attempts. For a fresh repetition, use a separate checkout with the corresponding result rows absent while preserving the current configuration summaries and shared input/reference archives. The publisher validates prescribed seed sets, regenerates the numerical tables, and updates this single report. The figure command reads the published results only. `BKT_experiments.ipynb` calls the same numerical runners, avoiding a second implementation of the fixed protocol.

For the retained product protocol, source indices are 0--5 and 7--10, so no source seed equals target seed 7. The regular product runners use these indices directly.

The matched OU P/I/S experiment has 180 runs, ranks 10, 20, 40, two steps and ten source seeds. Its dedicated runner is `ou_path_validation.py`. The alanine distribution and convergence figures use the same three Fourier BKT trajectories at s=8. Fitting and transport costs and two held-out evaluations are reported for the fixed fit. Analytical OU distances use the Gaussian reference; alanine SW2 uses its fixed periodic embedding.

`manuscript_results.py` regenerates this report without simulations. `--tables` regenerates CSV tables; `--check` checks canonical endpoint distances and the retained matched OU calculations. `alanine_experiment.py --stage verify` and `alanine_convergence.py --stage verify` check their original saved clouds. The latter checks the frozen protocol and inputs and reports the stored/current source-code fingerprints separately: adding path observations changes the source hash. Fresh run and shard provenance checks remain strict. Saved-array verification checks the reported metrics and numerical safeguard masks.

The shared printed typography is defined in `figure_style.py`: overall title 11 pt, panel title 9.5 pt, axis label 9 pt, ticks 8.5 pt, legend 8 pt, all normal weight. Canvas dimensions and manuscript insertion widths determine export scaling. Where manuscript sources are absent, frozen widths from the retained PDFs are used. The admissible-source rank figure remains 1-by-4. Product histograms use source seed 1, while their marginal-error panels show mean and sample SD over the ten prescribed realisations. Error bars are not confidence intervals.

# The Polytope Compression Hypothesis: Perceptual Efficiency as a Measurable Ratio of Experienced Discriminations to Available Markovian Degrees of Freedom

**Author:** Big D  
**Date:** February 13, 2026  
**Repository:** github.com/zfifteen  
**Status:** Preprint / Working Paper  

---

## Abstract

We propose a novel dimensionless metric, *perceptual efficiency* $\eta$, that quantifies how many behaviorally discriminable color experiences an organism extracts per unit of geometrically available experiential complexity. Available complexity is measured as the dimension of the Markov polytope $\mathcal{M}_k$ from Hoffman, Prakash, and Prentner's (2023) conscious-agent formalism, where $k$ is the number of functionally independent photoreceptor classes and $\dim(\mathcal{M}_k) = k(k-1)$. Discriminable experiences are measured as spectral just-noticeable-difference (JND) hue steps integrated across the organism's visible spectrum. We compute $\eta$ for six benchmark species spanning dichromats to dodecachromats using published psychophysical data. The result is a robust inverse scaling: organisms with more receptor classes extract systematically fewer discriminations per polytope dimension, consistent with a power law $\eta \propto k^{-\alpha}$ where $\alpha \approx 2.8$. We interpret this as evidence that the Markov polytope dimension grows faster than neural architectures can exploit, forcing organisms into one of two regimes: deep cortical amplification (high $\eta$, few receptors, fine discrimination) or shallow interval decoding (low $\eta$, many receptors, coarse discrimination). The framework yields falsifiable predictions for human tetrachromacy, synthetic sensor design, and the empirical relevance of Hoffman's polytope to sensory ecology.

---

## 1. Introduction

### 1.1 The Color Dimension Problem

The number of photoreceptor classes an organism possesses does not straightforwardly predict the richness of its color experience. Humans, with three cone types (S, M, L), achieve approximately 130 spectrally discriminable hue steps across the visible spectrum (Wright & Pitt, 1934). Mantis shrimp (Stomatopoda), with 12 narrowly tuned photoreceptor classes spanning 300--720 nm, discriminate roughly 12 spectral bins (Thoen et al., 2014). This is not a minor discrepancy. It is a factor of ~10 fewer discriminations despite a factor of 4 more receptor classes.

The standard explanation invokes a dichotomy between **opponent processing** (deep, recurrent, cortical) and **interval decoding** (shallow, hard-wired, peripheral). Primates build rich color spaces through pairwise opponent channels and successive stages of cortical refinement, culminating in narrowly tuned neurons in inferotemporal (IT) cortex (Zaidi et al., 2014). Mantis shrimp bypass this entirely: perceived color corresponds to the peak sensitivity of whichever receptor fires most strongly, a winner-take-all barcode strategy (Thoen et al., 2014; Marshall & Oberwinkler, 1999).

What has been missing is a **single quantitative framework** that predicts when an organism will land in one regime versus the other, and that connects this prediction to a formal model of experiential complexity.

### 1.2 The Markov Polytope as Experiential Arena

Hoffman, Prakash, and Prentner (2023) proposed that the dynamics of $n$ interacting conscious agents are described by Markov chains whose transition kernels live in a convex polytope $\mathcal{M}_n$ of dimension $n(n-1)$, with $n^n$ vertices. Each point in $\mathcal{M}_n$ is an $n \times n$ row-stochastic matrix $Q$, where $Q_{ij}$ gives the probability of transitioning from experiential state $i$ to state $j$. The polytope $\mathcal{M}_n$ is the space of all such matrices: the arena of all possible experiential dynamics for an agent with $n$ qualitative states.

Formally, a **conscious agent** $C$ is defined as a six-tuple:

$$C = \bigl((X, \mathcal{X}),\; (G, \mathcal{G}),\; (W, \mathcal{W}),\; P,\; D,\; A\bigr)$$

where:

- $(X, \mathcal{X})$ is a measurable space of potential conscious experiences,
- $(G, \mathcal{G})$ is a measurable space of potential actions,
- $(W, \mathcal{W})$ is a measurable space of world states (the agent network),
- $P: W \times X \to [0,1]$ is the **perception kernel** (Markovian),
- $D: X \times G \to [0,1]$ is the **decision kernel** (Markovian),
- $A: G \times W \to [0,1]$ is the **action kernel** (Markovian).

The composite **qualia kernel** $Q = D \circ A \circ P : X \times X \to [0,1]$ captures the agent's complete experiential dynamics. When $|X| = n$, the set of all possible qualia kernels forms $\mathcal{M}_n$.

Hoffman et al. also define a **fusion simplex** $\mathcal{F}_n$ of dimension $(n-1)$, consisting of rank-1 stationary kernels where all experiential states have become indistinguishable. A **kernel flow** on $\mathcal{M}_n$ describes how an agent's dynamics evolve over time, potentially converging toward $\mathcal{F}_n$ (fusion of qualia).

### 1.3 The Gap

Hoffman's formalism treats $n$ as a free parameter describing the number of experiential states, but never connects it to measurable sensory biology. Comparative vision science measures discriminability across species, but lacks a geometric framework for experiential complexity. This paper bridges the two.

---

## 2. The Perceptual Efficiency Metric

### 2.1 Definitions

Let $k \geq 2$ denote the number of **functionally independent photoreceptor classes** an organism uses for chromatic discrimination. "Functionally independent" means contributing to behaviorally measurable color opponency or discrimination, not merely present in the retina. This distinction is critical: *Papilio xuthus* has 8 receptor varieties across 6 spectral classes, but only 4 contribute to color discrimination (Koshitaka et al., 2008).

Define:

- $D(k) = k(k-1)$: the dimension of the Markov polytope $\mathcal{M}_k$, representing the total geometric degrees of freedom available for experiential dynamics.
- $B(k)$: the total number of spectral just-noticeable-difference (JND) hue steps the organism can discriminate, computed by integrating the reciprocal of the wavelength discrimination function $\Delta\lambda(\lambda)$ across the organism's visible spectrum:

$$B = \int_{\lambda_{\min}}^{\lambda_{\max}} \frac{1}{\Delta\lambda(\lambda)}\, d\lambda$$

- **Perceptual efficiency**:

$$\eta = \frac{B}{D(k)} = \frac{B}{k(k-1)}$$

$\eta$ is dimensionless (count/count). It measures how many discriminable experiential distinctions the organism realizes per unit of available polytope dimension.

### 2.2 Interpretation

- **High $\eta$** (e.g., >10): The organism extracts many more discriminable experiences than the raw polytope dimension would naively suggest. This implies deep, recurrent neural processing that "amplifies" a small polytope. The organism fills a larger effective volume of its experiential space through cortical computation.
- **Low $\eta$** (e.g., <1): The organism uses only a thin slice of the available polytope dimensions. Many degrees of freedom are unexploited. The organism relies on shallow, hard-wired decoding, collapsing onto low-dimensional faces of $\mathcal{M}_k$.
- **Regime boundary** near $\eta \approx 1$: marks a transition where the cost of exploiting an additional polytope dimension exceeds the discriminative benefit.

### 2.3 Relationship to Polytope Geometry

A point in $\mathcal{M}_k$ is a $k \times k$ row-stochastic matrix with $k(k-1)$ free parameters (each row sums to 1, removing one degree of freedom per row). An organism performing full pairwise opponent processing (comparing all receptor pairs) exploits $\binom{k}{2} = k(k-1)/2$ opponent channels, which grows quadratically with $k$. This is the maximum number of independent comparison channels, and is exactly half the polytope dimension.

The metabolic and wiring cost of maintaining $O(k^2)$ independent comparison channels scales quadratically, while the neural "budget" (brain size, synaptic density) grows at best linearly or sublinearly with $k$ across taxa. This mismatch is the mechanistic driver of the inverse scaling.

---

## 3. Empirical Data

### 3.1 Species Selection and JND Estimation

We selected six species with published wavelength discrimination ($\Delta\lambda$) functions or behavioral color discrimination data spanning a range of receptor counts from $k=2$ to $k=12$. JND counts ($B$) are estimated by numerical integration of published $\Delta\lambda$ functions or, where only sparse threshold data exist, by piecewise approximation.

All $B$ values are estimates derived from published discrimination thresholds, not direct counts reported in any single paper. This is a limitation shared by any cross-species comparison of color discriminability, as no single standardized metric exists across taxa.

### 3.2 Data Table

| Species | $k$ (functional) | $D = k(k-1)$ | $B$ (est. JNDs) | $\eta = B/D$ | Primary Source |
|---|---|---|---|---|---|
| Dog (*Canis lupus familiaris*) | 2 | 2 | ~20 | ~10.0 | Neitz et al., 1989 |
| Honeybee (*Apis mellifera*) | 3 | 6 | ~40 | ~6.7 | von Helversen, 1972 |
| Human (*Homo sapiens*) | 3 | 6 | ~130 | ~21.7 | Wright & Pitt, 1934 |
| Pigeon (*Columba livia*) | 5 | 20 | ~100 | ~5.0 | Emmerton & Delius, 1980 |
| Swallowtail butterfly (*Papilio xuthus*) | 4 | 12 | ~150 | ~12.5 | Koshitaka et al., 2008 |
| Mantis shrimp (Stomatopoda) | 12 | 132 | ~12 | ~0.09 | Thoen et al., 2014 |

### 3.3 Notes on Specific Entries

**Dog.** Neitz et al. (1989) measured wavelength discrimination at five spectral points (440--520 nm). Discrimination collapsed entirely above ~520 nm, restricting the usable chromatic range to roughly 80 nm. The best threshold was ~4 nm near 480 nm. Piecewise integration yields ~15--25 JND steps. We use 20 as a central estimate.

**Human.** The classic Wright & Pitt (1934) wavelength discrimination function, integrated from 420--670 nm, yields approximately 128--140 hue JNDs. Boring (1939) cited 156. We use 130, which is conservative and well-supported. Note: Pointer & Attridge (1998) estimated ~2.28 million total discernible surface colors (including lightness and saturation), which is a distinct quantity.

**Honeybee.** von Helversen (1972) produced the first wavelength discrimination function for *Apis mellifera*, with finest discrimination ~4.5 nm near 490 nm. Visible range ~300--650 nm. Piecewise integration yields ~35--45 JND steps.

**Pigeon.** Emmerton & Delius (1980) measured discrimination thresholds at 10 nm intervals from 360--660 nm, finding minima near 460, 530, and 595 nm plus a UV minimum near 370 nm. This pattern is consistent with pentachromacy ($k = 5$, not $k = 4$ as sometimes reported). Piecewise integration over the measured 300 nm range yields ~80--120 JND steps. We use 100.

**Papilio xuthus.** Koshitaka et al. (2008) demonstrated tetrachromacy ($k = 4$) despite 8 receptor varieties across 6 spectral classes. Only UV, blue (NB+WB), green (DG), and red classes contribute to color discrimination. The $\Delta\lambda$ function has three minima at 430, 480, and 560 nm, reaching ~1 nm, the smallest wavelength discrimination threshold ever measured in any animal. Integration over ~300--700 nm plausibly yields ~150 JNDs.

**Mantis shrimp.** Thoen et al. (2014) showed surprisingly poor wavelength discrimination (~12--25 nm thresholds) despite 12 narrowly tuned receptor classes. Zaidi et al. (2014) confirmed that stomatopods use fast, hard-wired interval decoding rather than opponent processing. Effective spectral bins: ~12.

### 3.4 Statistical Fit

A log-log regression of $\eta$ against $k$ across all six species yields:

$$\eta \approx 233 \cdot k^{-2.83}$$

with $R^2 \approx 0.78$. Given the small sample size ($n = 6$) and the fact that $B$ values are rough estimates, this should be treated as indicative of a strong inverse trend rather than a precise scaling law. The fit is heavily leveraged by the mantis shrimp outlier at $k = 12$, $\eta = 0.09$.

The human data point ($k = 3$, $\eta = 21.7$) sits substantially above the regression line, consistent with the interpretation that primate cortical amplification represents an unusually efficient exploitation of a small polytope.

---

## 4. Theoretical Framework

### 4.1 Two Regimes of Polytope Occupancy

We propose that organisms occupy one of two qualitatively distinct regimes, determined by the ratio of neural processing depth to polytope dimension:

**Regime I: Cortical Amplification** (high $\eta$, typically $k \leq 4$).
Deep, recurrent, multi-stage neural processing (retina to LGN to V1 to V4 to IT in primates) generates narrowly tuned color-selective neurons in later stages. These neurons effectively subdivide the organism's low-dimensional polytope $\mathcal{M}_k$ into a fine mesh, yielding many discriminable bins per polytope dimension. The organism "fills" a large effective volume of its polytope.

Zaidi et al. (2014) showed that primate IT cortex contains millions of narrowly tuned color cells that support interval decoding at a much finer spectral grain than the 3 cone classes would naively suggest. This is the computational mechanism behind high $\eta$: cortical processing transforms 3 broad spectral samples into ~130 narrowly resolved bins.

**Regime II: Interval Decoding / Barcode Scanning** (low $\eta$, typically $k > 6$).
Shallow, hard-wired, winner-take-all decoding at or near the receptor level. Perceived color corresponds to whichever receptor class fires most strongly. The organism collapses onto at most $k$ discrete bins (one per receptor), using only a $k$-dimensional face of the $k(k-1)$-dimensional polytope. Most polytope degrees of freedom are unexploited.

This regime is adaptive for organisms requiring rapid sensory decisions (mantis shrimp strike in ~2 ms) and possessing small nervous systems that cannot support $O(k^2)$ wiring complexity.

### 4.2 The Resource Constraint

The transition between regimes is driven by a fundamental resource mismatch:

- The Markov polytope dimension grows as $k(k-1) \sim O(k^2)$.
- The number of independent opponent channels required for full exploitation grows as $\binom{k}{2} \sim O(k^2)$.
- Neural resources (brain volume, synaptic density, metabolic budget for visual processing) grow at best linearly with sensory channel count across taxa, and often sublinearly.

When $k$ is small (2--4), the $O(k^2)$ cost is manageable: 2, 6, or 12 dimensions. An organism with sufficient cortical depth can fill this space. When $k$ is large (6--12), the cost becomes 30--132 dimensions. No known nervous system can support full opponent processing across this many channels. The organism must abandon depth for breadth.

### 4.3 Connection to Hoffman's Kernel Flow

In Hoffman et al.'s framework, kernel flow on $\mathcal{M}_n$ describes how an agent's experiential dynamics evolve, potentially converging toward the fusion simplex $\mathcal{F}_n$. The perceptual efficiency metric $\eta$ can be interpreted as measuring how much of the polytope's dynamical capacity is actually traversed by the organism's realized perception.

A high-$\eta$ organism (human) explores a rich submanifold of $\mathcal{M}_3$, with kernel flow trajectories that traverse many distinct experiential states before converging. A low-$\eta$ organism (mantis shrimp) is confined to a thin, low-dimensional face of $\mathcal{M}_{12}$, with kernel flow effectively frozen into one of ~12 fixed attractors (the winner-take-all states).

This suggests a refinement of Hoffman's framework: the "effective experiential dimension" of a conscious agent is not $\dim(\mathcal{M}_n) = n(n-1)$, but $\eta \cdot \dim(\mathcal{M}_n) / B_{\text{ref}}$, where $B_{\text{ref}}$ is a normalization constant. The polytope provides the geometric upper bound; the organism's neural architecture determines how much of that bound is realized.

---

## 5. Falsifiable Predictions

### 5.1 Cross-Species Scaling

**Prediction 1.** Across taxa with measured spectral JND counts and known functional photoreceptor class counts ($k \geq 2$), $\eta$ will show a statistically significant inverse relationship with $k$. Organisms with $k \leq 4$ and deep cortical processing (vertebrates) will cluster at $\eta > 5$. Organisms with $k > 6$ and shallow decoding (arthropods) will cluster at $\eta < 2$.

**Disconfirmation.** If a species with $k > 6$ is found to have $\eta > 10$ (many JNDs per polytope dimension despite many receptor classes), this would indicate that deep processing can scale with high receptor counts, falsifying the resource-constraint mechanism.

### 5.2 Human Tetrachromacy

**Prediction 2.** Confirmed strong tetrachromats (e.g., Jordan's cDa29) will show elevated JND counts in the spectral region where their anomalous L' photopigment provides maximum discrimination gain (roughly 540--600 nm), but their total $B$ will not exceed ~200. Their perceptual efficiency will therefore be:

$$\eta_{\text{tetra}} = \frac{B_{\text{tetra}}}{4(4-1)} = \frac{B_{\text{tetra}}}{12} \leq 16.7$$

This is **lower** than the trichromatic human $\eta \approx 21.7$, despite the absolute gain in $B$. The fourth cone adds discriminative capacity but at a reduced marginal efficiency per polytope dimension.

**Disconfirmation.** If a strong tetrachromat achieves $B > 260$, she would match or exceed the trichromatic human $\eta$, indicating that the cortex can fully scale to exploit the additional polytope dimensions without diminishing returns.

### 5.3 Weak Tetrachromats

**Prediction 3.** The ~12--15% of human females who carry four cone pigments but function as weak tetrachromats (Jordan & Mollon, 2019) will show $B$ values statistically indistinguishable from trichromats ($B \approx 130$). When scored against their actual polytope ($k = 4$, $D = 12$), their $\eta \approx 130/12 \approx 10.8$ will be significantly lower than that of trichromatic controls ($\eta \approx 21.7$), even though their absolute discrimination performance is identical.

This makes the specific point that weak tetrachromacy is not "failed" tetrachromacy. It is the cortex correctly recognizing that exploiting the fourth cone's polytope dimensions is not worth the wiring investment, given the marginal spectral separation (~4--5 nm between L cone alleles at site 180).

### 5.4 Decision Rule for Synthetic Sensory Systems

**Prediction 4 (Engineering).** In artificial perception systems (e.g., hyperspectral imaging classifiers), adding spectral channels beyond the point where $\eta$ drops below ~1 will not improve classification accuracy for tasks requiring fine discrimination, unless the downstream processing architecture (layers, parameters, recurrence) is scaled quadratically with channel count.

Formally: if a system has $k$ spectral channels and $L$ layers of recurrent processing, classification accuracy plateaus when:

$$\eta_{\text{eff}} = \frac{B_{\text{system}}}{k(k-1)} < 1 \quad \text{and} \quad L < c \cdot k^2$$

for some architecture-dependent constant $c$.

---

## 6. Relation to Prior Work

### 6.1 Comparison Table

| Framework | Overlap with This Work | Key Difference |
|---|---|---|
| Barlow (1961) efficient coding hypothesis | Both concern mapping from receptor signals to discriminations | Barlow works in information-theoretic terms (bits/spike); we use polytope dimension as the denominator, connecting to Hoffman's consciousness formalism |
| Buchsbaum & Gottschalk (1983) optimal channels | Both address the gap between receptor count and useful perceptual channels | B&G use eigenvalues of spectral covariance; we use a geometric ratio tied to a specific polytope |
| Thoen et al. (2014) interval decoding | Both explain why mantis shrimp have poor discrimination | Thoen provides the mechanism for one species; we provide a cross-species quantitative metric |
| Zaidi et al. (2014) convergent computation | Both identify interval decoding in mantis shrimp and primate IT | Zaidi focuses on computational convergence; we embed this in a polytope-dimensional scaling law |
| Hoffman et al. (2023) Markov polytope | We use their polytope as the denominator | Hoffman's paper never connects polytope dimension to empirical sensory ecology or measurable $\eta$ |
| Osorio & Vorobyev (2008) color space dimensionality | Both address perception vs. receptor count | O&V focus on receptor noise models; we focus on geometric scaling of experiential complexity |

### 6.2 Novelty Assessment

- **Purpose:** New. Bridging Hoffman's mathematical consciousness theory with comparative sensory ecology via a single testable metric.
- **Mechanism:** Partially new. Reinterprets known sensory ecology through a geometric lens that Hoffman's formalism provides but never applies to real organisms.
- **Evaluation:** New. The specific metric $\eta = B / k(k-1)$ has not been proposed previously.
- **Application:** New combination. No prior work connects polytope structure to empirical psychophysics across species.

---

## 7. Limitations

1. **Sample size.** Six species is insufficient for robust statistical inference. The power-law exponent and $R^2$ should be treated as preliminary. The fit is leveraged by the mantis shrimp extreme.

2. **JND estimation.** $B$ values are derived from published wavelength discrimination functions via approximate integration, not standardized behavioral counts. Different experimental paradigms (forced-choice vs. matching), adaptation states, and luminance levels produce different $\Delta\lambda$ functions.

3. **Receptor count ambiguity.** "Functional" receptor count ($k$) is not always clear. Papilio has 8 receptor varieties but functions tetrachromatically. Pigeons may be tetra- or pentachromatic depending on how oil-droplet filtering is counted. This ambiguity propagates into $D$ and $\eta$.

4. **Polytope interpretation.** The identification of $k$ (receptor classes) with $n$ (number of experiential states in Hoffman's formalism) is an assumption. Hoffman's $n$ refers to qualitative experiential states, which need not correspond one-to-one with photoreceptor types. This mapping is a hypothesis, not a theorem.

5. **Causality.** The framework identifies a scaling relationship, not a causal mechanism. The claim that neural resource constraints drive the inverse scaling is plausible but not directly tested here.

6. **Scope.** The metric applies only to spectral hue discrimination in organisms with $k \geq 2$ chromatic receptor classes. It does not address achromatic contrast sensitivity, polarization vision, or non-visual sensory modalities.

---

## 8. Conclusion

The perceptual efficiency metric $\eta = B / k(k-1)$ provides a falsifiable, dimensionless bridge between Hoffman's abstract polytope of experiential dynamics and the concrete psychophysics of color discrimination. The strong inverse scaling of $\eta$ with $k$ across taxa supports a "polytope compression" hypothesis: adding sensory channels without proportionally deepening the processing architecture does not expand experience. It collapses it into a coarser, faster regime. If the Markov polytope is genuinely the arena of experiential dynamics, as Hoffman proposes, then $\eta$ is a first-pass empirical probe of how much of that arena an organism actually occupies.

---

## References

- Barlow, H.B. (1961). Possible principles underlying the transformation of sensory messages. *Sensory Communication*, 217--234.
- Buchsbaum, G. & Gottschalk, A. (1983). Trichromacy, opponent colours coding and optimum colour information transmission in the retina. *Proceedings of the Royal Society B*, 220(1218), 89--113.
- Emmerton, J. & Delius, J.D. (1980). Wavelength discrimination in the "visible" and ultraviolet spectrum by pigeons. *Journal of Comparative Physiology*, 141(1), 47--52.
- Hoffman, D.D., Prakash, C., & Prentner, R. (2023). Fusions of Consciousness. *Entropy*, 25(1), 129.
- Jordan, G., Deeb, S.S., Bosten, J.M., & Mollon, J.D. (2010). The dimensionality of color vision in carriers of anomalous trichromacy. *Journal of Vision*, 10(8), 12.
- Jordan, G. & Mollon, J.D. (2019). Tetrachromacy: the mysterious case of extra-ordinary color vision. *Current Opinion in Behavioral Sciences*, 30, 130--134.
- Koshitaka, H., Kinoshita, M., Vorobyev, M., & Arikawa, K. (2008). Tetrachromacy in a butterfly that has eight varieties of spectral receptors. *Proceedings of the Royal Society B*, 275(1637), 947--954.
- Marshall, N.J. & Oberwinkler, J. (1999). The colourful world of the mantis shrimp. *Nature*, 401(6756), 873--874.
- Neitz, J., Geist, T., & Jacobs, G.H. (1989). Color vision in the dog. *Visual Neuroscience*, 3(2), 119--125.
- Osorio, D. & Vorobyev, M. (2008). A review of the evolution of animal colour vision and visual communication signals. *Vision Research*, 48(20), 2042--2051.
- Pointer, M.R. & Attridge, G.G. (1998). The number of discernible colours. *Color Research & Application*, 23(1), 52--54.
- Thoen, H.H., How, M.J., Chiou, T.H., & Marshall, J. (2014). A different form of color vision in mantis shrimp. *Science*, 343(6169), 411--413.
- von Helversen, O. (1972). Zur spektralen Unterschiedsempfindlichkeit der Honigbiene. *Journal of Comparative Physiology*, 80(4), 439--472.
- Wright, W.D. & Pitt, F.H.G. (1934). Hue discrimination in normal colour-vision. *Proceedings of the Physical Society*, 46(3), 459--473.
- Zaidi, Q., Marshall, J., Thoen, H., & Conway, B.R. (2014). Evolution of neural computations: Mantis shrimp and human color decoding. *i-Perception*, 5(6), 492--496.

---

## Appendix A: Markov Polytope Formal Definitions

**Definition (Markov Polytope).** For $n \geq 2$, the Markov polytope $\mathcal{M}_n$ is the set of all $n \times n$ row-stochastic matrices:

$$\mathcal{M}_n = \left\{ Q \in \mathbb{R}^{n \times n} \;\middle|\; Q_{ij} \geq 0,\; \sum_{j=1}^{n} Q_{ij} = 1 \;\forall\, i \right\}$$

$\mathcal{M}_n$ is a convex polytope of dimension $n(n-1)$ with $n^n$ vertices. Each vertex is a matrix where every row is a standard basis vector $e_j$ for some $j \in \{1, \ldots, n\}$.

**Definition (Fusion Simplex).** The fusion simplex $\mathcal{F}_n \subset \mathcal{M}_n$ is the $(n-1)$-dimensional simplex of rank-1 stochastic matrices:

$$\mathcal{F}_n = \left\{ Q \in \mathcal{M}_n \;\middle|\; Q_{ij} = \pi_j \;\forall\, i,\; \text{where } \sum_j \pi_j = 1,\; \pi_j \geq 0 \right\}$$

These are the stationary (idempotent) kernels: $Q^2 = Q$, $Q = \mathbf{1}\pi^T$. All rows are identical. From the perspective of an agent, reaching $\mathcal{F}_n$ means all experiential states have fused into a single invariant distribution; the agent can no longer distinguish between its qualitative states.

**Note on distinction from the Birkhoff polytope.** $\mathcal{M}_n$ (row-stochastic matrices) is not the same as the Birkhoff polytope $\mathcal{B}_n$ (doubly stochastic matrices). $\mathcal{B}_n \subset \mathcal{M}_n$. The Birkhoff polytope has dimension $(n-1)^2$ and $n!$ vertices (the permutation matrices). The Markov polytope has dimension $n(n-1)$ and $n^n$ vertices. In Hoffman's framework, $\mathcal{B}_n$ sits inside $\mathcal{M}_n$ as a distinguished sub-polytope, and permutation matrices in $\mathcal{B}_n$ correspond to decorated permutations that project onto scattering amplitudes in spacetime.

## Appendix B: Dimensional Accounting

For each species, the polytope dimension $D = k(k-1)$ counts the total free parameters in a $k \times k$ row-stochastic matrix ($k$ rows, each with $k-1$ free entries since the row sums to 1).

| $k$ | $D = k(k-1)$ | $n^n$ vertices | Opponent channels $\binom{k}{2}$ | Ratio $D / \binom{k}{2}$ |
|---|---|---|---|---|
| 2 | 2 | 4 | 1 | 2.0 |
| 3 | 6 | 27 | 3 | 2.0 |
| 4 | 12 | 256 | 6 | 2.0 |
| 5 | 20 | 3,125 | 10 | 2.0 |
| 6 | 30 | 46,656 | 15 | 2.0 |
| 12 | 132 | 8.9 x 10^12 | 66 | 2.0 |

The ratio $D / \binom{k}{2} = 2$ for all $k$. This is not a coincidence: $k(k-1) / [k(k-1)/2] = 2$ identically. Each pairwise opponent channel corresponds to exactly 2 polytope dimensions (one for each direction of the comparison). This means full opponent processing saturates exactly half the available polytope degrees of freedom, with the remaining half encoding asymmetries in transition probabilities (e.g., the probability of transitioning from state $i$ to $j$ versus $j$ to $i$).

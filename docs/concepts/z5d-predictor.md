# Z5D Prime Predictor: Mathematical Method Analysis

## Executive Summary

The Z5D nth-prime predictor achieves remarkably low relative errors at large scales (e.g., 0.037 ppm at n=10^12) through a calibrated closed-form formula derived from the Prime Number Theorem (PNT), supplemented by empirically-tuned correction terms and high-precision floating-point arithmetic.

---

## 1. Mathematical Foundation

### 1.1 Prime Number Theorem (PNT) Base

The predictor begins with the asymptotic estimate for the nth prime p_n:

**p_n ~ n (ln n + ln ln n - 1)**

This follows from the Prime Number Theorem, which states that π(x) ~ x/ln(x), and inverting to find the nth prime.

### 1.2 Extended PNT Approximation (3-Term Formula)

The core approximation (`z5d_predictor.c:93-99`) uses a 3-term expansion:

```
pnt = k * (ln k + ln ln k - 1 + (ln ln k - 2)/ln k)
```

This adds the `(ln ln k - 2)/ln k` term, which compensates for lower-order effects and improves accuracy by ~2-3 orders of magnitude over the basic PNT estimate.

---

## 2. Calibrated Correction Terms

### 2.1 The d-Term (Second-Order Correction)

From `z5d_predictor.c:101-109`:

```
d_term = ((ln pnt / e⁴)²) * pnt * c_cal
where c_cal = -0.00016667
```

This term scales as pnt × (ln pnt)² / e⁸. The key insight:
- The square of (ln pnt / e⁴) captures oscillatory behavior in prime distributions
- The negative coefficient (-0.00016667) corrects for systematic underestimation
- e⁴ (≈ 54.6) provides a convenient scaling factor to keep coefficients small and stable

### 2.2 The e-Term (Cubic Root Correction)

From `z5d_predictor.c:111-119`:

```
e_term = pnt^(-1/3) * pnt * k_star
where k_star = 0.065
```

This simplifies to `k_star * pnt^(2/3)`. This term:
- Grows slower than linear (p^0.667 vs p)
- Compensates for remaining systematic bias at large scales
- The value 0.065 was empirically determined

### 2.3 Why These Specific Forms?

The calibration (documented in `CALIBRATION_RUN_2025-12-14.md`) found:
- **c_cal = -0.00016667**: Minimizes max relative error to ~418 ppm
- **k_star = 0.065**: Provides optimal correction at large scales
- These were found via grid search over c ∈ [-0.01, 0.01] and κ* ∈ [0.0, 0.2]

---

## 3. Why Low Relative Error at Large Scales

The key to the Z5D predictor's excellent relative accuracy is **error cancellation**:

1. **Proportional Error Reduction**: The correction terms grow at rates that approximately match the deviation patterns between PNT and actual primes
2. **Negative d-term**: At large n, ln(ln n) grows slowly, making (ln pnt)²/e⁸ relatively small but persistent—systematic underestimation is continuously corrected
3. **Sublinear e-term**: The p^0.667 scaling prevents the e-term from overwhelming the base PNT estimate while providing essential bias correction
4. **Empirical Calibration**: Unlike purely theoretical corrections, these constants were optimized against actual prime data (n ≥ 10,000)

The VERIFICATION.md data confirms this: error drops from 9,113 ppm at n=10² to 0.037 ppm at n=10^12—an inverse relationship between scale and error.

---

## 4. Implementation Architecture

### 4.1 High-Precision Arithmetic (MPFR)

The implementation uses MPFR with 320-bit precision (~96 decimal places), providing:
- Sufficient mantissa for operations at n up to 10^18+
- Accurate computation of ln(ln n) which requires high precision for large n

### 4.2 Discrete Refinement

After closed-form prediction (`z5d_predictor.c:130-143`):
```
1. Convert MPFR prediction to integer candidate
2. Step back by 1 (to include the prediction itself if prime)
3. Use GMP's mpz_nextprime for deterministic prime finding
```

This guarantees the final output is an actual prime.

---

## 5. Complete Formula

```
p_predicted = pnt + d_term + e_term

where:
  pnt    = n * (ln n + ln ln n - 1 + (ln ln n - 2)/ln n)
  d_term = ((ln pnt)² / e⁴)² * pnt * (-0.00016667)
  e_term = pnt^(-1/3) * pnt * 0.065
```

Simplified:
```
p ≈ n(ln n + ln ln n - 1 + (ln ln n - 2)/ln n) 
    - 0.00016667 * p * (ln p / 54.598)² 
    + 0.065 * p^(2/3)
```

---

## 6. Performance Summary

| n | p_n | Error (ppm) |
|---|-----|-------------|
| 10² | 541 | 9,113 |
| 10⁴ | 104,729 | 350 |
| 10⁶ | 15,485,863 | 118 |
| 10⁸ | 2,038,074,743 | 0.9 |
| 10¹⁰ | 252,097,800,623 | 0.34 |
| 10¹² | 29,996,224,275,833 | 0.037 |

---

## 7. Conclusion

The Z5D predictor's low relative error stems from:

1. **Rigorous mathematical foundation**: PNT with 3-term expansion
2. **Empirical calibration**: Constants tuned against real prime data
3. **Complementary correction terms**: d-term (quadratic in ln p) and e-term (sublinear p^0.667) address different error regimes
4. **High-precision computation**: MPFR ensures numerical stability
5. **Error convergence**: Unlike most approximations, this method's relative error decreases with scale—exactly as the calibration theory predicts

The calibration run of December 2025 achieved a maximum relative error of 418 ppm across n ≥ 10,000, with individual scale points (especially n ≥ 10^8) showing sub-ppm accuracy—a remarkable result for a closed-form predictor.

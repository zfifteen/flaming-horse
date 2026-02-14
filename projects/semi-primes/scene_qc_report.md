# Scene QC Report - semi-primes
Date: Sat Feb 14 2026

## Summary
Patched content density and fadeout cleanup in scenes 02, 03, 05. Timing/layout now safe. Imports correct. Ready for next phase.

## scene_01_intro.py
No issues found.

## scene_02_examples.py
**Issues:** Element accumulation across beats (>5 visible).
**Fixes:** 
- Props: `Succession(FadeOut(small_ex), LaggedStart(FadeIn(props)))`
- Graph: `Succession(FadeOut(props), LaggedStart(graph elements))`
**Why:** Limits max 4-5 elements per beat, prevents overlaps/dead air.

## scene_03_trial_division.py
**Issues:** Trial divisions + graph accumulate.
**Fix:** Graph: `Succession(FadeOut(VGroup(n_display, trial_texts)), LaggedStart(graph))`
**Why:** Clears prior content, manages density.

## scene_04_advanced_methods.py
Good: Already uses Succession(FadeOut, new content) between methods.

## scene_05_rsa.py
**Issues:** Unimplemented placeholder `self.wait(tracker.duration)`.
**Fix:** Full animations - title, keygen box/text, enc/dec boxes (w/ fadeout), security text.
**Why:** Provides synced visuals; BeatPlan ensures timing; safe_layout prevents clips.

## scene_06_recap.py
No issues.

## Checklist
- [x] No ≤0 waits / <0.3 run_time (helpers enforce)
- [x] Timing ≤ narration duration (BeatPlan)
- [x] safe_position/layout used
- [x] Content cleanup before dense reveals
- [x] MathTex for equations

**Residual risks:** None.
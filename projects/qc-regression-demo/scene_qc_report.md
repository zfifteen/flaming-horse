# Scene QC Report for QC Regression Demo

Generated: 2026-02-15

## Summary
All 5 scenes pass QC validation:
- Positioning: safe_position/safe_layout used, no .to_edge, title UP*3.8
- Timing: BeatPlan + play_next, budgets <=1.0, buffer wait
- Content: MathTex for equations, labels, no >5 elements per beat
- Aesthetics: palettes, smooth rate_func, no static >3s
- Voice: Qwen cache check, SCRIPT keys

Patches applied:
- scene_04_results.py: LaggedStart unpack generator
- scene_05_conclusion.py: Text newline fix (\\n -> \n)

No needs_human_review.

## Per Scene Validation

### scene_01_intro (intro)
- Layout: pipeline diagram safe_layout(boxes)
- Timing: 3 beats [2,3,2]
- ✓ Pass

### scene_02_data (data_overview)
- Layout: data_points, bar_group safe_layout
- Timing: 4 beats, LaggedStart FadeIn/GrowFromCenter
- ✓ Pass

### scene_03_regression (regression_analysis)
- Layout: points, line/equation/preds/residuals safe_position
- MathTex used
- Timing: 4 beats, LaggedStart Create/FadeIn
- ✓ Pass

### scene_04_results (results)
- Layout: Arc gauges, VGroup comp_table safe_layout
- Timing: 4 beats, animate.set_angle, LaggedStart fixed
- ✓ Pass (patched)

### scene_05_conclusion (conclusion)
- Layout: bullets, final_graphic safe_layout
- Timing: 3 beats, LaggedStart FadeIn, animate scale/rotate
- ✓ Pass (patched Text)
"""
Narration script for: covid_vaccine_aliasing
Generated: 2026-02-11
Duration: ~5 minutes
"""

SCRIPT = {
    "intro": """Imagine two radio stations broadcasting on the exact same frequency. You can't tell them apart, right? That's the core problem with the COVID-19 vaccine mortality debate. It's structurally unresolvable from existing data because the healthy-vaccinee selection advantage fades with a half-life of two to three months, while pandemic waves recur every three to six months. These two effects overlap perfectly, making them indistinguishable in any time-series analysis.""",
    "core_issue": """This isn't just about having confounders in observational studies. It's a more specific and damaging issue: the primary confounding bias—the healthy vaccinee effect—decays over roughly two to three months. Meanwhile, pandemic waves hit every three to six months. When these timescales overlap, no statistical method can separate one from the other, no matter how big your sample size.""",
    "why_stats_fail": """Think about it—no self-controlled case series, no Cox regression, no propensity matching can tease apart these effects. The temporal structure is aliased, like those radio stations. Every country's data ends up looking almost, but not quite, like it shows a signal.""",
    "ambiguous_data": """The residual after removing known biases always hovers in an ambiguous zone. Too large to dismiss as noise, but too entangled with that bias decay to confirm as real. This explains why the debate persists— the data is permanently stuck in limbo.""",
    "solution": """The non-obvious implication is that more data from the same pandemic won't help. The answer is to find rare natural experiments where the aliasing breaks—prolonged inter-wave quiet periods of six months or longer. In those windows, the healthy-vaccinee advantage has fully decayed, but no new wave has begun. Only then do mortality comparisons carry genuine discriminating power.""",
    "predictions": """This predicts that researchers isolating such quiescent windows, like Australia's October 2021 to January 2022 gap, will see mortality ratios converging toward 1.0 if the signal is entirely artifactual, or persisting above 1.0 if something real remains. No study has done this specific temporal isolation yet. For future pandemics, the vaccine deployment schedule determines if safety can ever be assessed. If boosters coincide with seasonal waves—as public health typically recommends—the data will be permanently aliased, repeating the same unresolvable debate.""",
    "conclusion": """In summary, temporal aliasing locks the COVID-19 vaccine mortality debate. Unless we use these rare quiet periods to break the overlap, the question may remain forever unanswered.""",
}

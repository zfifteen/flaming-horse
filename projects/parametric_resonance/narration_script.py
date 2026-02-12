"""
Narration script for: Parametric Resonance in Plasma-Seeded Hypersonic Flow
Generated: 2026-02-11
Duration: ~240 seconds
"""

SCRIPT = {
    "threshold": "In plasma-seeded hypersonic flow under applied magnetic fields, acoustic momentum transfer becomes effective not when acoustic power is simply maximized, but when acoustic pressure (normalized by freestream dynamic pressure) multiplied by the ratio of modulation frequency to ion cyclotron frequency crosses a threshold near 0.05-0.1.",
    "resonance": "This threshold marks the onset of parametric resonance where the acoustic modulation, acting at a subharmonic of the ion cyclotron frequency, drives coherent ionic oscillations that couple momentum to the neutral flow with 10-50× amplification over non-resonant forcing.",
    "efficiency": "The non-obvious element is that weak acoustic pressure (5% of dynamic pressure) at the right frequency produces stronger flow control than strong acoustic pressure (50% of dynamic pressure) at wrong frequency.",
    "tradeoff": "This implies a designer faces a binary optimization: either hit the parametric resonance condition precisely (through careful tuning of both magnetic field strength and acoustic modulator characteristics), or accept an order-of-magnitude penalty in control authority.",
    "traditional": 'The traditional aerospace approach of "more power equals more control" fails in this regime because the coupling mechanism is fundamentally non-monotonic in frequency space.',
    "downconversion": "The parametric nature means that even modest laboratory-scale magnetic fields (0.1-0.5 Tesla) combined with kilohertz acoustic modulators can access megahertz ion physics without needing RF generators, effectively downconverting the frequency requirement through parametric excitation.",
    "window": 'When the combined parameter exceeds ~0.1, the system transitions into an over-coupled regime where plasma instabilities emerge, suggesting an operational window rather than a "more is better" paradigm.',
    "peaks": "This predicts experimentally observable peaks in momentum transfer efficiency at f_mod/f_ci ratios of exactly 1/2, 1/3, 1/4 (parametric subharmonics), distinguishing this mechanism from broadband resonance or simple impedance matching.",
}

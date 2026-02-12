"""
Narration script for: Climate Models' Hidden Weakness: The Viscosity That Reveals Missing Physics
Generated: 2026-02-11
Duration: ~6 minutes
"""

SCRIPT = {
    "reynolds_overview": """
    The Reynolds number isn't just a dimensionless parameter in fluid dynamics textbooks.
    It governs everything from why bacteria can swim through water to how hurricanes form and dissipate.
    Spanning 18 orders of magnitude, from microscopic flows to planetary circulation, the Reynolds number reveals the transition from smooth, predictable laminar flow to chaotic, turbulent cascades.
    But here's the problem: climate models, which simulate Earth's atmosphere and oceans, struggle with this fundamental parameter in ways that expose critical weaknesses.
    Today, we'll explore how artificial viscosity in these models isn't just a numerical fix—it's a diagnostic tool revealing the spatial scales of physics they've left out.
    Let's start with the foundations.
    """,
    "predictability_weakness": """
    At low Reynolds numbers, flows are reversible and predictable— you can run time backward and get the same result.
    At high Reynolds numbers, Kolmogorov's energy cascade creates exponential error growth, limiting weather forecasts to about two weeks.
    But the intermediate regime, where intermittency reigns, might have an even sharper predictability cliff.
    Discrete phase-space jumps from intermittent bursts mean climate models can't reliably capture the full range of fluid behavior.
    This non-uniform degradation exposes a core weakness: models tuned for high-Re turbulence may miss the subtle transitional dynamics that drive real-world climate variability.
    """,
    "viscosity_weakness": """
    Here's the paradox that breaks climate modeling wide open.
    Ocean and atmosphere models require eddy viscosity amplified by factors of 10^4 to 10^9 times the actual molecular viscosity.
    This is presented as "parameterizing unresolved turbulence," but it masks a deeper issue.
    When viscosity amplification reaches 10 billion, as in many ocean models, the implied dissipation scale exceeds the grid resolution by orders of magnitude.
    The model is no longer representing local turbulent eddies—it's artificially damping energy at scales it can't even resolve.
    This exposes a weakness: the model lacks the spatially coherent forcing mechanisms that should naturally organize flow at those large scales.
    """,
    "ghost_scale_weakness": """
    Let's derive the ghost scale—the spatial reach of missing physics.
    The implied dissipation scale L_implied equals the grid spacing L_grid times the square root of the viscosity amplification factor A.
    For ocean models with L_grid around 10 kilometers and A at 10^10, L_implied hits 10,000 kilometers—continental scale.
    When this ghost scale exceeds the domain size, the model admits it can't represent processes organizing flow at planetary distances.
    It's artificially suppressing what it doesn't understand, rather than simulating what it does.
    This weakness diagnostic reveals gaps in physics coverage, from ionospheric coupling to solar wind modulation, that standard models ignore.
    """,
    "weakness_implications": """
    This transforms climate modeling from guesswork to evidence-based science.
    By comparing viscosity amplification in standard models versus those with extended physics—like geomagnetic field effects or cosmic ray cloud seeding—we can quantify missing mechanisms.
    If adding ionospheric currents allows stable integration with 100-fold less viscosity, the ghost scale shrinks to match the mechanism's natural scale.
    This falsifiable approach exposes weaknesses in current models and guides reforms.
    Artificial viscosity becomes a precision diagnostic, turning numerical necessity into a roadmap for better climate science.
    Models with ghost scales over 10% of domain size simply don't understand what they're simulating.
    """,
}

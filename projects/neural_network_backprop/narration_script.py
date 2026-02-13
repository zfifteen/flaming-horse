"""
Narration script for: How Neural Networks Learn Through Backpropagation
Generated: 2026-02-13
Duration: ~180 seconds (3 minutes)
"""

SCRIPT = {
    "intro": """How does a computer learn to recognize a cat in a photo when no one ever programmed the rules? No one told it "look for pointed ears" or "check for whiskers." Yet somehow, from thousands of examples, the computer figures it out. The answer lies in an algorithm called backpropagation - and it's the key to everything modern AI can do.

But before we understand how it learns, we need to understand what it's learning with.""",
    "basics": """A neural network is made of layers of connected nodes. Think of each node as a tiny decision maker, and each connection as a pathway between them. Every connection has a number called a "weight" - and this weight determines how much influence that connection has.

Some weights are strong, passing signals through loudly. Others are weak, barely whispering. At the start, these weights are random. The network knows nothing. But here's the magic: by adjusting these weights, the network can learn to make better predictions. Learning isn't programming rules - it's tuning numbers.""",
    "forward_pass": """Let's watch a single prediction happen. Data enters as input - maybe pixel values from that cat photo. It flows into the first layer of nodes. Each node adds up everything coming in, multiplies by the connection weights, and passes the result forward.

The signal travels layer by layer. Each step, weights amplify or reduce the information. By the time it reaches the final layer, all these calculations combine into a prediction. The network declares: "Ninety percent sure this is a cat." But what if it's wrong? That's where the real learning begins.""",
    "backprop": """The network compares its prediction to the correct answer. If it said "cat" but the image was actually a dog, we calculate the error - just how wrong it was. Then we work backwards through the network, asking each connection: "How much did you contribute to this mistake?"

Connections that led us astray get their weights reduced. Connections that helped move us toward the right answer get strengthened. This is backpropagation - short for backward propagation of error. The error flows backward through the network, and each weight gets adjusted proportionally to its contribution.

Do this with thousands of examples, and the weights gradually settle into configurations that recognize cats, dogs, faces, speech, and more. The network never learns explicit rules. It discovers patterns through pure trial and error, guided by feedback.""",
    "conclusion": """So backpropagation is the secret behind learning without programming. No one tells the network what a cat looks like. It starts random, makes mistakes, and through countless corrections, the weights encode the patterns that define "cat-ness" itself. That's how modern AI learns - not from being told, but from being corrected, over and over, until it gets it right.""",
}

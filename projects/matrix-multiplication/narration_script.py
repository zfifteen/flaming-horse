"""
Narration script for: matrix-multiplication
Generated: 2026-02-13
Duration: ~240 seconds
"""

SCRIPT = {
    "intro": """Welcome to this video on matrix multiplication. Matrices are powerful mathematical tools that appear everywhere from computer graphics to machine learning. But multiplying them isn't as simple as multiplying regular numbers. In this video, we'll explore what matrix multiplication really means and why it's so important.""",
    "definition": """To multiply two matrices, the number of columns in the first matrix must equal the number of rows in the second. The result has the same number of rows as the first matrix and the same number of columns as the second. Each element in the result is the dot product of a row from the first matrix and a column from the second.""",
    "computation": """Let's work through a concrete example. Suppose we have a 2x3 matrix A and a 3x2 matrix B. To find the element in row 1, column 1 of the result, we multiply A's first row by B's first column: 1 times 4 plus 2 times 1 plus 3 times 2 equals 12. We'll calculate all the other elements the same way, building the result matrix step by step.""",
    "visualization": """Geometrically, matrix multiplication represents linear transformations. When you multiply a vector by a matrix, you're transforming that vector in space. Rotation matrices, scaling matrices, and projection matrices all work this way. Understanding this geometric view makes the algebra much clearer.""",
    "properties": """Matrix multiplication has some important properties. It's not commutative - AB doesn't equal BA in general. But it is associative, so (AB)C equals A(BC). This makes it perfect for representing complex transformations that can be combined in sequence.""",
    "recap": """To summarize, matrix multiplication combines rows and columns through dot products, with specific dimensional requirements. It represents linear transformations geometrically and has key algebraic properties. Mastering this operation unlocks the power of linear algebra in modern computing.""",
}

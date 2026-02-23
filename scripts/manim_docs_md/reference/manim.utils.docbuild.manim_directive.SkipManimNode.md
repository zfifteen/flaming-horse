<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.docbuild.manim_directive.SkipManimNode.html -->

# SkipManimNode

Qualified name: `manim.utils.docbuild.manim\_directive.SkipManimNode`

class SkipManimNode(*rawsource=''*, **children*, ***attributes*)[[source]](../_modules/manim/utils/docbuild/manim_directive.html#SkipManimNode)
:   Bases: `Admonition`, `Element`

    Auxiliary node class that is used when the `skip-manim` tag is present
    or `.pot` files are being built.

    Skips rendering the manim directive and outputs a placeholder instead.

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `basic_attributes` | Common list attributes. |
    | `child_text_separator` | Separator for child nodes, used by astext() method. |
    | `common_attributes` | Tuple of [`common attributes`__](#id1) known to all Doctree Element classes. |
    | `content_model` | Python representation of the element's content model (cf. |
    | `document` | Return the document root node of the tree containing this Node. |
    | `known_attributes` | Alias for common_attributes. |
    | `line` | The line number (1-based) of the beginning of this Node in source. |
    | `list_attributes` | Tuple of attributes that are initialized to empty lists. |
    | `local_attributes` | Obsolete. |
    | `parent` | Back-reference to the Node immediately containing this Node. |
    | `source` | Path or description of the input source which generated this Node. |
    | `tagname` | The element generic identifier. |
    | `valid_attributes` | Tuple of attributes that are valid for elements of this class. |
    | `rawsource` | The raw text from which this element was constructed. |
    | `children` | List of child nodes (elements and/or Text). |
    | `attributes` | value}. |

    Parameters:
    :   - **rawsource** (*str*)
        - **attributes** (*Any*)

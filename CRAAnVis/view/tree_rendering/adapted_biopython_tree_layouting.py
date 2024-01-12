
def set_x_positions(tree, app_config):
    """Adapted from Biopython: Create a mapping of each clade to its vertical position.

    Dict of {clade: y-coord}.
    Coordinates are negative, and integers for tips.
    """
    maxwidth = count_terminals(tree)

    # Rows are defined by the tips
    widths = {
        tip: maxwidth - i for i, tip in enumerate(reversed(get_terminals(tree)))
    }

    # Internal nodes: place at midpoint of children
    def calc_row(clade):
        for subclade in clade.c:
            if subclade not in widths:
                calc_row(subclade)
        widths[clade] = (
                                    widths[clade.c[0]] + widths[clade.c[-1]]
                            ) / 2.0

    if tree.c:
        calc_row(tree)

    for node, width in widths.items():
        node.x = width * app_config.t_dummy_node_width


def count_terminals(tree):
    counter = 0
    for node in tree.traverse_preorder():
        if node.cs == 0:
            counter += 1
    return counter


def get_terminals(tree):
    terminals = []
    for node in tree.traverse_preorder():
        if node.cs == 0:
            terminals.append(node)
    return terminals

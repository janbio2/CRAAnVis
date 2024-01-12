"""Functions for parsing newick strings into Tree objects often marked adaptions from ETE-Toolkit."""

import re


from model.tree import TreeNode


def _read_newick(newick, root_node=None, format=0, quoted_names=False):
    """
    Based on ETE-Toolkit function
    
    Read a newick tree from either a string or a file, and return
    an ETE tree structure.

    A previously existent node object can be passed as the root of the
    tree, which means that all its new children will belong to the same
    class as the root (this allows to work with custom Tree objects).

    You can also take advantage from this behaviour to concatenate
    several tree structures.
    """
    if root_node is None:
        root_node = TreeNode()

    newick = newick.strip()
    format = 1  # manualy set to 1
    matcher = compile_matchers(format)

    if not newick.endswith(';'):
        raise NewickError('Unexisting tree file or malformed newick tree structure.')

    return _read_newick_from_string(newick, root_node, matcher, format, quoted_names)


def _read_newick_from_string(nw, root_node, matcher, formatcode, quoted_names):
    """
    Based on ETE-Toolkit function

    Reads a newick string in the New Hampshire format.
    """
    
    if quoted_names:
        # Quoted text is mapped to references
        quoted_map = {}
        unquoted_nw = ''
        counter = 0
        for token in re.split(_QUOTED_TEXT_RE, nw):
            counter += 1
            if counter % 2 == 1:  # normal newick tree structure data
                unquoted_nw += token
            else:  # quoted text, add to dictionary and replace with reference
                quoted_ref_id = _QUOTED_TEXT_PREFIX + str(int(counter/2))
                unquoted_nw += quoted_ref_id
                quoted_map[quoted_ref_id] = token[1:-1]  # without the quotes
        nw = unquoted_nw

    if not nw.startswith('(') and nw.endswith(';'):
        _read_node_data(nw[:-1], root_node, "single", matcher, format)
        if quoted_names:
            if root_node.name.startswith(_QUOTED_TEXT_PREFIX):
                root_node.name = quoted_map[root_node.name]
        return root_node

    if nw.count('(') != nw.count(')'):
        raise NewickError('Parentheses do not match. Broken tree structure?')

    # white spaces and separators are removed
    nw = re.sub("[\n\r\t]+", "", nw)

    current_parent = None
    # Each chunk represents the content of a parent node, and it could contain
    # leaves and closing parentheses.
    # We may find:
    # leaf, ..., leaf,
    # leaf, ..., leaf))),
    # leaf)), leaf, leaf))
    # leaf))
    # ) only if formatcode == 100

    for chunk in nw.split("(")[1:]:
        # If no node has been created so far, this is the root, so use the node.
        if current_parent is None:
            current_parent = root_node
        else:
            current_parent.add_child()
            current_parent = current_parent.get_last_child()

        subchunks = [ch.strip() for ch in chunk.split(",")]
        # We should expect that the chunk finished with a comma (if next chunk
        # is an internal sister node) or a subchunk containing closing parenthesis until the end of the tree.
        # [leaf, leaf, '']
        # [leaf, leaf, ')))', leaf, leaf, '']
        # [leaf, leaf, ')))', leaf, leaf, '']
        # [leaf, leaf, ')))', leaf), leaf, 'leaf);']
        if subchunks[-1] != '' and not subchunks[-1].endswith(';'):
            raise NewickError('Broken newick structure at: %s' %chunk)

        # lets process the subchunks. Every closing parenthesis will close a
        # node and go up one level.
        for i, leaf in enumerate(subchunks):
            if leaf.strip() == '' and i == len(subchunks) - 1:
                continue  # "blah blah ,( blah blah"
            closing_nodes = leaf.split(")")

            # first part after splitting by ) always contain leaf info
            _read_node_data(closing_nodes[0], current_parent, "leaf", matcher, formatcode)

            # next contain closing nodes and data about the internal nodes.
            if len(closing_nodes) > 1:
                for closing_internal in closing_nodes[1:]:
                    closing_internal = closing_internal.rstrip(";")
                    # read internal node data and go up one level
                    _read_node_data(closing_internal, current_parent, "internal", matcher, formatcode)
                    current_parent = current_parent.parent

    # references in node names are replaced with quoted text before returning
    if quoted_names:
        for node in root_node.traverse():
            if node.name.startswith(_QUOTED_TEXT_PREFIX):
                node.name = quoted_map[node.name]

    return root_node


def _read_node_data(subnw, current_node, node_type, matcher, formatcode):
    """
    Based on ETE-Toolkit function
    
    Reads a leaf node from a subpart of the original newick
    tree """

    current_node : TreeNode

    if node_type == "leaf" or node_type == "single":
        if node_type == "leaf":
            current_node.add_child()
            node = current_node.get_last_child()
        else:
            node = current_node
    else:
        node = current_node

    subnw = subnw.strip()

    if not subnw and node_type == 'leaf' and formatcode != 100:
        raise NewickError('Empty leaf node found')
    elif not subnw:
        return

    container1, container2, converterFn1, converterFn2, compiled_matcher = matcher[node_type]
    data = re.match(compiled_matcher, subnw)
    if data:
        data = data.groups()
        # This prevents ignoring errors even in flexible nodes:
        if subnw and data[0] is None and data[1] is None and data[2] is None:
            raise NewickError("Unexpected newick format '%s'" %subnw)

        if data[0] is not None and data[0] != '':
            property_name = container1
            property_content = converterFn1(data[0].strip())
            # node.add_prop(container1, converterFn1(data[0].strip()))
            #print(f"property_name container1 is: {property_name}")
            #print(f"property_content is: {property_content}")
            if property_name == "name":
                node.name = property_content

        if data[1] is not None and data[1] != '':
            property_name = container2
            property_content = converterFn2(data[1][1:].strip())
            # node.add_prop(container2, converterFn2(data[1][1:].strip()))
            # print(f"property_name container2 is: {property_name}")
            # print(f"property_content is: {property_content}")
            if property_name == "dist":
                node.distance = property_content

    else:
        raise NewickError("Unexpected newick format '%s' " %subnw[0:50])
    return

# All Original ETE-Toolkit code from here on:

_FLOAT_RE = "\s*[+-]?\d+\.?\d*(?:[eE][-+]?\d+)?\s*"
_NAME_RE = "[^():,;]+?"
_NHX_RE = "\[&&NHX:[^\]]*\]"

_QUOTED_TEXT_RE = r"""((?=["'])(?:"[^"\\]*(?:\\[\s\S][^"\\    ]*)*"|'[^'\\]*(?:\\[\s\S][^'\\]*)*'))"""
_QUOTED_TEXT_PREFIX='ete3_quotref_'

NW_FORMAT = {
  0:   [['name', str, True],  ["dist", float, True],   ['support', float, True],  ["dist", float, True]], # Flexible with support
  1:   [['name', str, True],  ["dist", float, True],   ['name', str, True],       ["dist", float, True]], # Flexible with internal node names
  2:   [['name', str, False], ["dist", float, False],  ['support', float, False], ["dist", float, False]], # Strict with support values
  3:   [['name', str, False], ["dist", float, False],  ['name', str, False],      ["dist", float, False]], # Strict with internal node names
  4:   [['name', str, False], ["dist", float, False],  [None, None, False],       [None, None, False]],
  5:   [['name', str, False], ["dist", float, False],  [None, None, False],       ["dist", float, False]],
  6:   [['name', str, False], [None, None, False],     [None, None, False],       ["dist", float, False]],
  7:   [['name', str, False], ["dist", float, False],  ["name", str, False],      [None, None, False]],
  8:   [['name', str, False], [None, None, False],     ["name", str, False],      [None, None, False]],
  9:   [['name', str, False], [None, None, False],     [None, None, False],       [None, None, False]], # Only topology with node names
  100: [[None, None, False],  [None, None, False],     [None, None, False],       [None, None, False]] # Only Topology
}


def compile_matchers(formatcode):
    matchers = {}
    for node_type in ["leaf", "single", "internal"]:
        if node_type == "leaf" or node_type == "single":
            container1 = NW_FORMAT[formatcode][0][0]
            container2 = NW_FORMAT[formatcode][1][0]
            converterFn1 = NW_FORMAT[formatcode][0][1]
            converterFn2 = NW_FORMAT[formatcode][1][1]
            flexible1 = NW_FORMAT[formatcode][0][2]
            flexible2 = NW_FORMAT[formatcode][1][2]
        else:
            container1 = NW_FORMAT[formatcode][2][0]
            container2 = NW_FORMAT[formatcode][3][0]
            converterFn1 = NW_FORMAT[formatcode][2][1]
            converterFn2 = NW_FORMAT[formatcode][3][1]
            flexible1 = NW_FORMAT[formatcode][2][2]
            flexible2 = NW_FORMAT[formatcode][3][2]

        if converterFn1 == str:
            FIRST_MATCH = "("+_NAME_RE+")"
        elif converterFn1 == float:
            FIRST_MATCH = "("+_FLOAT_RE+")"
        elif converterFn1 is None:
            FIRST_MATCH = '()'
        else:
            FIRST_MATCH = ""
            raise NewickError("Unsupported data type FIRST_MATCH")

        if converterFn2 == str:
            SECOND_MATCH = "(:"+_NAME_RE+")"
        elif converterFn2 == float:
            SECOND_MATCH = "(:"+_FLOAT_RE+")"
        elif converterFn2 is None:
            SECOND_MATCH = '()'
        else:
            SECOND_MATCH = ""
            raise NewickError("Unsupported data type SECOND_MATCH")

        if flexible1 and node_type != 'leaf':
            FIRST_MATCH += "?"
        if flexible2:
            SECOND_MATCH += "?"


        matcher_str= '^\s*%s\s*%s\s*(%s)?\s*$' % (FIRST_MATCH, SECOND_MATCH, _NHX_RE)
        compiled_matcher = re.compile(matcher_str)
        matchers[node_type] = [container1, container2, converterFn1, converterFn2, compiled_matcher]

    return matchers


class NewickError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        if value is None:
            value = ''
        value += "\nYou may want to check other newick loading flags like 'format' or 'quoted_node_names'."
        Exception.__init__(self, value)


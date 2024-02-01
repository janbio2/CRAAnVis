from collections import deque
from typing import Dict, List, Optional
from model.helper_functions import is_flat


def produce_tree_model(data):
    """Produce a tree model from the data."""
    root = TreeNode()
    root.parse_newick(data["newick"])
    root.parse_evolutionary_events(data)
    return root


class TreeNode:
    """Tree class"""

    def __init__(self, name: Optional[str] = None):

        self.root = None
        self.name = name
        self.children = []
        self.parent = None
        self.distance = None

        self.events: Dict[str, List[str]] = {
            'gains': [],
            'losses': [],
            'contradictions': [],
            'duplications': [],
            'rearrangements': [],
            'double_gains': [],
            'independent_gains': [],
            'reacquisitions': [],
            'dups': []
        }

    def parse_newick(self, newick: str):
        """
        Read newick string.
        :param newick: newick string
        :return: Tree object
        """
        from model.newick_parser import _read_newick  # local import to avoid circular dependency
        return _read_newick(newick, self)

    def add_distance(self, distance):
        """Add distance to node"""
        self.distance = distance

    def add_child(self, child: Optional['TreeNode'] = None,
                  name=None, distance=None):
        """Add a child to the tree"""
        if child is None:
            child = TreeNode()
        if name is not None:
            child.name = name
        if distance is not None:
            child.distance = distance
        child.parent = self
        self.children.append(child)

    def get_last_child(self):
        """Get last child"""
        return self.children[-1]

    def traverse(self):
        """Traverse tree levelorder based on ETE toolkit function"""
        tovisit = deque([self])
        while len(tovisit) > 0:
            node = tovisit.popleft()
            yield node
            tovisit.extend(node.children)

    def parse_evolutionary_events(self, data):
        """get evolutionary events information and assign to nodes from data"""




        for node in self.traverse():
            if node.name in data['rec_gains_losses']['rec_gains'].keys():
                node.events['gains'] = data['rec_gains_losses']['rec_gains'][node.name]
            if node.name in data['rec_gains_losses']['rec_losses'].keys():
                node.events['losses'] = data['rec_gains_losses']['rec_losses'][node.name]

            if node.name in data['other_events']['rec_contra_dict'].keys():
                node.events['contradictions'] = data['other_events']['rec_contra_dict'][node.name]
            if node.name in data['other_events']['rec_duplications_dict'].keys():
                node.events['duplications'] = data['other_events']['rec_duplications_dict'][node.name]
            if node.name in data['other_events']['rec_rearrangements_dict'].keys():
                node.events['rearrangements'] = data['other_events']['rec_rearrangements_dict'][node.name]

            # decide which SpacerPlacer output data version is available
            old_categories = ["rec_double_gains_dict", "rec_default_or_indep_gains_dict"]
            new_categories = ["rec_reacquisition_dict", "rec_indep_gain_dict", "rec_other_dup_events_dict"]

            if all(category in data['other_events'].keys() for category in old_categories):
                if node.name in data['other_events']['rec_double_gains_dict'].keys():
                    node.events['double_gains'] = data['other_events']['rec_double_gains_dict'][node.name]
                if node.name in data['other_events']['rec_default_or_indep_gains_dict'].keys():
                    node.events['independent_gains'] = data['other_events']['rec_default_or_indep_gains_dict'][node.name]

            if all(category in data['other_events'].keys() for category in new_categories):
                if node.name in data['other_events']['rec_reacquisition_dict'].keys():
                    node.events[('reacquisitions')] = data['other_events']['rec_reacquisition_dict'][node.name]
                if node.name in data['other_events']['rec_indep_gain_dict'].keys():
                    node.events['independent_gains'] = data['other_events']['rec_indep_gain_dict'][node.name]
                if node.name in data['other_events']['rec_other_dup_events_dict'].keys():
                    node.events['dups'] = data['other_events']['rec_other_dup_events_dict'][node.name]



    def is_leaf(self):
        """Check if node is leaf"""
        return len(self.children) == 0


def connect_names_to_spacer_models(name_list, name_element_dict):
    if is_flat(name_list):
        return [(name, name_element_dict[name]) for name in name_list]
    else:
        return [[(name, name_element_dict[name]) for name in sublist] for sublist in name_list]

from typing import List, Dict, Tuple

from model.helper_functions import flatten


class SpacerData:
    """Represents a single spacer in a CRISPR array."""
    def __init__(self, name: str, original_name: str, index: int, duplicates: set, metadata: Dict = None):
        self.name = str(name)
        self.original_name = original_name
        self.index = index
        self.duplicates = duplicates
        self.metadata = metadata


class ArrayData:
    """Represents an arrays of Crispr Spacer."""
    def __init__(self, name, spacers: List[SpacerData] = None):
        self.name = name
        if spacers is None:
            spacers = []
        self.spacers = spacers

    def add_spacer(self, spacer: SpacerData):
        self.spacers.append(spacer)


def find_singular_stretches(sg_events: set, template: List[SpacerData]) -> List[List[Tuple[int, str]]]:
    """Find singular stretches of spacer gains in the template array."""
    indices = [spacer.index for spacer in template if spacer.name in sg_events]
    names = [spacer.name for spacer in template if spacer.name in sg_events]
    singular_stretches = []
    if len(indices) > 0:
        current_stretch = [(indices[0], names[0])]
        for i in range(1, len(indices)):
            if indices[i] == indices[i-1] + 1:
                current_stretch.append((indices[i], names[i]))
            else:
                singular_stretches.append(current_stretch)
                current_stretch = [(indices[i], names[i])]
        singular_stretches.append(current_stretch)

    return singular_stretches


def find_duplicates(spacer_names_to_numbers):
    """Find duplicates in spacer_names_to_numbers."""
    org_name_duplicates = {}
    sp_name_dupls = {}

    for org_name, sp_name in spacer_names_to_numbers.items():
        sp_name = str(sp_name)
        pruned_org_name = "".join(filter(str.isdigit, org_name))
        if pruned_org_name not in org_name_duplicates:
            org_name_duplicates[pruned_org_name] = set()
        org_name_duplicates[pruned_org_name].add(sp_name)

    org_name_duplicates = {k: v for k, v in org_name_duplicates.items() if len(v) > 1}

    for org_name, sp_names in org_name_duplicates.items():
        for sp_name in sp_names:
            if sp_name not in sp_name_dupls:
                sp_name_dupls[sp_name] = sp_names.copy()
                sp_name_dupls[sp_name].remove(sp_name)

    return sp_name_dupls



def gather_upstream_losses(node, node_set) -> set:
    """Recursively gather upstream losses"""
    node_set.update(str(x) for x in flatten(node.events["losses"]))
    if node.parent:
        node_set.update(gather_upstream_losses(node.parent, node_set))
    return node_set


def gather_upstream_gains(node, node_set) -> set:
    """Recursively gather upstream gains"""
    node_set.update(str(x) for x in node.events["gains"])
    node_set.update(str(x) for x in node.events["contradictions"])
    node_set.update(str(x) for x in node.events["duplications"])
    node_set.update(str(x) for x in node.events["rearrangements"])
    node_set.update(str(x) for x in node.events["double_gains"])
    node_set.update(str(x) for x in node.events["independent_gains"])
    if node.parent:
        node_set.update(gather_upstream_gains(node.parent, node_set))
    return node_set


def leaf_losses_dictionary(root) -> Dict[str, set]:
    """Produce dictionary leafnames : upstream_losses_set."""
    leaf_losses = {}
    for node in root.traverse():
        if node.is_leaf():
            leaf_losses[node.name] = set()
            gather_upstream_losses(node, leaf_losses[node.name])
    return leaf_losses


def get_node_by_name(root, name):
    return_node = None
    for node in root.traverse():
        if node.name == name:
            return_node = node
            break
    return return_node

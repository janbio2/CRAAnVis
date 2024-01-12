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


def add_array_model(data, model_container):
    """Add array model to model_container."""

    top_order = data['top_order']
    spacer_names_to_numbers = data['spacer_names_to_numbers']

    sp_name_duplicates = find_duplicates(spacer_names_to_numbers)

    rec_spacers = data['rec_spacers']
    rec_spacers = rec_spacers['rec_spacers']

    leaf_rec_spacers = {k: v for k, v in rec_spacers.items() if not k.startswith('Inner')}
    array_names = list(leaf_rec_spacers.keys())
    number_of_arrays = len(array_names)

    if 'metadata' in data:
        metadata = data['metadata']
    else:
        metadata = {}

    # produce template array
    array_length = len(top_order)
    template_array = ArrayData("template")

    for x in range(array_length):
        original_name = str(top_order[x])
        spacer_name = str(spacer_names_to_numbers[original_name])
        duplicates = None
        if spacer_name in sp_name_duplicates:
            duplicates = sp_name_duplicates[spacer_name]

        if spacer_name not in metadata:
            metadata[spacer_name] = {}
        spacer_metadata = metadata[spacer_name]
        new_spacer_data = SpacerData(spacer_name, original_name, x, duplicates, spacer_metadata)
        template_array.add_spacer(new_spacer_data)
    model_container.add_template_array(template_array)

    # produce all other arrays
    array_names_losses = leaf_losses_dictionary(model_container.tree)

    for x in range(len(array_names)):
        new_array = []
        new_array_name = array_names[x]
        spacers_existing = leaf_rec_spacers[new_array_name]
        names_of_deleted_spacers = array_names_losses[new_array_name]

        for exists, spacer_data in zip(spacers_existing, model_container.template.spacers):
            if exists == 1:
                new_array.append(1)
            elif spacer_data.name in names_of_deleted_spacers:
                new_array.append("d")
            else:
                new_array.append(0)

        model_container.arrays_dict[new_array_name] = new_array

    # add frequencies to template arrays
    for x in range(array_length):
        sp_count = 0
        sp_d_count = 0

        for array in model_container.arrays_dict.values():
            if array[x] in [1, "d"]:
                sp_d_count += 1
                if array[x] == 1:
                    sp_count += 1
        model_container.template.spacers[x].metadata["sp_frequency"] = sp_count/number_of_arrays
        model_container.template.spacers[x].metadata["sp_d_frequency"] = sp_d_count/number_of_arrays

    return model_container


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

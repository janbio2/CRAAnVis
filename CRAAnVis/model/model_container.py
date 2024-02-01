from collections import Counter
from typing import List, Tuple

from model.arrays import ArrayData
from model.helper_functions import flatten


class ModelContainer:
    """Container class for organizing multiple SpacerArrays."""

    def __init__(self, template: ArrayData = None, arrays: [] = None):
        self.template = template
        self.arrays_dict = {}
        if arrays is None:
            arrays = []
        for array in arrays:
            self.arrays_dict[array.name] = array
        self.tree = None

        # variables for collapsing leaf insertions
        self.array_singular_leaf_inserts = None
        self.singular_stretches = None
        self.sg_leaf_inserts_arrayname = None
        self.stretch_array_length = None
        self.stretch_array_order = None
        self.stretch_max_len = None
        self.stretch_array_shift = None
        self.stretch_arrayname_spacers = None
        self.stretch_max_length = None

        # variables for tree_legend
        self.item_types_in_tree = None

    def get_item_types_in_tree(self):
        if self.item_types_in_tree:
            return self.item_types_in_tree
        else:
            if not self.tree:
                return set()
            translation = {
                'gains': 'Acquisitions',
                'losses': 'Deletions',
                'contradictions': 'Contradictions',
                'duplications': 'Duplications',
                'rearrangements': 'Rearrangements',
                'double_gains': 'Reacquisition',
                'independent_gains': 'Ind. acquisition',
                'dups': 'Other Type of Dup. Insertion'
            }

            self.item_types_in_tree = set()
            for node in self.tree.traverse():
                for k, v in node.events.items():
                    if len(v) > 0:
                        self.item_types_in_tree.add(translation[k])
            return self.item_types_in_tree

    def add_template_array(self, template):
        self.template = template

    def get_array_names(self) -> List[str]:
        """Return a list of all array names."""
        return list(self.arrays_dict.keys())

    def get_spacer_names(self) -> List[str]:
        """Return a list of all spacer names."""
        spacer_names = [spacer.name for spacer in self.template.spacers]
        return spacer_names

    def get_singular_leaf_inserts(self):
        """Return a list of all singular leaf insertions."""
        if self.array_singular_leaf_inserts:
            return self.array_singular_leaf_inserts
        if not self.tree:
            return {}
        visited = set()
        arrayname_sgl_leaf_inserts = {}
        for node in self.tree.traverse():
            if node.is_leaf():
                sg_events = {str(gain) for gain in node.events["gains"]}
                arrayname_sgl_leaf_inserts[node.name] = sg_events
            else:
                visited.update(str(event) for events in node.events.values() for event in flatten(events))

        # remove all events that are not singular
        for array_name, sg_events in arrayname_sgl_leaf_inserts.items():
            sg_events.difference_update(visited)

        all_inserts = [gain for gains in arrayname_sgl_leaf_inserts.values() for gain in gains]
        all_inserts_counts = Counter(all_inserts)

        for array_name in arrayname_sgl_leaf_inserts.keys():
            arrayname_sgl_leaf_inserts[array_name] = [event for event in arrayname_sgl_leaf_inserts[array_name] if
                                                      all_inserts_counts[event] == 1]

        self.array_singular_leaf_inserts = arrayname_sgl_leaf_inserts
        self.sg_leaf_inserts_arrayname = {spacer_name: array_name for
                                          array_name, spacer_names in self.array_singular_leaf_inserts.items() for
                                          spacer_name in spacer_names}

        return self.array_singular_leaf_inserts

    def find_singular_stretches(self) -> List[List[Tuple[int, str]]]:
        """Find singular stretches of spacer gains in the template array."""
        if self.singular_stretches:
            return self.singular_stretches
        if not self.tree:
            return []
        if not self.array_singular_leaf_inserts:
            return []
        sg_l_ins_set = set()
        sg_l_ins_set.update(str(event) for events in self.array_singular_leaf_inserts.values() for event in events)

        indices = [spacer.index for spacer in self.template.spacers if spacer.name in sg_l_ins_set]
        names = [spacer.name for spacer in self.template.spacers if spacer.name in sg_l_ins_set]
        self.singular_stretches = []
        if len(indices) > 0:
            current_stretch = [(indices[0], names[0])]
            for i in range(1, len(indices)):
                if indices[i] == indices[i - 1] + 1:
                    current_stretch.append((indices[i], names[i]))
                else:
                    self.singular_stretches.append(current_stretch)
                    current_stretch = [(indices[i], names[i])]
            self.singular_stretches.append(current_stretch)

        return self.singular_stretches

    def array_len_and_ordr_in_collapse_parts(self):
        if not self.singular_stretches:
            return {}, {}, {}, {}
        if not self.sg_leaf_inserts_arrayname:
            return {}, {}, {}, {}
        if (self.stretch_array_length and
                self.stretch_array_order and
                self.stretch_max_len and
                self.stretch_array_shift):
            return self.stretch_array_length, self.stretch_array_order, self.stretch_max_len, self.stretch_array_shift

        # calculate new length of stretches
        # for each stretch start at leftmost index.
        stretch_array_length = {}
        stretch_array_order = {}
        stretch_array_shift = {}

        # for each stretch which array is it in and what are the spacers they contain
        if not self.stretch_arrayname_spacers:
            self.stretch_arrayname_spacers = []
            for stretch in self.singular_stretches:
                array_name_spacers_dict = {}
                for ix_sp_name in stretch:
                    if self.sg_leaf_inserts_arrayname[ix_sp_name[1]] not in array_name_spacers_dict:
                        array_name_spacers_dict[self.sg_leaf_inserts_arrayname[ix_sp_name[1]]] = []
                    array_name_spacers_dict[self.sg_leaf_inserts_arrayname[ix_sp_name[1]]].append(ix_sp_name)
                self.stretch_arrayname_spacers.append(array_name_spacers_dict)

        for stretch_ix, stretch in enumerate(self.singular_stretches):
            array_length = {}
            array_shift = {}
            array_order = {}

            curr_array = self.sg_leaf_inserts_arrayname[stretch[0][1]]

            # calculate the order of the arrays in the stretch
            array_order_nr = 0
            for ix, sp_name in stretch[1:]:
                if curr_array != self.sg_leaf_inserts_arrayname[sp_name]:
                    if curr_array not in array_order:
                        array_order[curr_array] = array_order_nr
                        array_order_nr += 1
                    curr_array = self.sg_leaf_inserts_arrayname[sp_name]
            if curr_array not in array_order:
                array_order[curr_array] = array_order_nr

            # calculate the length of the stretch and the inner stretch shift
            min_stretch_sp_ix = min([sp[0] for sp in stretch])
            for arr_name, sp_ix_names in self.stretch_arrayname_spacers[stretch_ix].items():
                array_spacer_ixs = [ix_name[0] for ix_name in sp_ix_names]
                arr_sp_min_ix = min(array_spacer_ixs)
                arr_sp_max_ix = max(array_spacer_ixs)
                array_length[arr_name] = arr_sp_max_ix - arr_sp_min_ix + 1
                array_shift[arr_name] = arr_sp_min_ix - min_stretch_sp_ix - array_order[arr_name]

            stretch_array_length[stretch_ix] = array_length
            stretch_array_order[stretch_ix] = array_order
            stretch_array_shift[stretch_ix] = array_shift

            # adapt the inner stretch shift to the order of the arrays

        self.stretch_array_length = stretch_array_length
        self.stretch_array_order = stretch_array_order
        self.stretch_array_shift = stretch_array_shift

        self.stretch_max_length = {}
        for stretch_ix in self.stretch_array_order.keys():
            max_len = 0
            for array_name in self.stretch_array_order[stretch_ix].keys():
                max_len = max(max_len,
                              self.stretch_array_length[stretch_ix][array_name] + self.stretch_array_order[stretch_ix][
                                  array_name])
            self.stretch_max_length[stretch_ix] = max_len

        return self.stretch_array_length, self.stretch_array_order, self.stretch_max_length, self.stretch_array_shift

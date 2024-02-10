import math
from collections import deque

from PyQt6.QtCore import QPointF, QObject, QLineF
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtWidgets import QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsRectItem, QMenu, \
    QGraphicsLineItem

from model.app_config import AppConfig
from model.helper_functions import is_flat, find_incremental_series, flatten
from model.tree import TreeNode
from view.colors.colors import produce_random_color
from view.tree_rendering.adapted_biopython_tree_layouting import set_x_positions
from view.tree_rendering.tree_events import produce_events, FrameItem, EventRectItem


class NodeItem(QGraphicsEllipseItem):
    """Class for the visual representation of a node in the tree view"""
    def __init__(self, view_model_node, model_node: TreeNode, app_config: AppConfig):

        super().__init__()
        self.app_config = app_config
        self.model_node = model_node
        self.view_model_node = view_model_node
        self.setBrush(app_config.t_node_color)
        self.setRect(0, 0, app_config.t_node_width, app_config.t_node_height)
        self.setZValue(1)

        self.inner_array_is_shown = False

        # tooltip
        tt_string = f"Node {self.model_node.name}"
        self.setToolTip(tt_string)

        # connect to tree signal manager for checking action states
        self.app_config.tree_signal_manager.show_inner_array.connect(self.notice_if_inner_array_is_shown)

    def notice_if_inner_array_is_shown(self, showing_node):
        if showing_node == self.model_node.name:
            self.inner_array_is_shown = not self.inner_array_is_shown
        else:
            self.inner_array_is_shown = False

    def contextMenuEvent(self, event):
        contextMenu = QMenu()
        swapChildNodesAction = QAction("Swap Child Nodes")
        if self.view_model_node.can_be_switched:
            swapChildNodesAction.setEnabled(True)
        else:
            swapChildNodesAction.setText("Node switching is unavailable while array parts are collapsed.")
            swapChildNodesAction.setEnabled(False)
        swapChildNodesAction.setCheckable(True)
        swapChildNodesAction.setChecked(self.view_model_node.c_switched)

        showInnerArrayAction = QAction("Show Set of Spacers at Node")
        showInnerArrayAction.setCheckable(True)
        showInnerArrayAction.setChecked(self.inner_array_is_shown)
        if self.view_model_node.can_be_switched:
            showInnerArrayAction.setEnabled(True)
        else:
            showInnerArrayAction.setText(
                "Showing Set of Spacers at Node not available while array parts are collapsed.")
            showInnerArrayAction.setEnabled(False)

        swapChildNodesAction.triggered.connect(self.switch_node_children)
        contextMenu.addAction(swapChildNodesAction)

        showInnerArrayAction.triggered.connect(self.show_n_sp_in_arrays)
        contextMenu.addAction(showInnerArrayAction)

        if len(self.model_node.children) == 0:
            swapChildNodesAction.setEnabled(False)
            showInnerArrayAction.setEnabled(False)
        contextMenu.exec(event.screenPos())

    def show_n_sp_in_arrays(self):
        self.app_config.tree_signal_manager.show_inner_array.emit(self.view_model_node.name)

    def switch_node_children(self):
        if self.view_model_node.c_switched:
            self.view_model_node.c_switched = False
        else:
            self.view_model_node.c_switched = True
        self.view_model_node.needs_switching = True
        self.app_config.tree_signal_manager.redrawTree.emit()


class TreeViewNode:
    """Class organising the visual representation of a tree node."""

    def __init__(self, root: TreeNode, tree_nodes: list, app_config: AppConfig):

        self.c_switched = False
        self.needs_switching = False
        self.can_be_switched = True

        self.c = []
        self.cs = 0

        self.events = []
        self.events = root.events
        self.event_items_dict = produce_events(root.events, app_config)

        self.distance = root.distance
        # node envelope size
        self.width = app_config.t_dummy_node_width
        self.extension_length = calc_event_extension_h(self, app_config)
        self.non_extension_len = 0
        self.height = 0

        # node positions/coordinates
        self.x = 0
        self.y = 0

        self.parent = None
        self.name = root.name

        self.qnode = NodeItem(self, root, app_config)
        tree_nodes.append(self.qnode)

        for c in root.children:
            new_child = TreeViewNode(c, tree_nodes, app_config)
            new_child.parent = self
            self.c.append(new_child)

            self.cs += 1

    def group_and_position_events(self, app_config: AppConfig):
        events_group = QGraphicsItemGroup()
        for node in self.traverse():
            curr_e_group = group_node_events_and_set_pos(node, app_config)
            events_group.addToGroup(curr_e_group)
        return events_group

    def set_node_positions(self):
        for node in self.traverse():
            node.qnode.setPos(node.x, node.y)

    def produce_leaf_tags(self, app_config: AppConfig):
        name_leaf_tag = {}
        for node in self.traverse():
            if not app_config.show_inner_l_tags:
                if node.name.startswith("Inner"):
                    continue
            txt_to_display = str(node.name)
            if node.name.startswith("Inner"):
                for child in node.c:
                    txt_to_display += "  " + str(child.name)
            text = QGraphicsSimpleTextItem(txt_to_display, node.qnode)
            text.setFont(app_config.t_leaf_tag_font)

            text_pos = QPointF(node.qnode.rect().right() + 10,
                               node.qnode.rect().center().y() - text.boundingRect().center().y())
            text.setPos(text_pos)
            text.setZValue(1)
            name_leaf_tag[node.name] = text

            if not app_config.horizontal_mode:
                # Set the rotation of the text to 90 degrees if in vertical mode.
                text.setRotation(90)
        return name_leaf_tag

    def update_leaf_tag_pos(self, leaf_tags, app_config: AppConfig):
        for node in self.traverse():
            if not app_config.show_inner_l_tags:
                if node.name.startswith("Inner"):
                    continue
            tag_name = node.name
            tag_center_y = leaf_tags[tag_name].boundingRect().center().y()
            new_text_pos = QPointF(node.qnode.sceneBoundingRect().right() + 10,
                                   node.qnode.sceneBoundingRect().center().y() - tag_center_y)
            leaf_tags[tag_name].setPos(new_text_pos)

    def add_node_size_illustration(self):
        """Debug function to visualize the size of the nodes"""
        for node in self.traverse():
            x = (node.qnode.rect().width() / 2) - node.height
            y = (node.qnode.rect().height() / 2) - node.width / 2

            item = QGraphicsRectItem(x, y, node.height, node.width, node.qnode)
            color = QColor(produce_random_color())
            item.setBrush(color)
            item.setOpacity(0.2)
            item.setZValue(-1)

    def traverse(self):
        """Traverse tree levelorder based on ETE toolkit function"""
        tovisit = deque([self])
        while len(tovisit) > 0:
            node = tovisit.popleft()
            yield node
            tovisit.extend(node.c)

    def traverse_preorder(self):
        """adapted ete toolkit funciton. Yield all descendant nodes in preorder."""
        to_visit = deque()
        node = self
        while node is not None:
            yield node
            if self.cs > 0:
                to_visit.extendleft(reversed(node.c))
            try:
                node = to_visit.popleft()
            except IndexError:
                node = None

    def traverse_postorder(self):
        """Yield all descendant nodes in postorder."""
        to_visit = deque()
        node = self
        while node is not None or to_visit:
            if node is not None:
                to_visit.append(node)
                if node.cs > 0:
                    node = node.c[0]
                else:
                    node = None
            else:
                node = to_visit.pop()
                yield node
                if to_visit and node == to_visit[-1].c[-1]:
                    node = None
                else:
                    node = to_visit[-1].c[node.parent.c.index(node) + 1] if to_visit else None


def switch_x_y(root: TreeViewNode):
    for node in root.traverse_preorder():
        old_x = node.x
        old_y = node.y
        node.y = old_x
        node.x = old_y


def add_items(app_config, bottom_branch_events, bottom_branch_offset, node, top_branch_events, top_branch_offset):
    for event_type, e_list in node.event_items_dict.items():
        if event_type.endswith("_pools"):
            continue
        branch_pos = app_config.event_positions[event_type]
        curr_frame = None
        if not is_flat(e_list):
            e_list = flatten(e_list)

        if branch_pos == "top-branch":
            for item in e_list:
                new_pt = QPointF(0 + top_branch_offset, 0)
                item.setPos(new_pt)
                top_branch_offset += app_config.event_width
                top_branch_events.addToGroup(item)
                if isinstance(item, EventRectItem):
                    if item.frame != curr_frame:
                        curr_frame = item.frame
                        curr_frame.setPos(new_pt)
                        top_branch_events.addToGroup(curr_frame)

        elif branch_pos == "bottom-branch":
            for item in e_list:
                new_pt = QPointF(0 + bottom_branch_offset, 0)
                item.setPos(new_pt)
                bottom_branch_offset += app_config.event_width
                bottom_branch_events.addToGroup(item)
                if isinstance(item, EventRectItem):
                    if item.frame != curr_frame:
                        curr_frame = item.frame
                        curr_frame.setPos(new_pt)
                        bottom_branch_events.addToGroup(curr_frame)

        else:
            raise ValueError("Unknown branch position: " + branch_pos)
    return bottom_branch_offset, top_branch_offset


def paint_new_frame(frame_buffer, bottom_branch_events, app_config):
    width = frame_buffer[-1].pos().x() - frame_buffer[0].pos().x() + app_config.event_width
    names = [item.name for item in frame_buffer]
    frame = FrameItem(frame_buffer[0].pos().x(), frame_buffer[0].pos().y(),
                      width, app_config.event_height,
                      names, QColor("red"), 1)
    frame.setZValue(6)
    bottom_branch_events.addToGroup(frame)


def paint_frame_in_buffer(frame_buffer, bottom_branch_events, app_config):
    # inside buffer check if frames are overlapping

    curr_item = frame_buffer[0]
    new_buffer = [curr_item]
    for x in range(1, len(frame_buffer)):
        next_item = frame_buffer[x]
        distance = next_item.pos().x() - curr_item.pos().x()
        if distance > app_config.event_width:
            # paint frame
            paint_new_frame(new_buffer, bottom_branch_events, app_config)
            new_buffer = []
        new_buffer.append(next_item)
        curr_item = next_item
    if len(new_buffer) > 0:
        paint_new_frame(new_buffer, bottom_branch_events, app_config)


def add_items_add_pools(app_config, bottom_branch_events, bottom_branch_offset, branch_pos, e_list_items, e_list_pools,
                        item_pooled_in_pool_ix, item_skip_list, top_branch_events, top_branch_offset):
    if branch_pos == "top-branch":
        for item in e_list_items:
            if item.name in item_skip_list:
                continue
            if item.name in item_pooled_in_pool_ix.keys():
                pool_ix = item_pooled_in_pool_ix[item.name]
                pool_item = e_list_pools[pool_ix]
                new_pt = QPointF(0 + top_branch_offset, 0)
                pool_item.setPos(new_pt)
                top_branch_events.addToGroup(pool_item)
                top_branch_offset += app_config.epool_width

                for pooled_item in pool_item.pooled_event_items:
                    item_skip_list.append(pooled_item.name)
            else:
                new_pt = QPointF(0 + top_branch_offset, 0)
                item.setPos(new_pt)
                top_branch_offset += app_config.event_width
                top_branch_events.addToGroup(item)
    elif branch_pos == "bottom-branch":
        for item in e_list_items:
            if item.name in item_skip_list:
                continue
            if item.name in item_pooled_in_pool_ix.keys():
                pool_ix = item_pooled_in_pool_ix[item.name]
                pool_item = e_list_pools[pool_ix]
                new_pt = QPointF(0 + bottom_branch_offset, 0)
                pool_item.setPos(new_pt)
                bottom_branch_events.addToGroup(pool_item)
                bottom_branch_offset += app_config.epool_width

                for pooled_item in pool_item.pooled_event_items:
                    item_skip_list.append(pooled_item.name)
            else:
                new_pt = QPointF(0 + bottom_branch_offset, 0)
                item.setPos(new_pt)
                bottom_branch_offset += app_config.event_width
                bottom_branch_events.addToGroup(item)
    else:
        raise ValueError("Unknown branch position: " + branch_pos)

    frame_buffer = []
    for item in bottom_branch_events.childItems():
        if isinstance(item, EventRectItem):
            curr_frame = item.frame
            if len(frame_buffer) > 0:
                last_item = frame_buffer[-1]
                if last_item.frame != curr_frame:
                    paint_frame_in_buffer(frame_buffer, bottom_branch_events, app_config)
                    frame_buffer = []
            frame_buffer.append(item)
    if len(frame_buffer) > 0:
        paint_frame_in_buffer(frame_buffer, bottom_branch_events, app_config)

    return bottom_branch_offset, top_branch_offset


def group_node_events_and_set_pos(node: TreeViewNode, app_config: AppConfig):
    event_group = QGraphicsItemGroup()
    top_branch_events = QGraphicsItemGroup()
    bottom_branch_events = QGraphicsItemGroup()

    top_branch_offset = 0
    bottom_branch_offset = 0

    for items in node.event_items_dict.values():
        if not is_flat(items):
            items = flatten(items)
        for item in items:
            if item.parentItem() is not None:
                if isinstance(item, EventRectItem):
                    item.frame.setParentItem(None)
                item.parentItem().removeFromGroup(item)

    # Item Pooling Start
    pool_eid_keys = [key for key in node.event_items_dict.keys() if key.endswith("_pools")]
    corresponding_eid_keys = [key[:-6] for key in pool_eid_keys]
    other_keys = [key for key in node.event_items_dict.keys() if
                  key not in pool_eid_keys and key not in corresponding_eid_keys]
    if len(other_keys) > 0:
        pass

    key_order = zip(pool_eid_keys, corresponding_eid_keys)

    if app_config.event_pooling:
        for pool_eid_key, corresponding_eid_key in key_order:
            e_list_pools = node.event_items_dict[pool_eid_key]
            e_list_pools = flatten(e_list_pools)
            e_list_items = node.event_items_dict[corresponding_eid_key]

            item_pooled_in_pool_ix = dict()

            item_skip_list = []

            for pool_ix in range(len(e_list_pools)):
                pool_item = e_list_pools[pool_ix]
                for item in pool_item.pooled_event_items:
                    item_pooled_in_pool_ix[item.name] = pool_ix

            branch_pos = app_config.event_positions[corresponding_eid_key]

            if not is_flat(e_list_items):
                e_list_items = flatten(e_list_items)

            if not is_flat(e_list_pools):
                e_list_pools = flatten(e_list_pools)

            bottom_branch_offset, top_branch_offset = add_items_add_pools(app_config, bottom_branch_events,
                                                                          bottom_branch_offset, branch_pos,
                                                                          e_list_items,
                                                                          e_list_pools, item_pooled_in_pool_ix,
                                                                          item_skip_list, top_branch_events,
                                                                          top_branch_offset)

    else:
        bottom_branch_offset, top_branch_offset = add_items(app_config, bottom_branch_events, bottom_branch_offset,
                                                            node,
                                                            top_branch_events, top_branch_offset)

    top_branch_x = node.qnode.scenePos().x() - top_branch_offset - app_config.t_edge_linewidth
    top_branch_y = (node.qnode.scenePos().y() -
                    app_config.event_height -
                    app_config.t_edge_linewidth -
                    app_config.event_line_width)
    # adjust to center of qnode

    top_branch_x += node.qnode.sceneBoundingRect().width() / 2
    top_branch_y += node.qnode.sceneBoundingRect().height() / 2

    top_branch_events.setPos(top_branch_x, top_branch_y)

    bottom_branch_x = node.x - bottom_branch_offset - app_config.t_edge_linewidth
    bottom_branch_y = node.y + app_config.t_edge_linewidth + app_config.event_line_width
    # adjust to center of qnode
    bottom_branch_x += node.qnode.sceneBoundingRect().width() / 2
    bottom_branch_y += node.qnode.sceneBoundingRect().height() / 2
    bottom_branch_events.setPos(bottom_branch_x, bottom_branch_y)

    event_group.addToGroup(top_branch_events)
    event_group.addToGroup(bottom_branch_events)
    return event_group


class TreeScalingContainer(QObject):
    def __init__(self, tree_view_model: TreeViewNode, array_length: float, app_config: AppConfig):
        super().__init__()
        self.max_x = None
        self.swapped_nodes = []
        self.app_config = app_config

        self.tree_view_model = tree_view_model
        self.array_length = array_length
        self.min_distance = find_min_distance(self.tree_view_model)
        self.leaf_dist_ext_dict = get_leaf_dist_ext(self.tree_view_model, [], [])

        self.best_x_scale_factor = optimize_scaling(self.leaf_dist_ext_dict,
                                                    self.min_distance,
                                                    app_config,
                                                    self.array_length)
        self.x_scale_factor = self.best_x_scale_factor

        if self.min_distance == 0:
            min_above_zero = find_min_above_zero_distance(self.tree_view_model)
            self.min_scale = get_maximal_scaling_without_size_increase(self.leaf_dist_ext_dict,
                                                                       app_config.min_leaf_dist / min_above_zero)
        else:
            self.min_scale = get_maximal_scaling_without_size_increase(self.leaf_dist_ext_dict,
                                                                   app_config.min_leaf_dist / self.min_distance)

        self.max_y = None

    def redraw_c_swapped(self):
        for node in self.tree_view_model.traverse():
            node.x = 0
            node.y = 0
            if node.needs_switching:
                node.c = node.c[::-1]
                node.needs_switching = False
        self.preset_y("dynamic")
        set_x_positions(self.tree_view_model, self.app_config)
        switch_x_y(self.tree_view_model)
        self.tree_view_model.set_node_positions()

    def swap_child_node(self, swap_target: TreeViewNode, current_node=None):
        if current_node is None:
            return
        elif current_node == swap_target:
            current_node.c.reverse()
        else:
            for child in current_node.c:
                self.swap_child_node(swap_target, child)

    def preset_y(self, methode):
        if methode == "dynamic":
            self.max_y = preset_y_dynamic_vertical(self.tree_view_model, self.x_scale_factor, 0)

    def rescale_x(self, factor):
        self.x_scale_factor = self.x_scale_factor * factor
        self.max_x = reset_x_horizontal(self.tree_view_model, self.x_scale_factor, 0)

    def reset_scaling(self):
        self.x_scale_factor = self.best_x_scale_factor
        self.max_x = reset_x_horizontal(self.tree_view_model, self.x_scale_factor, 0)

    def set_scaling_min(self):
        self.x_scale_factor = self.min_scale
        self.max_x = reset_x_horizontal(self.tree_view_model, self.x_scale_factor, 0)


def find_min_distance(node: TreeViewNode, min_dist=float('inf')):
    for c in node.c:
        min_dist = min(min_dist, find_min_distance(c, c.distance))
    return min_dist

def find_min_above_zero_distance(node: TreeViewNode, min_dist=float('inf')):
    for c in node.c:
        if c.distance > 0:
            min_dist = min(min_dist, find_min_above_zero_distance(c, c.distance))
    return min_dist


def get_max_distance_sum(leaf_dist_ext_dict):
    max_dist_sum = 0
    for leaf, dist_ext_tpl in leaf_dist_ext_dict.items():
        curr_dist_sum = 0
        for ix in range(len(dist_ext_tpl[0])):
            curr_dist_sum += dist_ext_tpl[0][ix]
        max_dist_sum = max(max_dist_sum, curr_dist_sum)
    return max_dist_sum


def get_max_extension_sum(leaf_dist_ext_dict):
    max_ext_sum = 0
    for leaf, dist_ext_tpl in leaf_dist_ext_dict.items():
        curr_ext_sum = 0
        for ix in range(len(dist_ext_tpl[0])):
            curr_ext_sum += dist_ext_tpl[1][ix]
        max_ext_sum = max(max_ext_sum, curr_ext_sum)
    return max_ext_sum


def optimize_scaling(leaf_dist_ext_dict, min_dist, app_config: AppConfig, array_length):
    min_tree_size = app_config.min_array_tree_ratio * array_length
    max_tree_size = app_config.max_array_tree_ratio * array_length
    optimal_tree_size = app_config.optimal_array_tree_ratio * array_length

    x_values = []
    tree_sizes = []
    extension_counts = []

    if min_dist == 0:
        x_start = 0
    else:
        x_start = app_config.min_leaf_dist / min_dist
    x_end = app_config.max_array_tree_ratio * array_length / get_max_distance_sum(leaf_dist_ext_dict)
    n_points = int(app_config.scaling_optimization_rounds / 2)
    x_grid = [x_start + i * (x_end - x_start) / (n_points - 1) for i in range(n_points)]

    for x in x_grid:
        curr_size, curr_e_count = evaluate_current_x(leaf_dist_ext_dict, x)

        x_values.append(x)
        tree_sizes.append(curr_size)
        extension_counts.append(curr_e_count)

    # find first x inside app_config.min_array_tree_ratio and last x inside app_config.max_array_tree_ratio
    x_start, x_end = find_new_x_range(x_values, tree_sizes, min_tree_size, max_tree_size)
    if x_start == x_end:  # if all trees are too large to be in the range
        best_x2 = get_minimal_scaling(leaf_dist_ext_dict)
        best_x = max(x_start, best_x2)
        best_x = get_maximal_scaling_without_size_increase(leaf_dist_ext_dict, best_x)
        # curr_size, curr_e_count = evaluate_current_x(leaf_dist_ext_dict, best_x)

        return best_x

    if x_start < 1:
        x_start = 1

    log_grid = [math.log2(x_start) + i * (math.log2(x_end) - math.log2(x_start)) /
                (int(app_config.scaling_optimization_rounds / 2) - 1) for i in
                range(int(app_config.scaling_optimization_rounds / 2))]
    x_grid = [2 ** x for x in log_grid]

    for x in x_grid:
        curr_size, curr_e_count = evaluate_current_x(leaf_dist_ext_dict, x)

        x_values.append(x)
        tree_sizes.append(curr_size)
        extension_counts.append(curr_e_count)

    # find x with the smallest extension count and best ratio
    best_x, best_size = find_best_x(x_values, tree_sizes, extension_counts, min_tree_size, max_tree_size,
                                    optimal_tree_size)

    # get maximal extension sum
    max_ext_sum = get_max_extension_sum(leaf_dist_ext_dict)

    if best_size == max_ext_sum:
        best_x2 = get_minimal_scaling(leaf_dist_ext_dict)
        if best_x < best_x2:
            best_x = best_x2

    best_x = get_maximal_scaling_without_size_increase(leaf_dist_ext_dict, best_x)

    return best_x


def get_maximal_scaling_without_size_increase(leaf_dist_ext_dict, prior_scale):
    # get current longest branch
    new_scale = prior_scale
    longest_branch = ""
    max_length = 0
    for leaf, dist_ext in leaf_dist_ext_dict.items():
        size, ecount = evaluate_current_x({leaf: leaf_dist_ext_dict[leaf]}, prior_scale)
        if size >= max_length:
            max_length = size
            longest_branch = leaf

    # if distance * prior_scale > extension scale increase not possible -> return prior scale
    for ix in range(1, len(leaf_dist_ext_dict[longest_branch][1])):
        if leaf_dist_ext_dict[longest_branch][0][ix] * prior_scale > leaf_dist_ext_dict[longest_branch][1][ix]:
            return prior_scale

    # check for each edge in max if extension possible without size increase
    if longest_branch == "":
        raise ValueError("No longest branch found")

    for ix in range(1, len(leaf_dist_ext_dict[longest_branch][1])):
        distance = leaf_dist_ext_dict[longest_branch][0][ix]
        extension = leaf_dist_ext_dict[longest_branch][1][ix]
        if distance == 0:
            continue
        curr_scale = extension / distance
        size, ecount = evaluate_current_x(leaf_dist_ext_dict, curr_scale)
        if size > max_length:
            continue
        else:
            if curr_scale > new_scale:
                new_scale = curr_scale
    return new_scale


def get_minimal_scaling(leaf_dist_ext_dict):
    min_x_scale = float('inf')
    for leaf, dist_ext_tpl in leaf_dist_ext_dict.items():
        for ix in range(1, len(dist_ext_tpl[0])):  # skip root distance
            distance = dist_ext_tpl[0][ix]
            extension = dist_ext_tpl[1][ix]
            # x * distance = extension
            if distance == 0:
                continue
            min_x_scale = min(min_x_scale, extension / distance)
    return min_x_scale


def find_best_x(x_values, tree_sizes, extension_counts, min_tree_size, max_tree_size, optimal_tree_size):
    interesting_ixs = []

    for ix in range(len(x_values)):
        if min_tree_size < tree_sizes[ix] < max_tree_size:
            interesting_ixs.append(ix)

    if len(interesting_ixs) == 0:
        for x in range(len(x_values)):
            print(f"x: {x_values[x]}, tree size: {tree_sizes[x]}")
        raise ValueError("No x scale factor in range found")

    subset_x_values = [x_values[ix] for ix in interesting_ixs]
    subset_t_sizes = [tree_sizes[ix] for ix in interesting_ixs]
    subset_e_counts = [extension_counts[ix] for ix in interesting_ixs]

    if len(subset_e_counts) > 3:
        sorted_indices = sorted(enumerate(subset_e_counts), key=lambda x: x[1])
        third_lowest_value = sorted_indices[2][1]  # get the third lowest value
        all_lowest_indices = [index for index, value in enumerate(subset_e_counts) if value <= third_lowest_value]
    else:
        all_lowest_indices = [index for index, value in enumerate(subset_e_counts)]

    closest_index, closest_value = min(enumerate(all_lowest_indices), key=lambda x: abs(x[1] - optimal_tree_size))

    best_x = subset_x_values[closest_index]
    best_size = subset_t_sizes[closest_index]

    return best_x, best_size


def find_new_x_range(x_values, tree_sizes, min_tree_size, max_tree_size):
    """ select new xstart xend based on the tree sizes
    xstart is the first factor producing trees of size min_tree_size,
    xend the first producing trees of size max_tree_size"""

    x_start = 0
    x_end = x_values[-1]
    for ix in range(len(x_values)):
        if tree_sizes[ix] >= min_tree_size:
            x_start = x_values[ix]
            break
    for ix in range(len(x_values)):
        if tree_sizes[ix] >= max_tree_size:
            x_end = x_values[ix]
            break
    return x_start, x_end


def evaluate_current_x(leaf_dist_ext_dict, x):
    all_leafes_max = 0
    extension_count = 0

    for leaf, dist_ext_tpl in leaf_dist_ext_dict.items():
        curr_leaf_max = 0
        for ix in range(len(dist_ext_tpl[0])):
            x_scaled_dist = x * dist_ext_tpl[0][ix]
            if dist_ext_tpl[1][ix] > x_scaled_dist:
                extension_count += 1
                curr_leaf_max += dist_ext_tpl[1][ix]
            else:
                curr_leaf_max += x_scaled_dist
        all_leafes_max = max(all_leafes_max, curr_leaf_max)

    return all_leafes_max, extension_count


def get_leaf_dist_ext(node, distances, extensions):
    """ Returns a dictionary of leaf names and a tuple of their distances and extensions as lists"""

    distances.append(node.distance)
    extensions.append(node.extension_length)

    # If it's a leaf, return its info
    if node.cs == 0:  # Assuming node.c is the children list
        return {node.name: (distances.copy(), extensions.copy())}

    leaf_dict = {}

    # Recursively gather info from children
    for child in node.c:
        leaf_dict.update(get_leaf_dist_ext(child, distances.copy(), extensions.copy()))

    return leaf_dict


def preset_y_dynamic_vertical(node: TreeViewNode, scale_factor, max_y):
    if node.parent is not None:
        node.non_extension_len = node.distance * scale_factor
        node.height = max(node.non_extension_len, node.extension_length)
        node.y = node.parent.y + node.height
    else:
        node.non_extension_len = node.distance * scale_factor
        node.height = max(node.non_extension_len, node.extension_length)
        node.y = node.height
    curr_max = max(max_y, node.y)
    for node in node.c:
        max_y = preset_y_dynamic_vertical(node, scale_factor, curr_max)
    return max_y


def reset_x_horizontal(node: TreeViewNode, scale_factor, max_x):
    node.non_extension_len = node.distance * scale_factor
    node.height = max(node.non_extension_len, node.extension_length)
    node.x = node.height
    if node.parent is not None:
        node.x += node.parent.x
    curr_max = max(max_x, node.x)
    for node in node.c:
        max_x = reset_x_horizontal(node, scale_factor, curr_max)
    return max_x


def calc_event_extension_h(node: TreeViewNode, app_config: AppConfig):
    if not app_config.event_pooling:
        height = non_pooled_ext(app_config, node)
    else:
        height = pooled_ext(app_config, node)
    return height


def count_items_pooled(nested_list):
    count_i, count_p = 0, 0

    for i in nested_list:
        if isinstance(i, list):
            res = count_items_pooled(i)
            count_i += res[0]
            count_p += res[1]
        else:
            count_i += 1
    return count_i, count_p


def count_pooled(lst):
    count_p, count_i = 0, 0
    if not is_flat(lst):
        for sub_lst in lst:
            ci, cp = count_pooled(sub_lst)
            count_p += cp
            count_i += ci
    else:
        if len(lst) < 3:
            return len(lst), 0
        s, ix = find_incremental_series(lst)
        count_p = len(s)
        count_i = 0
        s_set = flatten_to_set(s)
        for i in lst:
            if i not in s_set:
                count_i += 1
    return count_i, count_p


def flatten_to_set(nested_list):
    result = set()
    for item in nested_list:
        if isinstance(item, list):
            result.update(flatten_to_set(item))
        else:
            result.add(item)
    return result


def pooled_ext(app_config, node):
    height_below_branch = 0
    height_above_branch = 0
    events_exist_top_b = False
    events_exist_bottom_b = False
    for event, e_list in node.events.items():
        if (event == "duplications" or
                event == "contradictions" or
                event == "double_gains" or
                event == "independent_gains" or
                event == "reaquisitions" or
                event == "dups" or
                event == "rearrangements"):
            continue
        if app_config.event_positions[event] == "top-branch":
            ci, cp = count_pooled(e_list)
            height_above_branch += ci * app_config.event_width
            height_above_branch += cp * app_config.epool_width
            if count_items(e_list) > 0:
                events_exist_top_b = True
        elif app_config.event_positions[event] == "bottom-branch":
            ci, cp = count_pooled(e_list)
            height_below_branch += ci * app_config.event_width
            height_below_branch += cp * app_config.epool_width
            if count_items(e_list) > 0:
                events_exist_bottom_b = True
        else:
            raise ValueError("Invalid event position")
    if events_exist_top_b:
        height_above_branch += app_config.t_edge_linewidth * 2
    if events_exist_bottom_b:
        height_below_branch += app_config.t_edge_linewidth * 2
    height = max(height_below_branch, height_above_branch)
    return height


def non_pooled_ext(app_config, node):
    height_below_branch = 0
    height_above_branch = 0
    events_exist_top_b = False
    events_exist_bottom_b = False
    for event, e_list in node.events.items():
        if (event == "duplications" or
                event == "contradictions" or
                event == "double_gains" or
                event == "independent_gains" or
                event == "reaquisitions" or
                event == "dups" or
                event == "rearrangements"):
            continue
        if app_config.event_positions[event] == "top-branch":
            height_above_branch += count_items(e_list) * app_config.event_width
            if count_items(e_list) > 0:
                events_exist_top_b = True
        elif app_config.event_positions[event] == "bottom-branch":
            height_below_branch += count_items(e_list) * app_config.event_width
            if count_items(e_list) > 0:
                events_exist_bottom_b = True
        else:
            raise ValueError("Invalid event position")
    if events_exist_top_b:
        height_above_branch += app_config.t_edge_linewidth * 2
    if events_exist_bottom_b:
        height_below_branch += app_config.t_edge_linewidth * 2
    height = max(height_below_branch, height_above_branch)
    return height


def count_items(nested_list):
    count = 0
    for i in nested_list:
        if isinstance(i, list):
            count += count_items(i)
        else:
            count += 1
    return count


def singular_leaf_inserts(root: TreeNode):
    visited = set()
    leaf_sgl_inserts = {}

    for node in root.traverse():
        if not node.c:
            sg_events = [str(gain) for gain in node.events["gains"] if gain not in visited]
            leaf_sgl_inserts[node.name] = sg_events
        else:
            visited.update(event for events in node.events.values() for event in flatten(events))

    return leaf_sgl_inserts


def switch_x_y(root: TreeViewNode):
    for node in root.traverse_preorder():
        old_x = node.x
        old_y = node.y
        node.y = old_x
        node.x = old_y


def create_edges(root_node: TreeViewNode, app_config: AppConfig):
    edge_group = QGraphicsItemGroup()

    for node in root_node.traverse():
        adjusted_x = node.x + node.qnode.boundingRect().width() / 2
        adjusted_y = node.y + node.qnode.boundingRect().height() / 2

        if node.parent is None:
            if app_config.show_events and node.height > 0:
                line_p1 = QPointF(adjusted_x - node.height, adjusted_y)
                line_p2 = QPointF(adjusted_x, adjusted_y)
                line1 = QGraphicsLineItem(QLineF(line_p1, line_p2))
                line1.setPen(app_config.t_extension_edge_pen)
                edge_group.addToGroup(line1)
        else:
            adjusted_parent_x = node.parent.x + node.parent.qnode.boundingRect().width() / 2
            adjusted_parent_y = node.parent.y + node.parent.qnode.boundingRect().height() / 2
            # Draw a vertical line from the parent's y position to the child's y position
            line_ver = QGraphicsLineItem(QLineF(adjusted_parent_x, adjusted_parent_y, adjusted_parent_x, adjusted_y))
            line_ver.setPen(app_config.t_edge_pen)
            line_ver.setZValue(-2)
            edge_group.addToGroup(line_ver)

            if app_config.show_events:
                # events caused extension should be shown in dot style
                # ----....---- = line1, line2, line3
                non_extended_len = node.non_extension_len
                extension_len = node.extension_length

                if extension_len == 0:
                    line_hor = QGraphicsLineItem(QLineF(adjusted_parent_x, adjusted_y, adjusted_x, adjusted_y))
                    line_hor.setPen(app_config.t_edge_pen)
                    edge_group.addToGroup(line_hor)
                else:
                    draw_extended_h_line(app_config, edge_group, extension_len, node, non_extended_len)
            else:
                line_hor = QGraphicsLineItem(QLineF(adjusted_parent_x, adjusted_y, adjusted_x, adjusted_y))
                line_hor.setPen(app_config.t_edge_pen)
                line_hor.setZValue(-2)
                edge_group.addToGroup(line_hor)
    return edge_group


def draw_extended_h_line(app_config, edge_group, extension_len, node, non_extended_len):
    adjusted_x = node.x + node.qnode.boundingRect().width() / 2
    adjusted_y = node.y + node.qnode.boundingRect().height() / 2
    adjusted_parent_x = node.parent.x + node.parent.qnode.boundingRect().width() / 2

    if app_config.t_extension_pos == "center":
        len_l1_l3 = non_extended_len / 2
        line1_p1 = QPointF(adjusted_parent_x, adjusted_y)
        line1_p2 = QPointF(adjusted_parent_x + len_l1_l3, adjusted_y)
        line2_p1 = QPointF(adjusted_parent_x + len_l1_l3, adjusted_y)
        line2_p2 = QPointF(adjusted_parent_x + len_l1_l3 + extension_len, adjusted_y)
        line3_p1 = QPointF(adjusted_parent_x + len_l1_l3 + extension_len, adjusted_y)
        line3_p2 = QPointF(adjusted_x, adjusted_y)
        line1 = QGraphicsLineItem(QLineF(line1_p1, line1_p2))
        line2 = QGraphicsLineItem(QLineF(line2_p1, line2_p2))
        line3 = QGraphicsLineItem(QLineF(line3_p1, line3_p2))
        line1.setPen(app_config.t_edge_pen)
        line2.setPen(app_config.t_extension_edge_pen)
        line3.setPen(app_config.t_edge_pen)
        edge_group.addToGroup(line1)
        edge_group.addToGroup(line2)
        edge_group.addToGroup(line3)
    elif app_config.t_extension_pos == "node":

        line1_p1 = QPointF(adjusted_parent_x, adjusted_y)
        line1_p2 = QPointF(adjusted_parent_x + non_extended_len, adjusted_y)
        line2_p1 = QPointF(adjusted_parent_x + non_extended_len, adjusted_y)
        line2_p2 = QPointF(adjusted_x, adjusted_y)
        line1 = QGraphicsLineItem(QLineF(line1_p1, line1_p2))
        line2 = QGraphicsLineItem(QLineF(line2_p1, line2_p2))
        line1.setPen(app_config.t_edge_pen)
        line2.setPen(app_config.t_extension_edge_pen)
        edge_group.addToGroup(line1)
        edge_group.addToGroup(line2)
    else:
        raise ValueError("Invalid extension position")


def draw_tree(root: TreeNode, array_length, app_config: AppConfig):
    tree_nodes = []

    tree_view_model = TreeViewNode(root, tree_nodes, app_config)

    tree_container = TreeScalingContainer(tree_view_model, array_length, app_config)
    tree_container.preset_y("dynamic")

    set_x_positions(tree_container.tree_view_model, app_config)
    switch_x_y(tree_container.tree_view_model)

    tree_container.tree_view_model.set_node_positions()

    leaf_tags = tree_container.tree_view_model.produce_leaf_tags(app_config)
    event_group = None
    if app_config.show_tree_edges:
        edge_group = create_edges(tree_container.tree_view_model, app_config)
        event_group = tree_container.tree_view_model.group_and_position_events(app_config)
    else:
        edge_group = QGraphicsItemGroup()

    return tree_nodes, edge_group, event_group, leaf_tags, tree_container

import csv
import itertools
import math
import random

from PyQt6.QtCore import QObject, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QColor, QBrush, QPen, QLinearGradient, QFontMetrics, QFont
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem, QColorDialog

from model.helper_functions import num_to_display_str
from model.model_container import ModelContainer
from view.array_rendering.render_arrays import SpacerItem
from view.colors.color_schemes import (C_2, C_3, C_4, C_5, C_6, C_7, C_8, C_10, C_13, C_15, C_21, C_23, C_26, C_35,
                                       C_41, C_62, C_97, C_139, C_230, C_470, C_1232)
from view.legend.render_legend import GradientLegendItem, prod_arr_legend_items


class ColorMapGenerator:
    """Class for generating color maps."""
    def __init__(self, spacer_names=None):
        self.spacer_names = spacer_names
        self.color_pairs_iter = None
        self.color_mode = "random"
        self.color_map = {}

        self.single_color_mode = False
        self.current_n_element = 0

    def get_element_color(self, name):
        colors = self.color_map[name]
        pen_color = colors[0]
        brush_color = colors[1]
        return pen_color, brush_color

    def add_element(self, name):
        if self.color_mode == "random" and not self.single_color_mode:
            brush_color = produce_random_color()
            pen_color = produce_random_color()
            self.color_map[str(name)] = (brush_color, pen_color)
        elif self.color_mode == "random" and self.single_color_mode:
            brush_color = produce_random_color()
            pen_color = brush_color
            self.color_map[str(name)] = (brush_color, pen_color)

        elif self.color_mode == "schemewise" and not self.single_color_mode:
            color_tuple = next(self.color_pairs_iter, None)
            if color_tuple:
                brush_color, pen_color = color_tuple
            else:
                brush_color = produce_random_color()
                pen_color = produce_random_color()
            self.color_map[str(name)] = (brush_color, pen_color)

        elif self.color_mode == "schemewise" and self.single_color_mode:
            color_tuple = next(self.color_pairs_iter, None)
            if color_tuple:
                brush_color = color_tuple[0]
                pen_color = brush_color
            else:
                brush_color = produce_random_color()
                pen_color = brush_color
            self.color_map[str(name)] = (brush_color, pen_color)
        else:
            raise Exception("Unknown color mode")

    def get_15_unused_colors(self):
        if self.color_pairs_iter is None:
            return []
        colors = []
        for i in range(15):
            color_tuple = next(self.color_pairs_iter, None)
            if color_tuple:
                colors.append(color_tuple)
            else:
                break
        return colors

    def set_schema(self, n_array_elements, two_color_mode):
        self.current_n_element = n_array_elements

        scheme = self.select_scheme_by_size(n_array_elements, two_color_mode)

        q_colors = list(map(lambda x: QColor(x), scheme))
        random.seed(10)
        random.shuffle(q_colors)
        if not two_color_mode:
            self.single_color_mode = True

            if len(q_colors) < n_array_elements:
                print(f"Not enough colors in color scheme ({len(q_colors)}) to cover all {n_array_elements} spacers."
                      f" Using larger color scheme.")
                scheme = self.color_schemes["ColorPhrogzNetExtended"]
                q_colors = list(map(lambda x: QColor(x), scheme.color_list))
                random.shuffle(q_colors)
                if len(q_colors) < n_array_elements:
                    print(
                        f"Not enough colors in color scheme ({len(q_colors)}) to cover all {n_array_elements} spacers."
                        f" Using random colors for the not covered arrays.")

            color_pairs = list(zip(q_colors, q_colors))
            self.color_pairs_iter = iter(color_pairs)
            self.color_mode = "schemewise"
            return

        if not self.enough_combination_space(scheme, n_array_elements):
            print("Not enough combination space for this color scheme."
                  " Using random colors for the not covered arrays.")
            return

        colors_pairs = list(itertools.combinations(q_colors, 2))
        random.seed(10)
        random.shuffle(colors_pairs)
        self.color_pairs_iter = iter(colors_pairs)
        self.color_mode = "schemewise"

    def select_scheme_by_size(self, n_array_elements, two_color_mode):
        if two_color_mode:
            scheme = C_62
        elif n_array_elements > 470:
            scheme = C_1232
        elif n_array_elements > 230:
            scheme = C_470
        elif n_array_elements > 139:
            scheme = C_230
        elif n_array_elements > 97:
            scheme = C_139
        elif n_array_elements > 62:
            scheme = C_97
        elif n_array_elements > 41:
            scheme = C_62
        elif n_array_elements > 35:
            scheme = C_41
        elif n_array_elements > 26:
            scheme = C_35
        elif n_array_elements > 23:
            scheme = C_26
        elif n_array_elements > 21:
            scheme = C_23
        elif n_array_elements > 15:
            scheme = C_21
        elif n_array_elements > 13:
            scheme = C_15
        elif n_array_elements > 10:
            scheme = C_13
        elif n_array_elements > 8:
            scheme = C_10
        elif n_array_elements > 7:
            scheme = C_8
        elif n_array_elements > 6:
            scheme = C_7
        elif n_array_elements > 5:
            scheme = C_6
        elif n_array_elements > 4:
            scheme = C_5
        elif n_array_elements > 3:
            scheme = C_4
        elif n_array_elements > 2:
            scheme = C_3
        else:
            scheme = C_2
        return scheme

    def enough_combination_space(self, scheme, n_arrays):
        n = len(scheme)
        n_comb = math.comb(n, 2)
        return n_comb >= n_arrays


def produce_random_color():
    def r():
        return random.randint(0, 255)

    color = f'#{r():02X}{r():02X}{r():02X}'
    color = QColor(color)
    return color


class TreeSignalManager(QObject):
    switchNodeChildren = pyqtSignal(str, bool)
    redrawTree = pyqtSignal()
    show_inner_array = pyqtSignal(str)

    def __init__(self):
        super().__init__()


class ColorManager(QObject):
    """Class for managing color maps and highlighting of spacers and events."""
    updateItemColor = pyqtSignal(str)
    updateEventColorSplit = pyqtSignal(str)
    highlightEvent = pyqtSignal(str, object)
    highlightMode = pyqtSignal(bool)
    updateArrayLegend = pyqtSignal()

    def __init__(self, app_config, model: ModelContainer, two_color_mode):  # , legend_update_func):
        super().__init__()

        self.app_config = app_config
        self.model = model
        self.spacer_names = model.get_spacer_names()

        self.sp_names_items = {}

        # map_name:color_map (dict) -> sp_name: (pen_color, brush_color)
        self.color_maps = {}
        # map_name:groups (dict) -> group_name: [sp_names]
        self.cmaps_groups = {}
        # map_name:sp_names_in_groups (dict) -> sp_name: group_name
        self.cmaps_sp_names_in_groups = {}
        # map_name:single_color_mode (bool) to put event in right mode
        self.cmap_single_c = {}
        # map_name:legend_info (dict) -> map_name: (color_translation_type, categories:color or min_mid_max:val_col)
        self.cmap_legend_info = {}
        # map_name:array_legend_items (dict) -> map_name: [legend_items]
        self.cmap_legend_items = {}
        # map_name:unused_colors (dict) -> map_name: [unused_colors]
        self.cmap_unused_colors = {}

        self.cmap_previous_to_zoom = None

        # after that go back to initializing different color maps
        self.current_map_name = None
        if two_color_mode:
            self.set_color_map("two_color_mode")
        else:
            self.set_color_map("single_color_mode")

    def get_legend_items(self):
        if self.current_map_name not in self.cmap_legend_items.keys():
            self.prod_legend_items(self.current_map_name)
        return self.cmap_legend_items[self.current_map_name]

    def prod_legend_items(self, map_name):
        if map_name not in self.cmap_legend_info.keys():
            self.cmap_legend_items[map_name] = []
        else:
            self.cmap_legend_items[map_name] = prod_arr_legend_items(self.cmap_legend_info[map_name],
                                                                     self.app_config)
        return self.cmap_legend_items[map_name]

    def metadata_color_options(self):
        metadata_types = {}

        for sp in self.model.template.spacers:
            for cat, val in sp.metadata.items():
                if cat not in metadata_types:
                    if val is not None:
                        metadata_types[cat] = type(val)
                    else:
                        # If the value is None continue checking other spacers
                        for sp_check in self.model.template.spacers:
                            if sp_check.metadata[cat] is not None:
                                metadata_types[cat] = type(sp_check.metadata[cat])
                                break

        for cat, typ in metadata_types.items():
            groups_sp = {}
            sp_names_in_groups = {}
            if typ == float or typ == int:
                if cat == "sp_frequency":
                    new_map_name = "Value Range of Spacer Frequency"
                elif cat == "sp_d_frequency":
                    new_map_name = "Value Range of Spacer Frequency with Deletions"
                else:
                    new_map_name = f"Value Range of {cat}"
                # get_range
                min_val = 0
                max_val = math.inf

                new_color_map = {}
                temp_sp_values = {}

                for sp in self.model.template.spacers:
                    temp_sp_values[sp.name] = sp.metadata[cat]

                if cat not in ["sp_frequency", "sp_d_frequency"]:
                    min_val = min(temp_sp_values.values())
                    max_val = max(temp_sp_values.values())
                    mid_val = (min_val + max_val) / 2

                    def min_max_scaling(x):
                        if min_val == max_val:
                            return 0.5
                        return (x - min_val) / (max_val - min_val)

                    temp_sp_values = {k: min_max_scaling(v) for k, v in temp_sp_values.items()}
                    min_c = frequency_to_color(min_max_scaling(min_val))
                    max_c = frequency_to_color(min_max_scaling(max_val))
                else:
                    min_val = 0
                    max_val = 1
                    mid_val = 0.5
                    min_c = frequency_to_color(min_val)
                    max_c = frequency_to_color(max_val)

                legend_info = {'min': (min_val, min_c),
                               'mid': (mid_val, None),
                               'max': (max_val, max_c)}

                self.cmap_legend_info[new_map_name] = ("value_range", legend_info)

                # calculate value for spacer
                for key, value in temp_sp_values.items():
                    new_color = frequency_to_color(value)
                    new_color_map[key] = (new_color, new_color)
                # assign color map to color manager
                self.color_maps[new_map_name] = new_color_map
                self.cmap_single_c[new_map_name] = True
                if new_map_name == "Value Range of Spacer Frequency":
                    copy_name = "sp_frequency"
                    self.color_maps[copy_name] = new_color_map
                    self.cmap_single_c[copy_name] = True
                    self.cmap_legend_items[copy_name] = []
            if typ == list:
                new_map_name = f"Groups in {cat}"

                for sp in self.model.template.spacers:
                    key = ', '.join(sorted(sp.metadata[cat]))

                    if key not in groups_sp:
                        groups_sp[key] = []

                    groups_sp[key].append(sp.name)
                    sp_names_in_groups[sp.name] = key

                self.cmaps_groups[new_map_name] = groups_sp
                self.cmaps_sp_names_in_groups[new_map_name] = sp_names_in_groups
                group_names = list(groups_sp.keys())
                color_map_generator = ColorMapGenerator(group_names)
                color_map_generator.set_schema(len(group_names), False)
                for name in group_names:
                    color_map_generator.add_element(name)
                group_color_map = color_map_generator.color_map
                self.cmap_legend_info[new_map_name] = ("categorical", group_color_map)
                self.color_maps[new_map_name] = {}
                self.cmap_single_c[new_map_name] = True

                for sp_name, group_name in self.cmaps_sp_names_in_groups[new_map_name].items():
                    self.color_maps[new_map_name][sp_name] = group_color_map[group_name]

        options_liste = list(
            map_name for map_name in self.color_maps.keys() if map_name not in ["single_color_mode", "two_color_mode"])
        return options_liste

    def initialize_color_map(self, map_name, c_map_type=None):
        self.color_maps[map_name] = {}

        if map_name == "single_color_mode":
            color_map_generator = ColorMapGenerator(self.spacer_names)
            color_map_generator.set_schema(len(self.spacer_names), False)
            for name in self.spacer_names:
                color_map_generator.add_element(name)
            self.color_maps[map_name] = color_map_generator.color_map
            self.cmap_single_c[map_name] = True
        elif map_name == "two_color_mode":
            color_map_generator = ColorMapGenerator(self.spacer_names)
            color_map_generator.set_schema(len(self.spacer_names), True)
            for name in self.spacer_names:
                color_map_generator.add_element(name)
            self.color_maps[map_name] = color_map_generator.color_map
            self.cmap_single_c[map_name] = False
        else:
            print(f"Unknown color map type to initialize{c_map_type}")

        self.cmap_unused_colors[map_name] = color_map_generator.get_15_unused_colors()

    def register_item(self, item):
        """Register an item with a specific name."""
        name = item.name
        if name not in self.sp_names_items:
            self.sp_names_items[name] = []
        self.sp_names_items[name].append(item)
        self.updateItemColor.connect(item.c_update_by_manager)
        if type(item) is SpacerItem:
            if item.template:
                self.highlightEvent.connect(item.highlight_by_manager)
                self.highlightMode.connect(item.change_highlight_mode)
        # if item not spacer item type connect to updateEventColorSplit
        if type(item) is not SpacerItem:
            self.updateEventColorSplit.connect(item.csplit_update_by_manager)
            self.highlightEvent.connect(item.highlight_by_manager)
            self.highlightMode.connect(item.change_highlight_mode)
            # set to current color mode
            if self.cmap_single_c[self.current_map_name]:
                item.csplit_update_by_manager("single_color")

    def create_color_map(self, map_name):
        """Create a new color map."""
        if map_name not in self.color_maps:
            self.color_maps[map_name] = {}
            # If it's the first map, set it as the current one.
            if self.current_map_name is None:
                self.current_map_name = map_name

    def set_color_map(self, map_name, c_map_type=None):
        """Switch to a different color map and update all items' colors."""
        if map_name == "sp_frequency":
            self.cmap_previous_to_zoom = self.current_map_name
        self.current_map_name = map_name
        if map_name not in self.color_maps:
            self.initialize_color_map(map_name, c_map_type)

        if map_name == "sp_frequency":
            self.updateEventColorSplit.emit("single_color")
        elif self.cmap_single_c[map_name]:
            self.updateEventColorSplit.emit("single_color")
        else:
            self.updateEventColorSplit.emit(self.app_config.event_color_mode)

        self.updateItemColor.emit("all")
        self.updateArrayLegend.emit()

    def highlight_event(self, event_name, y_n_bool=None):
        self.highlightEvent.emit(event_name, y_n_bool)

    def set_highlight_blinking(self, blinking):
        self.highlightMode.emit(blinking)

    def pic_new_color(self, name, group_name):
        picker_1 = QColorDialog()
        color_1 = picker_1.getColor()
        if not color_1.isValid():
            print("Invalid color")
            return

        if not self.cmap_single_c[self.current_map_name]:
            picker_2 = QColorDialog()
            color_2 = picker_2.getColor()

            if not color_2.isValid():
                print("Invalid color")
                return
        else:
            color_2 = color_1

        self.assign_new_color(color_1, color_2, group_name, name)

    def assign_new_color(self, color_1, color_2, group_name, name):
        if group_name == "spacer":
            if self.current_map_name == "single_color_mode":
                self.color_maps[self.current_map_name][name] = (color_1, color_1)
                self.updateItemColor.emit(name)

            elif self.current_map_name == "two_color_mode":
                self.color_maps[self.current_map_name][name] = (color_1, color_2)
                self.updateItemColor.emit(name)

        else:
            for sp_name in self.cmaps_groups[self.current_map_name][group_name]:
                self.color_maps[self.current_map_name][sp_name] = (color_1, color_1)
            self.updateItemColor.emit("all")
            self.cmap_legend_info[self.current_map_name][1][group_name] = (color_1, color_1)
            self.cmap_legend_items[self.current_map_name] = prod_arr_legend_items(
                self.cmap_legend_info[self.current_map_name],
                self.app_config)
            self.updateArrayLegend.emit()

    def set_new_rand_color(self, name, group_name):
        """Set a new random color for the given name in the current color map and inform relevant items."""
        if self.current_map_name in self.cmap_unused_colors:
            if len(self.cmap_unused_colors[self.current_map_name]) > 0:
                color_1, color_2 = self.cmap_unused_colors[self.current_map_name].pop()
                self.assign_new_color(color_1, color_2, group_name, name)
                return
        color_1 = produce_random_color()
        color_2 = produce_random_color()
        self.assign_new_color(color_1, color_2, group_name, name)

    def get_new_col_info(self, item_name):
        """Fetch the color for the given name from the current color map."""
        if self.current_map_name.startswith("Groups in"):
            if item_name in self.cmaps_sp_names_in_groups[self.current_map_name]:
                cat_color_group = self.cmaps_sp_names_in_groups[self.current_map_name][item_name]
            else:
                raise Exception(f"Unknown color group for spacer {item_name}")
        else:
            cat_color_group = None

        colors = self.color_maps[self.current_map_name][item_name]
        pen_c = colors[0]
        brush_c = colors[1]
        return pen_c, brush_c, cat_color_group

    def save_curr_color_map(self, file_path):
        with open(file_path, 'w') as file:
            writer = csv.writer(file)

            # write header
            writer.writerow(['# Spacer | Main Color | Auxillary Outer Color (optional)'])
            writer.writerow(['color_map_name', self.current_map_name, ''])

            for sp_name, colors in self.color_maps[self.current_map_name].items():
                pen_c = colors[0]
                brush_c = colors[1]
                writer.writerow([sp_name, pen_c.name(), brush_c.name()])

    def save_color_map_template(self, file_path):
        with open(file_path, 'w') as file:
            writer = csv.writer(file)

            # write header
            writer.writerow(
                ["# Spacer | Main Color (always set)| Auxillary Outer Color (optional - either set for all or none)"])
            writer.writerow(['# Add color_map_name in next line'])
            writer.writerow(['color_map_name', 'SET_NAME_HERE', ''])

            for sp_name, colors in self.color_maps[self.current_map_name].items():
                writer.writerow([sp_name, "", ""])

    def add_loaded_color_map(self, file_path):
        new_map = {}
        new_map_name = None
        is_single_color = False

        with open(file_path, 'r') as file:
            reader = csv.reader(file)

            for row in reader:
                if row[0].startswith("#"):
                    continue
                key = row[0]
                val1 = row[1]
                val2 = row[2]
                if key == "color_map_name":
                    new_map_name = val1
                else:
                    if val2 and not is_single_color:
                        if val1 == val2:
                            is_single_color = True
                            val1 = QColor(val1)
                            new_map[key] = (val1, val1)
                        else:
                            new_map[key] = (QColor(val1), QColor(val2))
                    else:
                        val1 = QColor(val1)
                        new_map[key] = (val1, val1)
                        is_single_color = True

        name_conter = 2
        while new_map_name in self.color_maps:
            new_map_name = f"{new_map_name}({name_conter})"
            name_conter += 1
        self.color_maps[new_map_name] = new_map

        self.cmap_single_c[new_map_name] = is_single_color

        return new_map_name


def frequency_to_color(frequency: float) -> QColor:
    hue = 240  # blue
    saturation = int(15 + frequency * 140)
    value = 255
    return QColor.fromHsv(hue, saturation, value)


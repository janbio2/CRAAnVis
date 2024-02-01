from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QFontMetrics, QLinearGradient
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsSimpleTextItem, \
    QGraphicsItem

from model.helper_functions import num_to_display_str
from view.tree_rendering.tree_events import TwoColorHexagonItem


class LegendsContainer:
    """Class to manage the tree and array legends"""
    def __init__(self, app_config, scene, start_y=None, start_t_x=None, end_t_x=None, start_a_x=None, end_a_x=None):
        self.app_config = app_config
        self.app_config.color_manager.updateArrayLegend.connect(self.update_array_legend)
        self.scene = scene

        self.y_gap = self.app_config.event_height + 5
        # adapt y to have some gap to tree and array
        self.start_y = start_y
        if self.start_y:
            self.start_y += self.y_gap
        self.start_x_t = start_t_x
        self.end_t_x = end_t_x
        self.start_x_a = start_a_x
        self.end_a_x = end_a_x
        self.x_overshoot = 0

        self.t_leg_items = {}
        self.a_leg_items = []

    def set_t_leg_items(self, items_dict):
        self.t_leg_items = items_dict

    def set_a_leg_items(self, items_dict):
        self.a_leg_items = items_dict

    def remove_legends_from_scene(self, which="all"):
        if which == "all":
            for item, text in self.t_leg_items.values():
                self.scene.removeItem(item)
            for item in self.a_leg_items:
                if isinstance(item, tuple):
                    self.scene.removeItem(item[0])
                else:
                    self.scene.removeItem(item)
                    self.scene.update()
        elif which == "tree":
            for item, text in self.t_leg_items.values():
                self.scene.removeItem(item)
        elif which == "array":
            for item in self.a_leg_items:
                if isinstance(item, tuple):
                    self.scene.removeItem(item[0])
                else:
                    self.scene.removeItem(item)
                    self.scene.update()

    def update_array_legend(self):
        self.remove_legends_from_scene("array")
        self.a_leg_items = self.app_config.color_manager.get_legend_items()
        self.layout_array_legend()

    def update_array_dimensions(self, start_x, end_x):
        if start_x != self.start_x_a or end_x != self.end_a_x:
            self.start_x_a = start_x
            self.end_a_x = end_x
            self.remove_legends_from_scene("array")
            self.layout_array_legend()

    def update_legend_dimensions(self, start_y, start_t_x, end_t_x, start_a_x, end_a_x):
        if start_y != self.start_y:
            self.set_dimensions(start_y, start_t_x, end_t_x, start_a_x, end_a_x)
            self.remove_legends_from_scene()
            self.layout_legends()
            return

        if start_t_x != self.start_x_t or end_t_x != self.end_t_x:
            self.start_x_t = start_t_x
            self.end_t_x = end_t_x
            self.remove_legends_from_scene("tree")
            self.layout_tree_legend()
        if start_a_x != self.start_x_a or end_a_x != self.end_a_x:
            self.start_x_a = start_a_x
            self.end_a_x = end_a_x

            self.remove_legends_from_scene("array")
            self.layout_array_legend()

    def set_dimensions(self, start_y, start_t_x, end_t_x, start_a_x, end_a_x):
        # adapting y to have some gap to tree and array
        self.start_y = start_y + self.y_gap
        self.start_x_t = start_t_x
        self.end_t_x = end_t_x
        self.start_x_a = start_a_x
        self.end_a_x = end_a_x

    def layout_legends(self):
        self.layout_tree_legend()
        self.layout_array_legend()

    def layout_array_legend(self):
        if len(self.a_leg_items) == 0:
            return
        if self.x_overshoot > 0:
            self.start_x_a += self.x_overshoot + self.app_config.legend_legend_margin

        curr_x = self.start_x_a
        curr_y = self.start_y
        x_gap_len = self.app_config.legend_legend_margin
        y_gap_len = x_gap_len * 3

        # check if line height is sufficient
        item_height = 0
        for item in self.a_leg_items:
            if isinstance(item, GradientLegendItem):
                item_height = max(item.boundingRect().height(), item_height)

        while item_height > y_gap_len:
            y_gap_len += x_gap_len

        # get total item len
        total_itm_len = 0
        for item in self.a_leg_items:
            if isinstance(item, GradientLegendItem):
                total_itm_len += item.boundingRect().width()
            elif isinstance(item, tuple):
                total_itm_len += self.get_tpl_len(item)
        n_items = len(self.a_leg_items) - 1
        if n_items > 0:
            total_itm_len += n_items * x_gap_len

        expected_line_wdth = total_itm_len / ((total_itm_len // (self.end_a_x - self.start_x_a)) + 1)

        curr_line_width = 0
        num_items_in_line = 0

        for item in self.a_leg_items:
            if isinstance(item, tuple):
                item_w = self.get_tpl_len(item)
                item = item[0]
            elif isinstance(item, GradientLegendItem):
                item_w = item.boundingRect().width()
            else:
                errormsg = f"Unknown item type in array legend: {type(item)}"
                raise ValueError(errormsg)

            curr_x, curr_y, curr_line_width, num_items_in_line = place_legend_item(self.scene, item, item_w,
                                                                                   self.start_x_a, x_gap_len, y_gap_len,
                                                                                   expected_line_wdth, curr_line_width,
                                                                                   curr_x, curr_y,
                                                                                   num_items_in_line)

    def get_tpl_len(self, tpl):
        return tpl[1].boundingRect().width() + tpl[0].boundingRect().width() + self.app_config.legend_item_margin

    def layout_tree_legend(self):

        if len(self.t_leg_items) == 0:
            return
        curr_x = self.start_x_t
        curr_y = self.start_y
        x_gap_len = self.app_config.legend_legend_margin
        y_gap_len = x_gap_len * 3

        item: QGraphicsItem
        text: QGraphicsItem
        total_itm_len = sum(
            text.boundingRect().width() + item.boundingRect().width() + self.app_config.legend_item_margin
            for item, text in self.t_leg_items.values())  # maybe adjust width measurement
        n_items = len(self.t_leg_items) - 1
        if n_items > 0:
            total_itm_len += n_items * x_gap_len
        expected_line_wdth = total_itm_len / ((total_itm_len // (self.end_t_x - self.start_x_t)) + 1)
        expected_line_wdth += self.app_config.legend_legend_margin

        curr_line_width = 0
        num_items_in_line = 0
        x_overshoot = 0

        for item_name, (item, text) in self.t_leg_items.items():
            item_w = text.boundingRect().width() + self.app_config.legend_item_margin + item.boundingRect().width()

            curr_x, curr_y, curr_line_width, num_items_in_line = place_legend_item(self.scene, item, item_w,
                                                                                   self.start_x_t, x_gap_len, y_gap_len,
                                                                                   expected_line_wdth, curr_line_width,
                                                                                   curr_x, curr_y,
                                                                                   num_items_in_line)

            if curr_x > self.start_x_a:
                x_overshoot = max(x_overshoot, curr_x - self.start_x_a)
            self.x_overshoot = x_overshoot


class GradientLegendItem(QGraphicsRectItem):
    """Class to display a gradient legend."""
    def __init__(self, x, y, width, height,
                 tick_width, tick_text_gap, min_texttext_gap,
                 color1, color2,
                 min_val, mid_val, max_val,
                 font):
        super().__init__(x, y, width, height)

        self.rect_height = height
        self.tick_width = tick_width
        self.tick_text_gap = tick_text_gap
        self.min_texttext_gap = min_texttext_gap
        self.tick_length = self.rect_height + self.rect_height / 5

        self.color_l = color1
        self.color_r = color2

        self.min_val = num_to_display_str(min_val)
        self.mid_val = num_to_display_str(mid_val)
        self.max_val = num_to_display_str(max_val)

        self.font = QFont(font)
        print(f"font size: {self.font.pointSize()}")
        font_metrics = QFontMetrics(self.font)

        min_dist_l = (font_metrics.horizontalAdvance(self.min_val) / 2 +
                      font_metrics.horizontalAdvance(self.mid_val) / 2 +
                      2 * self.min_texttext_gap)

        min_dist_r = (font_metrics.horizontalAdvance(self.mid_val) / 2 +
                      font_metrics.horizontalAdvance(self.max_val) / 2 +
                      2 * self.min_texttext_gap)

        self.min_length = max(min_dist_l, min_dist_r) * 2

        if self.rect().width() < self.min_length:
            self.prepareGeometryChange()
            self.setRect(self.rect().x(), self.rect().y(), self.min_length, self.rect().height())
            self.update()

        self.rect_top = self.rect().top()
        self.positions = [(self.rect().left(), self.min_val),
                          (self.rect().center().x(), self.mid_val),
                          (self.rect().right(), self.max_val)]
        for pos, text in self.positions:
            text = QGraphicsSimpleTextItem(text, parent=self)
            text.setFont(self.font)
            # center text under tick mark
            text.setPos(pos - text.boundingRect().width() / 2, self.rect_top + self.tick_length + self.tick_text_gap)

    def boundingRect(self):
        base_rect = super().boundingRect()
        # Calculate additional height required for the text and tick marks
        additional_height = self.rect_height - self.tick_length + self.tick_text_gap + QFontMetrics(self.font).height()
        # Return a new rectangle that includes space for the ticks and text
        return QRectF(base_rect.x(), base_rect.y(), base_rect.width(), base_rect.height() + additional_height)

    def paint(self, painter, option, widget=None):
        gradient = QLinearGradient(self.boundingRect().topLeft(), self.boundingRect().topRight())
        gradient.setColorAt(0, self.color_l)
        gradient.setColorAt(1, self.color_r)

        painter.setBrush(QBrush(gradient))
        pen = QPen(QColor('black'), self.tick_width)
        painter.setPen(pen)
        painter.drawRect(self.rect())

        # painter.setFont(self.font)
        for pos, _ in self.positions:
            painter.drawLine(QPointF(pos, self.rect_top), QPointF(pos, self.rect_top + self.tick_length))


def prod_arr_legend_items(arr_legend_info, app_config):
    legend_items = []

    if arr_legend_info[0] == "value_range":
        valname_val_color_dict = arr_legend_info[1]
        min_val = valname_val_color_dict["min"][0]
        mid_val = valname_val_color_dict["mid"][0]
        max_val = valname_val_color_dict["max"][0]
        color_l = valname_val_color_dict["min"][1]
        color_r = valname_val_color_dict["max"][1]
        legend_item = GradientLegendItem(0, 0,
                                         app_config.legend_item_width * 10, app_config.legend_item_height,
                                         3, 8, 10,
                                         color_l, color_r, min_val, mid_val, max_val, app_config.legend_font)
        legend_items.append(legend_item)

    elif arr_legend_info[0] == "categorical":
        cat_color_dict = arr_legend_info[1]

        for cat, colors in cat_color_dict.items():
            sp_dummy = QGraphicsRectItem(0, 0, app_config.legend_item_width, app_config.legend_item_height)
            sp_dummy.setBrush(QBrush(QColor(colors[0])))
            sp_dummy.setPen(QPen(QColor(colors[1])))

            text = QGraphicsSimpleTextItem(cat, parent=sp_dummy)
            text.setFont(app_config.legend_font)
            text.setPos(app_config.legend_item_width + app_config.legend_item_margin, 0)

            legend_items.append((sp_dummy, text))
    return legend_items


def place_legend_item(scene, item, item_w,
                      x_start, x_gap_len, y_gap_len,
                      expected_line_width, curr_line_width,
                      curr_x, curr_y,
                      num_items_in_line):
    if num_items_in_line == 0:
        # place item in line without gap
        curr_line_width = 0

    elif curr_line_width + x_gap_len + item_w <= expected_line_width:
        # place item in line with gap
        curr_x += x_gap_len
        curr_line_width += x_gap_len

    else:
        # place item in new line without gap
        curr_x = x_start  # self.start_x_t
        curr_y += y_gap_len
        curr_line_width = 0
        num_items_in_line = 0
    item.setPos(curr_x, curr_y)
    scene.addItem(item)
    curr_line_width += item_w
    curr_x += item_w
    num_items_in_line += 1
    return curr_x, curr_y, curr_line_width, num_items_in_line


def prod_tr_legend_items(app_config, itemtypes_in_tree):
    tree_legend_dict = {}

    legend_content = [
        ("Acquisitions", QGraphicsEllipseItem, "green"),
        ("Deletions", QGraphicsRectItem, "red"),
        ("Contradictions", TwoColorHexagonItem, "orange"),
        ("Duplications", TwoColorHexagonItem, "blue"),
        ("Rearrangements", TwoColorHexagonItem, "purple"),
        ("Reacquisition", TwoColorHexagonItem, "turquoise"),
        ("Ind. acquisition", TwoColorHexagonItem, "brown"),
        ("Other Type of Dup. Insertion", TwoColorHexagonItem, "gray")
    ]

    pos_x = 0
    pos_y = 0

    for legend_text, item_class, color in legend_content:
        if legend_text not in itemtypes_in_tree:
            continue
        if issubclass(item_class, TwoColorHexagonItem):
            item = item_class(" ",
                              0, 0, app_config.legend_item_width, app_config.legend_item_height,
                              app_config.event_font,
                              QColor("white"), QColor("white"), QColor(color))
        elif issubclass(item_class, QGraphicsEllipseItem):
            item = item_class(pos_x, pos_y, app_config.legend_item_width, app_config.legend_item_height)
            pen = QPen(QColor(color))
            pen.setWidth(2)
            item.setPen(pen)
            item.setBrush(QBrush(QColor("white")))
        elif issubclass(item_class, QGraphicsRectItem):
            item = item_class(0, 0, app_config.legend_item_width, app_config.legend_item_height)
            pen = QPen(QColor(color))
            pen.setWidth(2)
            item.setPen(pen)
            item.setBrush(QBrush(QColor("white")))
        else:
            item = item_class(0, 0, app_config.legend_item_width, app_config.legend_item_height)
            item.setPen(QPen(QColor(color)))
            item.setBrush(QBrush(QColor(color)))

        item.setPos(pos_x, pos_y)

        # set textitem
        text = QGraphicsSimpleTextItem(legend_text, parent=item)
        text.setFont(app_config.legend_font)
        text.setPos(pos_x + app_config.legend_item_width + app_config.legend_item_margin,
                    pos_y)

        tree_legend_dict[legend_text] = (item, text)

    return tree_legend_dict

from PyQt6.QtCore import QRectF, Qt, QSettings, QTimer
from PyQt6.QtGui import QColor, QPen, QFont, QPainter, QAction, QBrush
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QGraphicsItem, QGraphicsSimpleTextItem

from model.arrays import get_node_by_name, gather_upstream_gains, gather_upstream_losses
from model.helper_functions import adapt_font_to_width
from model.model_container import ModelContainer
from view.colors.highlighting import HighlightManagingMixin


class SpacerItem(HighlightManagingMixin, QGraphicsRectItem):
    """Class for visualizing a single spacer."""
    def __init__(self, app_config, model,
                 x, y, width, height,
                 font, brush_color, pen_color, pen_width=6,
                 original_names=False, color_group=None, template=False):
        QGraphicsRectItem.__init__(self, QRectF(x, y, width, height))
        HighlightManagingMixin.__init__(self)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.model = model
        self.original_names = original_names
        self.template = template
        self.app_config = app_config
        self.pen_color = pen_color
        self.brush_color = brush_color
        self.pen_width = pen_width
        self.highlighted = False

        # variables for color sync
        self.color_group = color_group

        if self.template:
            self.highlighted = False
            self.blink_state = False
            self.blink_timer = None
            self.blink_pen = None
            self.blink_brush = None

        if self.original_names:
            self.name = self.model.original_name
        else:
            self.name = self.model.name

        self.font = font
        self.font = adapt_font_to_width(self.font, str(self.name), width)
        self.text = QGraphicsSimpleTextItem(str(self.name), self)
        self.text.setFont(self.font)
        self.text.setPos(self.rect().center() - self.text.boundingRect().center())

        self.reg_brush = QBrush(QColor(brush_color))
        self.setBrush(self.reg_brush)
        self.reg_pen = QPen(QColor(pen_color), pen_width)
        self.reg_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.setPen(self.reg_pen)

        # register with color manager
        self.app_config.color_manager.register_item(self)

        # tooltip
        if self.original_names:
            tt_string = (f"Original Name {self.model.original_name}"
                         f"\nSpacer {self.model.name}")
        else:
            tt_string = (f"Spacer {self.model.name}"
                         f"\nOriginal Name {self.model.original_name}")
        if self.model.duplicates:
            if len(self.model.duplicates) == 1:
                tt_string += f"\nDuplicate {next(iter(self.model.duplicates))}"
            else:
                tt_string += f"\nDuplicates {', '.join(self.model.duplicates)}"
        if self.model.metadata:
            for key, value in self.model.metadata.items():
                tt_string += f"\n{key}: {value}"
        self.setToolTip(tt_string)

        # restorable position
        self.restorable_pos = None

    def store_pos(self):
        self.restorable_pos = self.pos()

    def restore_pos(self):
        if self.restorable_pos:
            self.setPos(self.restorable_pos)
            self.update()

    # Override contextMenuEvent to show custom context menu
    def contextMenuEvent(self, event):
        if self.original_names:
            return
        contextMenu = QMenu()

        newHighlightEventsAction = QAction("Highlight Spacer in Tree")
        contextMenu.addAction(newHighlightEventsAction)
        newHighlightEventsAction.triggered.connect(self.highlight_spacer_in_tree)

        # delete color printing in production:
        # printMyColorsAction = QAction("Print my Color")
        # printMyColorsAction.triggered.connect(self.print_my_colors)
        # contextMenu.addAction(printMyColorsAction)

        if self.color_group:
            newCatColorPicAction = QAction("Pick New Group Color")
            contextMenu.addAction(newCatColorPicAction)
            newCatColorPicAction.triggered.connect(self.change_cat_color)

            newCatColorAction = QAction("Set New Group Color Randomly")
            contextMenu.addAction(newCatColorAction)
            newCatColorAction.triggered.connect(self.change_cat_color_randomly)
        else:
            newColorAction = QAction("Pick New Spacer Color")
            contextMenu.addAction(newColorAction)
            newColorAction.triggered.connect(self.change_color)

            newRandomColorAction = QAction("Set New Spacer Color Randomly")
            contextMenu.addAction(newRandomColorAction)
            newRandomColorAction.triggered.connect(self.change_color_randomly)

        if self.model.duplicates:
            newHighlightDuplicatesAction = QAction("Highlight Duplicates")
            contextMenu.addAction(newHighlightDuplicatesAction)
            newHighlightDuplicatesAction.triggered.connect(self.highlight_duplicates)

        contextMenu.exec(event.screenPos())

    def print_my_colors(self):
        print(self.pen_color.name(), self.brush_color.name())

    def highlight_duplicates(self):
        for sp_name in self.model.duplicates:
            self.app_config.color_manager.highlight_event(sp_name)
        self.app_config.color_manager.highlight_event(self.name)

    def change_color_randomly(self):
        self.app_config.color_manager.set_new_rand_color(self.name, "spacer")

    def change_cat_color_randomly(self):
        self.app_config.color_manager.set_new_rand_color(self.name, self.color_group)

    def change_color(self):
        self.app_config.color_manager.pic_new_color(self.name, "spacer")

    def change_cat_color(self):
        self.app_config.color_manager.pic_new_color(self.name, self.color_group)

    def highlight_spacer_in_tree(self):
        self.app_config.color_manager.highlight_event(self.name)

    def c_update_by_manager(self, name):
        """Slot to handle color update from the manager."""
        if self.original_names:
            return

        if name == "all" or name == self.name:
            pen_color, brush_color, self.color_group = self.app_config.color_manager.get_new_col_info(self.name)
            self.reg_brush = QBrush(QColor(brush_color))
            self.reg_pen = QPen(QColor(pen_color), self.pen().width())
            self.reg_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            if self.highlighted:
                self.blink_pen = QPen(QColor(pen_color.red(),
                                             pen_color.green(),
                                             pen_color.blue(), 50), self.pen().width())
                self.blink_brush = QBrush(QColor(brush_color.red(), brush_color.green(), brush_color.blue(), 50))
                self.blink_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            self.setPen(self.reg_pen)
            self.setBrush(self.reg_brush)
            self.update()

    def start_highlight_static(self):
        self.setPen(self.highlight_pen)
        self.setBrush(self.highlight_brush)
        self.highlighted = True
        self.update()

    def end_highlight_static(self):
        self.setPen(self.reg_pen)
        self.setBrush(self.reg_brush)
        self.highlighted = False
        self.update()

    def start_blinking(self):
        self.blink_pen = QPen(QColor(self.pen_color.red(),
                                     self.pen_color.green(),
                                     self.pen_color.blue(), 50), self.pen_width)
        self.blink_brush = QBrush(QColor(self.brush_color.red(), self.brush_color.green(), self.brush_color.blue(), 50))
        self.blink_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.highlighted = True
        self.blink_state = True
        self.blink_timer = QTimer(self.parentObject())
        self.blink_timer.timeout.connect(self.toggle_opacity)
        self.blink_timer.start(350)

    def toggle_opacity(self):
        if self.blink_state and self.highlighted:
            self.setPen(self.blink_pen)
            self.setBrush(self.blink_brush)
            self.update()
        else:
            self.setPen(self.reg_pen)
            self.setBrush(self.reg_brush)
            self.update()
        self.blink_state = not self.blink_state

    def stop_blinking(self):
        self.highlighted = False
        self.blink_state = False
        self.setPen(self.reg_pen)
        self.setBrush(self.reg_brush)
        self.update()
        if hasattr(self, 'blink_timer'):
            if self.blink_timer is not None:
                self.blink_timer.stop()


class BrightDeletedSpacerItem(QGraphicsRectItem):
    """Class for visualizing a deleted single spacer."""
    def __init__(self, model, x, y, width, height, pen_width=1):
        super().__init__(QRectF(x, y, width, height))

        self.model = model
        self.setOpacity(0.9)

        self.brush().setStyle(Qt.BrushStyle.NoBrush)
        pen = QPen(Qt.GlobalColor.red, pen_width)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
        self.cross_pen = QPen(pen)

        # tooltip
        tt_string = (f"Deleted Spacer {self.model.name}"
                     f"\nOriginal Name {self.model.original_name}")
        for key, value in self.model.metadata.items():
            tt_string += f"\n{key}: {value}"
        self.setToolTip(tt_string)

        # restorable position
        self.restorable_pos = None

    def store_pos(self):
        self.restorable_pos = self.pos()

    def restore_pos(self):
        if self.restorable_pos:
            self.setPos(self.restorable_pos)
            self.update()

    def paint(self, painter: QPainter, option, widget):
        painter.setPen(self.pen())
        painter.drawRect(self.rect())

        # Draw the cross using the red pen
        painter.setPen(self.cross_pen)
        painter.drawLine(self.rect().topLeft(), self.rect().bottomRight())
        painter.drawLine(self.rect().topRight(), self.rect().bottomLeft())


def produce_inner_array(name, model, app_config, settings: QSettings):
    model: ModelContainer

    x_sp_margin = settings.value("margins/x_between_crispr_elements", type=float)
    width = settings.value("array/spacer_width", type=float)
    height = settings.value("array/spacer_height", type=float)
    font = app_config.spacer_font
    spc_pen_width = settings.value("array/spacer_pen_width", type=float)

    new_array = []

    # collect these values first
    node = get_node_by_name(model.tree, name)
    inserted_spacers = gather_upstream_gains(node, set())
    deleted_spacers = gather_upstream_losses(node, set())

    for spacer in model.template.spacers:
        x = spacer.index * x_sp_margin
        pen_color, brush_color, cat_color_group = app_config.color_manager.get_new_col_info(spacer.name)

        if spacer.name in inserted_spacers and spacer.name not in deleted_spacers:
            curr_sp_item = SpacerItem(app_config, spacer,
                                      x, 0, width, height,
                                      font, brush_color, pen_color, spc_pen_width,
                                      False, cat_color_group)
            new_array.append(curr_sp_item)
        elif spacer.name in deleted_spacers:
            del_item = BrightDeletedSpacerItem(spacer, x, 0, width, height)
            new_array.append(del_item)

    return new_array


def add_arrays_to_dict(model, app_config, settings: QSettings):
    model: ModelContainer

    x_sp_margin = settings.value("margins/x_between_crispr_elements", type=float)
    width = settings.value("array/spacer_width", type=float)
    height = settings.value("array/spacer_height", type=float)
    # Todo why settings not working here?
    font = app_config.spacer_font

    all_groups_dict = {}
    spc_pen_width = settings.value("array/spacer_pen_width", type=float)
    org_spc_pen_width = spc_pen_width - spc_pen_width / 5

    # add QGraphicGroups
    for array_name in model.arrays_dict.keys():
        all_groups_dict[array_name] = []

    all_groups_dict["template"] = []
    all_groups_dict["original_names"] = []

    # add items to groups
    for spacer in model.template.spacers:
        x = spacer.index * x_sp_margin
        pen_color, brush_color, cat_color_group = app_config.color_manager.get_new_col_info(spacer.name)
        grey = Qt.GlobalColor.gray
        # template
        template_sp_item = SpacerItem(app_config, spacer,
                                      x, 0, width, height,
                                      font, brush_color, pen_color, spc_pen_width,
                                      False, cat_color_group, template=True)
        all_groups_dict["template"].append(template_sp_item)

        # org_names
        org_sp_item = SpacerItem(app_config, spacer,
                                 x, 0, width, height,
                                 font, grey, grey, org_spc_pen_width,
                                 True, cat_color_group)
        all_groups_dict["original_names"].append(org_sp_item)

        # all others
        for array_name, array in model.arrays_dict.items():
            if array[spacer.index] == 1:
                sp_item = SpacerItem(app_config, spacer,
                                     x, 0, width, height,
                                     font, brush_color, pen_color, spc_pen_width,
                                     False, cat_color_group)
                all_groups_dict[array_name].append(sp_item)
            elif array[spacer.index] == "d":
                del_item = BrightDeletedSpacerItem(spacer, x, 0, width, height)
                all_groups_dict[array_name].append(del_item)
            else:
                continue

    return all_groups_dict

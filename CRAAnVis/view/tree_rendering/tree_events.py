from typing import Optional

from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import QPainterPath, QBrush, QPen, QColor, QFont, QPainter, QPolygonF
from PyQt6.QtWidgets import (QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsSimpleTextItem,
                             QStyleOptionGraphicsItem, QGraphicsPolygonItem, QWidget, QGraphicsItem)

from model.helper_functions import is_flat, find_incremental_series, adapt_font_to_width2
from view.colors.highlighting import HighlightManagingMixin


class EventEllipseItem(HighlightManagingMixin, QGraphicsEllipseItem):
    def __init__(self, app_config,
                 name: str, event_type: str,
                 x: float, y: float, width: float, height: float,
                 font: QFont,
                 color1: QColor, color2: QColor = None,
                 line_width=2,
                 color_mode='horizontal'):
        QGraphicsEllipseItem.__init__(self, QRectF(x, y, width, height))
        HighlightManagingMixin.__init__(self)

        self.color1 = color1
        self.color2 = color2 if color2 else color1
        self.brush1 = QBrush(QColor(self.color1))
        self.brush2 = QBrush(QColor(self.color2))

        self.app_config = app_config
        self.highlighted = False
        self.blink_state = False
        self.blink_timer = None
        self.blink_brush1 = QBrush(QColor(self.color1.red(), self.color1.green(), self.color1.blue(), 50))
        self.blink_brush2 = QBrush(QColor(self.color2.red(), self.color2.green(), self.color2.blue(), 50))

        self.line_color = QColor("green")
        self.line_width = line_width
        self.color_mode = color_mode

        self.name = str(name)
        self.event_type = event_type
        self.font = font
        self.font = adapt_font_to_width2(self.font, self.name, width - self.line_width)
        self.text = QGraphicsSimpleTextItem(str(self.name), self)
        self.text.setFont(self.font)
        self.text.setPos(self.rect().center() - self.text.boundingRect().center())

        # register for color sync
        self.color_group = None
        self.app_config.color_manager.register_item(self)

        # Tooltip
        tt_string = f"{self.event_type} of spacer {self.name}"
        self.setToolTip(tt_string)

    def change_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, "spacer")

    def change_cat_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, self.color_group)

    def c_update_by_manager(self, name):
        """Slot to handle color update from the manager."""
        if name == "all" or name == self.name:
            color1, color2, self.color_group = self.app_config.color_manager.get_new_col_info(self.name)
            self.set_colors(color1, color2)

    def csplit_update_by_manager(self, csplit):
        self.color_mode = csplit
        self.update()

    def toggle_opacity(self):
        if self.blink_state and self.highlighted:
            self.update()
        else:
            self.update()
        self.blink_state = not self.blink_state

    def start_highlight_static(self):
        self.highlighted = True
        self.update()

    def end_highlight_static(self):
        self.highlighted = False
        self.update()

    def set_colors(self, color1: QColor, color2: QColor):
        self.color1 = color1
        self.color2 = color2
        self.brush1 = QBrush(QColor(self.color1))
        self.brush2 = QBrush(QColor(self.color2))
        self.update()

    def set_color_mode(self, color_mode: str):
        self.color_mode = color_mode
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        painter.setPen(Qt.PenStyle.NoPen)

        if self.color_mode == 'horizontal':
            # Draw upper half
            upper_half = QPainterPath()
            upper_half.moveTo(self.rect().center())
            upper_half.arcTo(self.rect(), 0, 180)

            self.select_brush(painter, 1)
            painter.drawPath(upper_half)

            # Draw lower half
            lower_half = QPainterPath()
            lower_half.moveTo(self.rect().center())
            lower_half.arcTo(self.rect(), 180, 180)

            self.select_brush(painter, 2)
            painter.drawPath(lower_half)

        elif self.color_mode == 'inner_outer':
            self.select_brush(painter, 1)
            painter.drawEllipse(self.rect())

            # Draw inner ellipse
            offset = 3.5  # value determines the size of the inner ellipse
            inner_rect = QRectF(self.rect().x() + offset, self.rect().y() + offset,
                                self.rect().width() - 2 * offset, self.rect().height() - 2 * offset)

            self.select_brush(painter, 2)
            painter.drawEllipse(inner_rect)

        elif self.color_mode == 'single_color':
            self.select_brush(painter, 2)
            painter.drawEllipse(self.rect())

        # Draw full ellipse outline
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setColor(self.line_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(self.rect())


class EventRectItem(HighlightManagingMixin, QGraphicsRectItem):
    def __init__(self, app_config,
                 name: str, event_type: str,
                 x: float, y: float, width: float, height: float,
                 font: QFont,
                 color1: QColor, color2: QColor = None,
                 line_width=2,
                 color_mode='horizontal', frame=None):
        QGraphicsRectItem.__init__(self, QRectF(x, y, width, height))
        HighlightManagingMixin.__init__(self)

        self.color1 = color1
        self.color2 = color2 if color2 else color1
        self.brush1 = QBrush(QColor(self.color1))
        self.brush2 = QBrush(QColor(self.color2))

        self.app_config = app_config
        self.blink_state = False
        self.blink_timer = None
        self.blink_brush1 = QBrush(QColor(self.color1.red(), self.color1.green(), self.color1.blue(), 50))
        self.blink_brush2 = QBrush(QColor(self.color2.red(), self.color2.green(), self.color2.blue(), 50))

        self.frame = frame
        self.name = str(name)
        self.event_type = event_type

        self.line_color = QColor("white")
        self.line_width = line_width
        self.color_mode = color_mode

        self.font = font
        self.text = QGraphicsSimpleTextItem(str(name), self)
        self.font = adapt_font_to_width2(self.font, self.name, width - self.line_width)
        self.text.setFont(self.font)
        self.text.setPos(self.rect().center() - self.text.boundingRect().center())

        # Tooltip
        tt_string = f"{self.event_type} of spacer {self.name}"
        self.setToolTip(tt_string)

        # register for color sync
        self.color_group = None
        self.app_config.color_manager.register_item(self)
        self.highlighted = False

    def change_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, "spacer")

    def change_cat_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, self.color_group)

    def c_update_by_manager(self, name):
        """Slot to handle color update from the manager."""
        if name == "all" or name == self.name:
            color1, color2, self.color_group = self.app_config.color_manager.get_new_col_info(self.name)
            self.set_colors(color1, color2)

    def csplit_update_by_manager(self, csplit):
        """Slot to handle color update from the manager."""
        self.color_mode = csplit
        self.update()

    def toggle_opacity(self):
        if self.blink_state and self.highlighted:
            self.update()
        else:
            self.update()
        self.blink_state = not self.blink_state

    def set_colors(self, color1: QColor, color2: QColor):
        self.color1 = color1
        self.color2 = color2
        self.brush1 = QBrush(QColor(self.color1))
        self.brush2 = QBrush(QColor(self.color2))
        self.update()

    def start_highlight_static(self):
        self.highlighted = True
        self.update()

    def end_highlight_static(self):
        self.highlighted = False
        self.update()

    def set_color_mode(self, color_mode: str):
        self.color_mode = color_mode
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        painter.setPen(Qt.PenStyle.NoPen)

        if self.color_mode == 'horizontal':
            # Draw upper half
            upper_half = QPainterPath()
            upper_half.addRect(self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height() / 2)

            self.select_brush(painter, 1)

            painter.drawPath(upper_half)

            # Draw lower half
            lower_half = QPainterPath()
            lower_half.addRect(self.rect().x(), self.rect().y() + self.rect().height() / 2, self.rect().width(),
                               self.rect().height() / 2)

            self.select_brush(painter, 2)
            painter.drawPath(lower_half)

        elif self.color_mode == 'inner_outer':
            # Draw outer rectangle
            self.select_brush(painter, 1)
            painter.drawRect(self.rect())

            # Draw inner rectangle
            offset = 3.5  # value determines the size of the inner rectangle
            inner_rect = QRectF(self.rect().x() + offset, self.rect().y() + offset,
                                self.rect().width() - 2 * offset, self.rect().height() - 2 * offset)

            self.select_brush(painter, 2)
            painter.drawRect(inner_rect)

        elif self.color_mode == 'single_color':
            self.select_brush(painter, 2)
            painter.drawRect(self.rect())

        # Draw full rectangle outline
        pen = QPen(Qt.PenStyle.DotLine)
        pen.setColor(self.line_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())


class EventHexagonItem(HighlightManagingMixin,
                       QGraphicsPolygonItem):
    def __init__(self, app_config,
                 name: str, event_type: str,
                 x: float, y: float, width: float, height: float,
                 font: QFont,
                 line_color,
                 color1: QColor, color2: QColor = None,
                 line_width=2,
                 color_mode='horizontal'):
        QGraphicsPolygonItem.__init__(self)
        HighlightManagingMixin.__init__(self)

        self.color1 = color1
        self.color2 = color2 if color2 else color1
        self.brush1 = QBrush(QColor(self.color1))
        self.brush2 = QBrush(QColor(self.color2))

        self.app_config = app_config
        self.highlighted = False
        self.blink_state = False
        self.blink_timer = None
        self.blink_brush1 = QBrush(QColor(self.color1.red(), self.color1.green(), self.color1.blue(), 50))
        self.blink_brush2 = QBrush(QColor(self.color2.red(), self.color2.green(), self.color2.blue(), 50))

        self.line_color = line_color
        self.line_width = line_width
        self.color_mode = color_mode
        self.width = width
        self.height = height

        # text
        self.name = str(name)
        self.font = font
        self.font = adapt_font_to_width2(self.font, self.name, self.width - (self.line_width + 2))
        self.event_type = event_type
        self.text = QGraphicsSimpleTextItem(str(self.name), self)
        self.text.setFont(self.font)
        text_pos = QPointF(self.width / 2, height / 2)
        self.text.setPos(text_pos - self.text.boundingRect().center())

        h = height / 2
        w = width / 2
        self.hexagon = QPolygonF([
            QPointF(w * 1 / 2, 0),
            QPointF(w * 3 / 2, 0),
            QPointF(2 * w, h),
            QPointF(w * 3 / 2, 2 * h),
            QPointF(w * 1 / 2, 2 * h),
            QPointF(0, h)
        ])

        self.setPolygon(self.hexagon)
        self.setPos(x, y)

        # Tooltip
        tt_string = f"{self.event_type} of spacer {self.name}"
        self.setToolTip(tt_string)

        # register for color sync
        self.color_group = None
        self.app_config.color_manager.register_item(self)

    def change_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, "spacer")

    def change_cat_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, self.color_group)

    def c_update_by_manager(self, name):
        """Slot to handle color update from the manager."""
        if name == "all" or name == self.name:
            color1, color2, self.color_group = self.app_config.color_manager.get_new_col_info(self.name)
            self.set_colors(color1, color2)

    def csplit_update_by_manager(self, csplit):
        self.color_mode = csplit
        self.update()

    def start_highlight_static(self):
        self.highlighted = True
        self.update()

    def end_highlight_static(self):
        self.highlighted = False
        self.update()

    def toggle_opacity(self):
        if self.blink_state and self.highlighted:
            self.update()
        else:
            self.update()
        self.blink_state = not self.blink_state

    def set_colors(self, color1: QColor, color2: QColor):
        self.color1 = color1
        self.color2 = color2
        self.brush1 = QBrush(QColor(self.color1))
        self.brush2 = QBrush(QColor(self.color2))
        self.update()

    def set_color_mode(self, color_mode: str):
        self.color_mode = color_mode
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        painter.setPen(Qt.PenStyle.NoPen)

        if self.color_mode == 'horizontal':
            # Draw upper half
            self.select_brush(painter, 1)
            painter.drawPolygon(QPolygonF([self.hexagon[5], self.hexagon[0], self.hexagon[1], self.hexagon[2]]))

            # Draw lower half
            self.select_brush(painter, 2)
            painter.drawPolygon(self.hexagon[2:])

        elif self.color_mode == 'inner_outer':
            self.select_brush(painter, 1)
            painter.drawPolygon(self.polygon())

            # test
            offset_factor = 0.25  # size of the inner hexagon

            inner_hexagon = QPolygonF(
                [QPointF(point.x() * (1 - offset_factor) + self.hexagon.boundingRect().width() * offset_factor / 2,
                         point.y() * (1 - offset_factor) + self.hexagon.boundingRect().height() * offset_factor / 2)
                 for point in self.hexagon])

            self.select_brush(painter, 2)
            painter.drawPolygon(inner_hexagon)

        elif self.color_mode == 'single_color':

            self.select_brush(painter, 2)
            painter.drawPolygon(self.hexagon)

        # Draw full hexagon outline
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setColor(self.line_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(self.hexagon)


class FrameItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, names, color, line_width=1):
        super().__init__(x, y, width, height)
        self.names = names
        self.setPen(QPen(color))
        self.line_width = line_width
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        # Only draw the outline
        pen = QPen(self.color)
        pen.setWidth(self.line_width)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())


def draw_hsplit_brush_patches(painter, x, y, width, height, brush1, brush2):
    # draw top half
    upper_half = QPainterPath()
    upper_half.addRect(x, y, width, height / 2)
    painter.setBrush(brush1)
    painter.drawPath(upper_half)
    # Draw lower half
    lower_half = QPainterPath()
    lower_half.addRect(x, y + height / 2, width,
                       height / 2)
    painter.setBrush(brush2)
    painter.drawPath(lower_half)


def draw_io_brush_patches(painter, x, y, width, height, brush1, brush2):
    # Draw outer rectangle
    background_rect = QPainterPath()
    background_rect.addRect(x, y, width, height)
    painter.setBrush(brush1)
    painter.drawPath(background_rect)

    # Draw inner rectangle
    offset = 3.5  # size of the rect
    inner_rect = QRectF(x, y + offset,
                        width, height - 2 * offset)
    painter.setBrush(brush2)
    painter.drawRect(inner_rect)


def draw_sigle_c_brush_patches(painter, x, y, width, height, brush):
    background_rect = QRectF(x, y, width, height)
    painter.setBrush(brush)
    painter.drawRect(background_rect)


class EventPoolItem(QGraphicsItem):
    """parent class for pooling event classes.
    Holds the sigle event items and renders the middle part of the Pooled Items."""

    def __init__(self,
                 event_items: list, event_type: str,
                 x: float, y: float, width: float, height: float,
                 app_config,
                 pen_color: QColor):
        super().__init__()

        self.blinking_caused_by_name = None
        self.names = [event.name for event in event_items]

        self.app_config = app_config
        self.highlighted = False
        self.blink_state = False
        self.highlight_mode_blinking = True
        self.blink_timer = None
        self.blink_cols1 = []
        self.blink_cols2 = []
        self.blinking_caused_by_names = set()

        self.pooled_event_items = event_items
        self.name = str(self.pooled_event_items[0].name) + " - " + str(self.pooled_event_items[-1].name)
        self.event_type = event_type

        self.outer_event_w = app_config.epool_sides_width
        self.inner_event_width = (width - 2 * self.outer_event_w) / self.get_inner_length()
        self.height = height
        self.x = x
        self.y = y

        # texttag
        self.font = app_config.event_font
        self.font = adapt_font_to_width2(self.font, self.name, width)
        self.text = QGraphicsSimpleTextItem(str(self.name), self)
        self.text.setFont(self.font)
        text_pos = QPointF(width / 2, self.height / 2)
        self.text.setPos(text_pos - self.text.boundingRect().center())

        self.pen_color = pen_color
        self.line_width = app_config.epool_line_width
        self.color_mode = app_config.event_color_mode

        self.setToolTip(self.generate_tooltip(self.blinking_caused_by_names))

        # register for color sync
        self.color_group = None
        self.app_config.color_manager.register_item(self)

    def generate_tooltip(self, bold_names: set) -> str:
        header = "<html><head/><body>"
        footer = "</body></html>"
        tt_string = f"{self.event_type} of spacers:"
        for event in self.pooled_event_items:
            if str(event.name) in bold_names:
                tt_string += f"<br><b>{event.name}</b>"
            else:
                tt_string += f"<br>{event.name}"
        return header + tt_string + footer

    def change_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, "spacer")

    def change_cat_color(self):
        self.app_config.color_manager.set_new_rand_color(self.name, self.color_group)

    def c_update_by_manager(self, name):
        """Slot to handle color update from the manager."""
        if name == "all" or name in self.names:
            self.update()

    def csplit_update_by_manager(self, csplit):
        self.color_mode = csplit
        self.update()

    def highlight_by_manager(self, name, y_n_bool=None):
        if name in self.names:
            if y_n_bool is not None:
                if y_n_bool:
                    if len(self.blinking_caused_by_names) == 0:
                        self.blinking_caused_by_names.add(name)
                        self.start_highlight()
                    else:
                        self.blinking_caused_by_names.add(name)
                else:
                    if name in self.blinking_caused_by_names:
                        self.blinking_caused_by_names.remove(name)
                        if len(self.blinking_caused_by_names) == 0:
                            self.end_highlight()
            else:
                if name in self.blinking_caused_by_names:
                    self.blinking_caused_by_names.remove(name)
                    if len(self.blinking_caused_by_names) == 0:
                        self.end_highlight()
                else:
                    if len(self.blinking_caused_by_names) == 0:
                        self.blinking_caused_by_names.add(name)
                        self.start_highlight()
                    else:
                        self.blinking_caused_by_names.add(name)
            self.setToolTip(self.generate_tooltip(self.blinking_caused_by_names))

    def start_highlight(self):
        if self.highlight_mode_blinking:
            self.start_blinking()
        else:
            self.start_highlight_static()

    def end_highlight(self):
        if self.highlight_mode_blinking:
            self.stop_blinking()
        else:
            self.end_highlight_static()

    def change_highlight_mode(self, blinking: bool):
        if self.highlight_mode_blinking != blinking:
            self.highlight_mode_blinking = blinking
            if blinking:
                if self.highlighted:
                    self.end_highlight_static()
                    self.start_blinking()
            else:
                if self.highlighted:
                    self.stop_blinking()
                    self.start_highlight_static()

    def start_highlight_static(self):
        self.blink_state = True
        self.highlighted = True
        num_items = len(self.pooled_event_items)
        white_col = QColor(Qt.GlobalColor.white)
        self.blink_cols1 = [white_col for _ in range(num_items)]
        self.blink_cols2 = [white_col for _ in range(num_items)]
        self.update()

    def end_highlight_static(self):
        self.highlighted = False
        self.update()

    def start_blinking(self):
        self.highlighted = True
        self.blink_state = True
        self.blink_timer = QTimer(self.parentObject())
        self.blink_timer.timeout.connect(self.toggle_opacity)
        self.blink_timer.start(350)
        self.blink_cols1 = [QColor(event.color1.red(), event.color1.green(), event.color1.blue(), 50) for event in
                            self.pooled_event_items]
        self.blink_cols2 = [QColor(event.color2.red(), event.color2.green(), event.color2.blue(), 50) for event in
                            self.pooled_event_items]

    def toggle_opacity(self):
        if self.blink_state and self.highlighted:
            self.update()
        else:
            self.update()
        self.blink_state = not self.blink_state

    def stop_blinking(self):
        self.highlighted = False
        self.blinking_caused_by_name = None
        self.update()
        if hasattr(self, 'blink_timer'):
            self.blink_timer.stop()

    def boundingRect(self):
        width = self.inner_event_width * self.get_inner_length() + self.line_width + 2 * self.outer_event_w
        height = self.height + self.line_width
        return QRectF(self.x, self.y, width, height)

    def get_inner_length(self):
        if len(self.pooled_event_items) <= 2:
            return 0
        else:
            return len(self.pooled_event_items) - 2

    def get_right_end_x(self):
        return self.x + self.outer_event_w + self.inner_event_width * self.get_inner_length()

    def paint(self, painter, option, widget):
        x = self.x + self.outer_event_w
        y = 0
        for ix in range(len(self.pooled_event_items[1:-1])):
            if self.blink_state and self.highlighted:
                col1 = self.blink_cols1[ix + 1]
                col2 = self.blink_cols2[ix + 1]
            else:
                col1 = self.pooled_event_items[ix + 1].color1
                col2 = self.pooled_event_items[ix + 1].color2

            painter.setPen(Qt.PenStyle.NoPen)

            if self.color_mode == "horizontal":
                draw_hsplit_brush_patches(painter, x, y, self.inner_event_width, self.height, col1, col2)

            elif self.color_mode == "inner_outer":
                draw_io_brush_patches(painter, x, y, self.inner_event_width, self.height, col1, col2)

            elif self.color_mode == 'single_color':
                draw_sigle_c_brush_patches(painter, x, y, self.inner_event_width, self.height, col2)
            else:
                raise ValueError("Invalid color_mode value: " + self.color_mode)
            x += self.inner_event_width


class EllipsePoolItem(EventPoolItem):
    def __init__(self,
                 event_items: list, event_type: str,
                 x: float, y: float, width: float, height: float,
                 app_config,
                 pen_color: QColor):
        super().__init__(event_items, event_type, x, y, width, height, app_config, pen_color)

    def draw_arc_patch(self, painter, x, y,
                       width, height,
                       start_angle, end_angle,
                       brush, draw_inner=False, inner_brush=None):

        arc_point = QPointF(x + width, height / 2)
        arc_rect = QRectF(x, y, 2 * width, height)
        path = QPainterPath()
        path.moveTo(arc_point)
        path.arcTo(arc_rect, start_angle, end_angle)
        painter.setBrush(brush)
        painter.drawPath(path)
        if draw_inner:
            offset = 3.5  # size of the inner ellipse
            inner_rect = QRectF(x + self.outer_event_w / 2, y + offset,
                                width, height - 2 * offset)
            painter.setBrush(QBrush(inner_brush))
            painter.drawChord(inner_rect, 16 * start_angle, 16 * end_angle)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        x = self.x

        if self.blink_state and self.highlighted:
            brush1l = self.blink_cols1[0]
            brush2l = self.blink_cols2[0]
            brush1r = self.blink_cols1[-1]
            brush2r = self.blink_cols2[-1]
        else:
            brush1l = self.pooled_event_items[0].brush1
            brush2l = self.pooled_event_items[0].brush2
            brush1r = self.pooled_event_items[-1].brush1
            brush2r = self.pooled_event_items[-1].brush2

        if self.color_mode == "horizontal":
            # paint left half

            self.draw_arc_patch(painter, x, self.y,
                                self.outer_event_w, self.height,
                                90, 90,
                                brush1l)
            self.draw_arc_patch(painter, x, self.y,
                                self.outer_event_w, self.height,
                                180, 90,
                                brush2l)

            # paint right half
            x = self.get_right_end_x()

            self.draw_arc_patch(painter, x - self.outer_event_w, self.y,
                                self.outer_event_w, self.height,
                                0, 90,
                                brush1r)
            self.draw_arc_patch(painter, x - self.outer_event_w, self.y,
                                self.outer_event_w, self.height,
                                270, 90,
                                brush2r)

        elif self.color_mode == "inner_outer":
            # paint left half
            # draw bg
            self.draw_arc_patch(painter, x, self.y,
                                self.outer_event_w, self.height,
                                90, 180,
                                brush1l,
                                draw_inner=True,
                                inner_brush=brush2l)

            # paint right half
            x = self.get_right_end_x()
            # draw bg
            self.draw_arc_patch(painter, x - self.outer_event_w, self.y,
                                self.outer_event_w, self.height,
                                270, 180,
                                brush1r,
                                draw_inner=True,
                                inner_brush=brush2r)

        elif self.color_mode == 'single_color':
            # paint left half
            self.draw_arc_patch(painter, x, self.y,
                                self.outer_event_w, self.height,
                                90, 180,
                                brush2l)
            # paint right half
            x = self.get_right_end_x()
            self.draw_arc_patch(painter, x - self.outer_event_w, self.y,
                                self.outer_event_w, self.height,
                                270, 180,
                                brush2r)
        else:
            raise ValueError("Invalid color_mode value: " + self.color_mode)

        # draw outline
        pen = QPen(self.pen_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # draw left half ellipse
        left_rect = QRectF(self.x, self.y, 2 * self.outer_event_w, self.height)
        painter.drawArc(left_rect, 90 * 16, 180 * 16)

        r_x = self.get_right_end_x()

        # draw right half ellipse
        right_rect = QRectF(r_x - self.outer_event_w, self.y, 2 * self.outer_event_w, self.height)
        painter.drawArc(right_rect, -90 * 16, 180 * 16)

        # draw middle rectangle
        middle_rect = QRectF(self.x + self.outer_event_w, self.y,
                             self.get_inner_length() * self.inner_event_width, self.height)
        # draw top line
        painter.drawLine(middle_rect.topLeft(), middle_rect.topRight())
        # draw bottom line
        painter.drawLine(middle_rect.bottomLeft(), middle_rect.bottomRight())


class RectPoolItem(EventPoolItem):
    def __init__(self,
                 event_items: list, event_type,
                 x: float, y: float, width: float, height: float,
                 app_config,
                 pen_color: QColor):
        super().__init__(event_items, event_type, x, y, width, height, app_config, pen_color)

        self.outer_event_w = app_config.epool_width / (self.get_inner_length() + 2)
        self.inner_event_width = self.outer_event_w

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        x = self.x

        if self.blink_state and self.highlighted:
            brush1l = self.blink_cols1[0]
            brush2l = self.blink_cols2[0]
            brush1r = self.blink_cols1[-1]
            brush2r = self.blink_cols2[-1]
        else:
            brush1l = self.pooled_event_items[0].brush1
            brush2l = self.pooled_event_items[0].brush2
            brush1r = self.pooled_event_items[-1].brush1
            brush2r = self.pooled_event_items[-1].brush2

        if self.color_mode == "horizontal":
            # paint left end:
            draw_hsplit_brush_patches(painter, x, self.y,
                                      self.outer_event_w, self.height,
                                      brush1l, brush2l)
            # paint right end:
            x = self.get_right_end_x()
            draw_hsplit_brush_patches(painter, x, self.y,
                                      self.outer_event_w, self.height,
                                      brush1r, brush2r)

        elif self.color_mode == "inner_outer":
            # paint left half
            draw_io_brush_patches(painter, x, self.y,
                                  self.outer_event_w, self.height,
                                  brush1l, brush2l)

            x = self.get_right_end_x()
            draw_io_brush_patches(painter, x, self.y,
                                  self.outer_event_w, self.height,
                                  brush1r, brush2r)

        elif self.color_mode == 'single_color':
            # paint left half
            draw_sigle_c_brush_patches(painter, x, self.y,
                                       self.outer_event_w, self.height,
                                       brush2l)
            # paint right half
            x = self.get_right_end_x()
            draw_sigle_c_brush_patches(painter, x, self.y,
                                       self.outer_event_w, self.height,
                                       brush2r)

        else:
            raise ValueError("Invalid color_mode value: " + self.color_mode)

        # draw outline
        pen = QPen(self.pen_color)
        pen.setWidth(1)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(self.x, self.y,
                                2 * self.outer_event_w + self.get_inner_length() * self.inner_event_width,
                                self.height))


class HexagonPoolItem(EventPoolItem):
    def __init__(self,
                 event_items: list, event_type,
                 x: float, y: float, width: float, height: float,
                 app_config,
                 pen_color: QColor):
        super().__init__(event_items, event_type, x, y, width, height, app_config, pen_color)

        ############
        #   0__1   #
        #  5/  \2  #
        #   \__/   #
        #  4    3  #
        ############
        self.hexagon = [
            QPointF(self.outer_event_w * 1 / 2, 0),  # 0
            QPointF(self.outer_event_w * 3 / 2, 0),  # 1
            QPointF(2 * self.outer_event_w, self.height / 2),  # 2
            QPointF(self.outer_event_w * 3 / 2, self.height),  # 3
            QPointF(self.outer_event_w * 1 / 2, self.height),  # 4
            QPointF(0, self.height / 2)  # 5
        ]
        self.mid_01 = QPointF((self.hexagon[0].x() + self.hexagon[1].x()) / 2,
                              (self.hexagon[0].y() + self.hexagon[1].y()) / 2)
        self.mid_43 = QPointF((self.hexagon[3].x() + self.hexagon[4].x()) / 2,
                              (self.hexagon[3].y() + self.hexagon[4].y()) / 2)
        self.mid_52 = QPointF((self.hexagon[5].x() + self.hexagon[2].x()) / 2,
                              (self.hexagon[5].y() + self.hexagon[2].y()) / 2)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        def brush_draw_pt_polygon(pol_points, brush):
            patch = QPolygonF(pol_points)
            painter.setBrush(brush)
            painter.drawPolygon(patch)

        curr_pntl = QPointF(self.x, self.y)
        curr_pntr = QPointF(self.get_right_end_x() - self.outer_event_w, self.y)

        if self.blink_state and self.highlighted:
            brush1l = self.blink_cols1[0]
            brush2l = self.blink_cols2[0]
            brush1r = self.blink_cols1[-1]
            brush2r = self.blink_cols2[-1]
        else:
            brush1l = self.pooled_event_items[0].brush1
            brush2l = self.pooled_event_items[0].brush2
            brush1r = self.pooled_event_items[-1].brush1
            brush2r = self.pooled_event_items[-1].brush2

        if self.color_mode == "horizontal":
            # paint left half
            # paint upper half
            luh_points = [
                self.mid_01 + curr_pntl,
                self.mid_52 + curr_pntl,
                self.hexagon[5] + curr_pntl,
                self.hexagon[0] + curr_pntl
            ]
            brush_draw_pt_polygon(luh_points, brush1l)

            # paint lower half
            llh_points = [
                self.mid_52 + curr_pntl,
                self.mid_43 + curr_pntl,
                self.hexagon[4] + curr_pntl,
                self.hexagon[5] + curr_pntl
            ]
            brush_draw_pt_polygon(llh_points, brush2l)

            # paint right half
            # paint upper half
            ruh_points = [
                self.mid_01 + curr_pntr,
                self.hexagon[1] + curr_pntr,
                self.hexagon[2] + curr_pntr,
                self.mid_52 + curr_pntr
            ]
            brush_draw_pt_polygon(ruh_points, brush1r)

            # paint lower half
            rlh_points = [
                self.mid_52 + curr_pntr,
                self.hexagon[2] + curr_pntr,
                self.hexagon[3] + curr_pntr,
                self.mid_43 + curr_pntr
            ]
            brush_draw_pt_polygon(rlh_points, brush2r)

        elif self.color_mode == "inner_outer":
            offset_factor = 0.25  # size of the inner hexagon
            inner_hexagon = [
                QPointF(point.x() * (1 - offset_factor) + QPolygonF(
                    self.hexagon).boundingRect().width() * offset_factor / 2,
                        point.y() * (1 - offset_factor) + QPolygonF(
                            self.hexagon).boundingRect().height() * offset_factor / 2)
                for point in self.hexagon
            ]

            inner_mid_01 = QPointF((inner_hexagon[0].x() + inner_hexagon[1].x()) / 2,
                                   (inner_hexagon[0].y() + inner_hexagon[1].y()) / 2)
            inner_mid_43 = QPointF((inner_hexagon[3].x() + inner_hexagon[4].x()) / 2,
                                   (inner_hexagon[3].y() + inner_hexagon[4].y()) / 2)

            # paint left half
            # paint outer
            lho_points = [
                self.mid_01 + curr_pntl,
                self.mid_43 + curr_pntl,
                self.hexagon[4] + curr_pntl,
                self.hexagon[5] + curr_pntl,
                self.hexagon[0] + curr_pntl
            ]
            brush_draw_pt_polygon(lho_points, brush1l)
            # paint inner
            lhi_points = [
                inner_mid_01 + curr_pntl,
                inner_mid_43 + curr_pntl,
                inner_hexagon[4] + curr_pntl,
                inner_hexagon[5] + curr_pntl,
                inner_hexagon[0] + curr_pntl
            ]
            brush_draw_pt_polygon(lhi_points, brush2l)

            # paint right half
            # paint outer
            rho_points = [
                self.mid_01 + curr_pntr,
                self.hexagon[1] + curr_pntr,
                self.hexagon[2] + curr_pntr,
                self.hexagon[3] + curr_pntr,
                self.mid_43 + curr_pntr
            ]
            brush_draw_pt_polygon(rho_points, brush1r)
            # paint inner
            rhi_points = [
                inner_mid_01 + curr_pntr,
                inner_hexagon[1] + curr_pntr,
                inner_hexagon[2] + curr_pntr,
                inner_hexagon[3] + curr_pntr,
                inner_mid_43 + curr_pntr
            ]
            brush_draw_pt_polygon(rhi_points, brush2r)

        elif self.color_mode == 'single_color':
            # paint left half
            lh_points = [
                self.mid_01 + curr_pntl,
                self.mid_43 + curr_pntl,
                self.hexagon[4] + curr_pntl,
                self.hexagon[5] + curr_pntl,
                self.hexagon[0] + curr_pntl
            ]
            brush_draw_pt_polygon(lh_points, brush2l)

            # paint right half
            rh_points = [
                self.mid_01 + curr_pntr,
                self.hexagon[1] + curr_pntr,
                self.hexagon[2] + curr_pntr,
                self.hexagon[3] + curr_pntr,
                self.mid_43 + curr_pntr
            ]
            brush_draw_pt_polygon(rh_points, brush2r)
        else:
            raise ValueError("Invalid color_mode value: " + self.color_mode)

        # draw outline
        ol_points = [
            self.hexagon[0] + curr_pntl,
            self.hexagon[1] + curr_pntr,
            self.hexagon[2] + curr_pntr,
            self.hexagon[3] + curr_pntr,
            self.hexagon[4] + curr_pntl,
            self.hexagon[5] + curr_pntl
        ]
        pen = QPen(self.pen_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(QPolygonF(ol_points))


class TwoColorEllipseItem(QGraphicsEllipseItem):
    def __init__(self,
                 name: str,
                 x: float, y: float, width: float, height: float,
                 font: QFont,
                 color1: QColor, color2: QColor,
                 line_width=2):
        super().__init__(QRectF(x, y, width, height))
        self.color1 = color1
        self.color2 = color2
        self.line_color = QColor("green")
        self.line_width = line_width

        self.text = QGraphicsSimpleTextItem(str(name), self)
        self.text.setFont(font)
        self.text.setPos(self.rect().center() - self.text.boundingRect().center())

    def set_colors(self, color1: QColor, color2: QColor):
        self.color1 = color1
        self.color2 = color2
        self.update()

    def paint(self, painter, option, widget):
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw upper half
        upper_half = QPainterPath()
        upper_half.moveTo(self.rect().center())
        upper_half.arcTo(self.rect(), 0, 180)

        painter.setBrush(QBrush(QColor(self.color1)))
        painter.drawPath(upper_half)

        # Draw lower half
        lower_half = QPainterPath()
        lower_half.moveTo(self.rect().center())
        lower_half.arcTo(self.rect(), 180, 180)

        painter.setBrush(QBrush(QColor(self.color2)))
        painter.drawPath(lower_half)

        # Draw full ellipse outline
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setColor(self.line_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(self.rect())


def produce_event_items(event_list, event_type, app_config, events_dict):

    color_dict = app_config.event_color_dict
    name_dict = app_config.event_name_dict

    if event_type == "gains":
        event_items = produce_gain_items(event_list, app_config, events_dict)
    elif event_type == "losses":
        event_items = produce_loss_items(event_list, app_config)
    else:
        # if len(event_list) > 0:
        #     print(f" event_type: {event_type}")
        #     print(f" event_list: {event_list}")
        event_items = produce_other_items(event_list, app_config, name_dict[event_type], color_dict[event_type])

    return event_items


def produce_pooled_items(event_list, event_items, event_type, app_config, ix=None):

    color_dict = app_config.event_color_dict
    name_dict = app_config.event_name_dict
    if len(event_list) == 0:
        return []

    if ix is not None:
        event_list = event_list[ix]
        event_items = event_items[ix]

    pools, ixs = find_incremental_series(event_list)

    if len(event_items) == 1:
        if len(pools) > 0:
            # changing the code so this would not be necessary would be cool
            event_items = event_items[0]

    if len(pools) == 0:
        return []
    if len(event_items) == 0:
        return []

    if event_type == "gains":
        pool_items = produce_gain_pools(event_items, pools, ixs, app_config)
    elif event_type == "losses":
        pool_items = produce_loss_pools(event_items, pools, ixs, app_config)
    else:
        pool_items = produce_other_pools(event_items, pools, ixs, app_config, color_dict[event_type],
                                         name_dict[event_type])

    return pool_items


def produce_gain_items(event_list, app_config, events_dict):
    gain_items = []
    for sp_name in event_list:
        if sp_name in events_dict["duplications"]:
            continue
        if sp_name in events_dict["contradictions"]:
            continue
        if sp_name in events_dict["double_gains"]:
            continue
        if sp_name in events_dict["independent_gains"]:
            continue
        if sp_name in events_dict["reacquisitions"]:
            continue
        if sp_name in events_dict["dups"]:
            continue
        if sp_name in events_dict["rearrangements"]:
            continue
        col1, col2, color_group = app_config.color_manager.get_new_col_info(
            str(sp_name))
        gain_item = EventEllipseItem(app_config,
                                     sp_name, "Acquisition",
                                     0, 0, app_config.event_width, app_config.event_height,
                                     app_config.event_font,
                                     col1, col2,
                                     app_config.event_line_width,
                                     app_config.event_color_mode)
        gain_item.setZValue(1)
        gain_items.append(gain_item)

    return gain_items


def produce_gain_pools(event_items, pools, ixs, app_config):
    pool_items = []
    col = QColor("green")
    for i in range(len(pools)):
        curr_item_ixs = ixs[i]
        current_items = [event_items[ix] for ix in curr_item_ixs]
        pool_item = EllipsePoolItem(current_items, "Acquisition",
                                    0, 0, app_config.epool_width, app_config.event_height,
                                    app_config,
                                    col)
        pool_item.setZValue(1)
        pool_items.append(pool_item)

    return pool_items


def produce_loss_items(event_list, app_config):
    loss_items = []
    # produce frame
    frame = FrameItem(0, 0, app_config.event_width * len(event_list), app_config.event_height,
                      event_list, QColor("red"), 1)
    frame.setZValue(5)

    for sp_name in event_list:
        col1, col2, color_group = app_config.color_manager.get_new_col_info(str(sp_name))
        loss_item = EventRectItem(app_config,
                                  sp_name, "Loss",
                                  0, 0, app_config.event_width, app_config.event_height,
                                  app_config.event_font,
                                  col1, col2,
                                  1,
                                  app_config.event_color_mode,
                                  frame)
        loss_item.setZValue(1)
        loss_items.append(loss_item)

    return loss_items


def produce_loss_pools(event_items, pools, ixs, app_config):
    pool_items = []
    col = QColor("red")
    for i in range(len(pools)):
        curr_item_ixs = ixs[i]
        current_items = [event_items[ix] for ix in curr_item_ixs]
        pool_item = RectPoolItem(current_items, "Loss",
                                 0, 0, app_config.epool_width, app_config.event_height,
                                 app_config,
                                 col)
        pool_item.setZValue(1)
        pool_items.append(pool_item)
    return pool_items


def produce_other_items(event_list, app_config, e_type_name, e_type_color):
    pool_items = []
    for sp_name in event_list:
        col1, col2, color_group = app_config.color_manager.get_new_col_info(str(sp_name))
        other_item = EventHexagonItem(app_config,
                                      sp_name, e_type_name,
                                      0, 0, app_config.event_width, app_config.event_height,
                                      app_config.event_font,
                                      e_type_color,
                                      col1, col2,
                                      app_config.event_line_width,
                                      app_config.event_color_mode)
        other_item.setZValue(1)
        pool_items.append(other_item)
    return pool_items


def produce_other_pools(event_items, pools, ixs, app_config, color, event_type_name):
    pool_items = []
    for i in range(len(pools)):
        curr_item_ixs = ixs[i]
        current_items = [event_items[ix] for ix in curr_item_ixs]
        pool_item = HexagonPoolItem(current_items, event_type_name,
                                    0, 0, app_config.epool_width, app_config.event_height,
                                    app_config,
                                    color)
        pool_item.setZValue(1)
        pool_items.append(pool_item)
    return pool_items


def produce_events(events_dict, app_config):
    items_dict = {}

    for event_type in events_dict.keys():
        if event_type not in items_dict:
            items_dict[event_type] = []

    for event_type, event_list in events_dict.items():
        if is_flat(event_list):
            items = produce_event_items(event_list, event_type, app_config, events_dict)
            items_dict[event_type].append(items)

        else:
            for sub_list in event_list:
                items = produce_event_items(sub_list, event_type, app_config, events_dict)
                items_dict[event_type].append(items)

    if app_config.event_pooling:
        for event_type in events_dict.keys():
            pool_event_type = event_type + "_pools"
            if pool_event_type not in items_dict:
                items_dict[pool_event_type] = []

        for event_type, event_list in events_dict.items():
            e_items = items_dict[event_type]
            pool_event_type = event_type + "_pools"
            if is_flat(event_list):
                if event_type == "gains":
                    event_list = [event for event in event_list if event not in events_dict["duplications"] and
                                  event not in events_dict["contradictions"] and
                                  event not in events_dict["double_gains"]]
                pools = produce_pooled_items(event_list, e_items, event_type, app_config)
                items_dict[pool_event_type].append(pools)
            else:
                for ix in range(len(event_list)):
                    if event_type == "gains":
                        event_list = [event for event in event_list[ix] if event not in events_dict["duplications"] and
                                      event not in events_dict["contradictions"] and
                                      event not in events_dict["double_gains"]]
                    pools = produce_pooled_items(event_list, e_items, event_type, app_config, ix)
                    items_dict[pool_event_type].append(pools)

    return items_dict


class TwoColorRectItem(QGraphicsRectItem):
    def __init__(self,
                 name: str,
                 x: float, y: float, width: float, height: float,
                 font: QFont,
                 color1: QColor, color2: QColor,
                 line_width=2):
        super().__init__(QRectF(x, y, width, height))
        self.color1 = color1
        self.color2 = color2
        self.line_color = QColor("white")
        self.line_width = line_width

        self.text = QGraphicsSimpleTextItem(str(name), self)
        self.text.setFont(font)
        self.text.setPos(self.rect().center() - self.text.boundingRect().center())

    def set_colors(self, color1: QColor, color2: QColor):
        self.color1 = color1
        self.color2 = color2
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw upper half
        upper_half = QPainterPath()
        upper_half.addRect(self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height() / 2)

        painter.setBrush(QBrush(self.color1))
        painter.drawPath(upper_half)

        # Draw lower half
        lower_half = QPainterPath()
        lower_half.addRect(self.rect().x(), self.rect().y() + self.rect().height() / 2,
                           self.rect().width(), self.rect().height() / 2)

        painter.setBrush(QBrush(self.color2))
        painter.drawPath(lower_half)

        # draw full rectangle outline
        pen = QPen(Qt.PenStyle.DotLine)
        pen.setColor(self.line_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())


class TwoColorHexagonItem(QGraphicsPolygonItem):
    def __init__(self,
                 name: str,
                 x: float, y: float, width: float, height: float,
                 font: QFont,
                 color1: QColor, color2: QColor, line_color,
                 line_width=2):
        super().__init__()
        self.line_color = line_color
        self.line_width = line_width

        # text
        self.text = QGraphicsSimpleTextItem(str(name), self)
        self.text.setFont(font)
        text_pos = QPointF(width / 2, height / 2)
        self.text.setPos(text_pos - self.text.boundingRect().center())

        # points of the hexagon.
        self.hexagon = QPolygonF([
            QPointF(0, height / 2),
            QPointF(width / 4, 0),
            QPointF(width * 3 / 4, 0),
            QPointF(width, height / 2),
            QPointF(width * 3 / 4, height),
            QPointF(width / 4, height)
        ])

        self.setPolygon(self.hexagon)
        self.setPos(x, y)

        self.color1 = color1
        self.color2 = color2

    def paint(self, painter, option, widget):
        # Draw the first half of the hexagon with color1.
        painter.setBrush(QBrush(self.color1))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPolygon(self.hexagon[0:4])

        # Draw the second half of the hexagon with color2.
        painter.setBrush(QBrush(self.color2))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPolygon(QPolygonF([self.hexagon[5],
                                       self.hexagon[4],
                                       self.hexagon[3],
                                       self.hexagon[0]]))

        # draw the outline.
        painter.setPen(QPen(self.line_color, self.line_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(self.polygon())

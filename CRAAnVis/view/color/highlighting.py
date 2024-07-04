from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPen, QColor, QBrush


class HighlightManagingMixin:
    """Mixin to add highlighting functionality """
    def __init__(self):
        self.highlighted = False
        self.blink_state = False
        self.highlight_mode_blinking = True

        # higlight pen is black highlight brush is white
        self.highlight_pen = QPen(QColor(0, 0, 0))
        self.highlight_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.highlight_brush = QBrush(QColor(255, 255, 255))

    def change_highlight_mode(self, blinking: bool):
        # if highlighted
        if self.highlighted:
            self.end_highlight()
            self.highlight_mode_blinking = blinking
            self.start_highlight()
        else:
            self.highlight_mode_blinking = blinking

    def start_highlight_static(self):
        error_message = "start_highlight_static() not implemented for class: " + str(self.__class__)
        raise NotImplementedError(error_message)

    def end_highlight_static(self):
        error_message = "end_highlight_static() not implemented"
        raise NotImplementedError(error_message)

    def select_brush(self, painter, brush_nr):
        """Allows Tree Events to select the right brush depending on the highlight mode"""
        if self.highlighted:
            if self.highlight_mode_blinking:
                if self.blink_state:
                    if brush_nr == 1:
                        painter.setBrush(self.blink_brush1)
                    elif brush_nr == 2:
                        painter.setBrush(self.blink_brush2)
                else:
                    if brush_nr == 1:
                        painter.setBrush(self.brush1)
                    elif brush_nr == 2:
                        painter.setBrush(self.brush2)
            else:
                painter.setBrush(self.highlight_brush)
        else:
            if brush_nr == 1:
                painter.setBrush(self.brush1)
            elif brush_nr == 2:
                painter.setBrush(self.brush2)

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

    def highlight_by_manager(self, name, y_n_bool=None):
        if name == self.name:
            if y_n_bool is not None:
                if y_n_bool:
                    self.start_highlight()
                else:
                    if self.highlighted:
                        self.end_highlight()
            else:
                if self.highlighted:
                    self.end_highlight()
                else:
                    self.start_highlight()

    def start_blinking(self):
        self.blink_state = True
        self.blink_timer = QTimer(self.parentObject())
        self.blink_timer.timeout.connect(self.toggle_opacity)
        self.blink_timer.start(350)
        self.highlighted = True

    def stop_blinking(self):
        if hasattr(self, 'blink_timer'):
            if self.blink_timer is not None:
                self.blink_timer.stop()
            self.blink_timer.stop()
        self.highlighted = False
        self.blink_state = False
        self.update()

import os

from PyQt6.QtCore import QRectF, QSizeF, QMarginsF
from PyQt6.QtGui import QPainter, QPageSize, QPixmap, QColor
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QApplication, QFileDialog, QDialog, QVBoxLayout, QLineEdit, QLabel, \
    QPushButton, QGridLayout


def print_to_png(view, file_path=None, clipboard=False):
    # default resolution
    def_res = view.scene.sceneRect().size().toSize()
    res_x = def_res.width()
    res_y = def_res.height()

    if file_path:
        print("file_path:", file_path)
        file_name = view.app_config.file_name + ".png"
        file_path = os.path.join(file_path, file_name)

    elif not clipboard:
        # get resolution
        dlg = ResolutionPicker(res_x, res_y, view)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            res_x, res_y = dlg.get_res()
        else:
            return
        if res_x is None or res_y is None:
            return

        # get file path
        file_path = get_save_png_path(view)
        if file_path == ".png":
            return

    # setup view
    view.app_config.color_manager.set_highlight_blinking(False)

    # setup pixmap
    print("size:", view.scene.sceneRect().size().toSize())
    out_size = QSizeF(res_x, res_y)
    pixmap = QPixmap(out_size.toSize())
    pixmap.fill(QColor("white"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Render the scene with scene and target rectangles
    scene_rect = view.scene.sceneRect()
    target_rect = QRectF(0, 0, out_size.width(), out_size.height())
    view.scene.render(painter, target_rect, scene_rect)

    painter.end()
    if clipboard:
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        print("Copied to clipboard")
        return
    try:
        pixmap.save(file_path)
        print("Saved to", file_path)
    except FileNotFoundError:
        print(f"FileNotFoundError: {file_path}")
    view.app_config.color_manager.set_highlight_blinking(view.ui.actionBlinking_Highlights.isChecked())


class ResolutionPicker(QDialog):
    def __init__(self, def_x, def_y, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set PNG Resolution")
        layout = QVBoxLayout()
        res_layout = QGridLayout()

        self.x_input = QLineEdit(self)
        self.x_input.setText(str(def_x))
        self.x_label = QLabel("X:")
        self.y_input = QLineEdit(self)
        self.y_input.setText(str(def_y))
        self.y_label = QLabel("Y:")

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        res_layout.addWidget(self.x_label, 0, 0)
        res_layout.addWidget(self.x_input, 0, 1)
        res_layout.addWidget(self.y_label, 1, 0)
        res_layout.addWidget(self.y_input, 1, 1)

        layout.addLayout(res_layout)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_res(self):
        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
            return x, y
        except ValueError:
            return None, None


def print_to_pdf(view, file_path=None):
    if file_path == ".pdf":
        return
    if file_path:
        print("file_path:", file_path)
        file_name = view.app_config.file_name + ".pdf"
        file_path = os.path.join(file_path, file_name)
    elif file_path is None:
        file_path = get_save_pdf_path(view)

    # setup view
    view.app_config.color_manager.set_highlight_blinking(False)

    printer = QPrinter()
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(file_path)
    printer.setResolution(view.app_config.pdf_dpi)

    # Additional checks for printer setup
    if not printer.isValid():
        print("Printer setup is invalid.")
        return

    printer.setFullPage(False)

    bounding_rect = view.scene.itemsBoundingRect()
    page_width = view.app_config.pdf_width
    page_height = bounding_rect.height() * (page_width / bounding_rect.width())
    size_unit = QPageSize.Unit.Point
    page_size = QPageSize(QSizeF(page_width, page_height), size_unit)
    printer.setPageSize(page_size)
    page_margins = QMarginsF(0, 0, 0, 0)
    printer.setPageMargins(page_margins)

    painter = QPainter(printer)
    try:
        view.scene.render(painter)
        painter.end()
        print(f"PDF file saved to {file_path}")
    except FileNotFoundError:
        print(f"FileNotFoundError: {file_path}")
    view.app_config.color_manager.set_highlight_blinking(view.ui.actionBlinking_Highlights.isChecked())


def get_sp_placer_folder_path(parent):
    folder_path = QFileDialog.getExistingDirectory(
        parent=parent,
        caption="Select SpacerPlacer Experiment Folder"
    )
    return folder_path


def get_save_cmap_path(parent, caption):
    cmap_filter = "CSV Files (*.csv)"
    cmap_file_ext = ".csv"
    return get_save_file_path(parent, caption, cmap_filter, cmap_file_ext)


def get_save_png_path(parent):
    caption = "Save PNG"
    png_filter = "PNG Files (*.png)"
    png_file_ext = ".png"
    return get_save_file_path(parent, caption, png_filter, png_file_ext)


def get_save_pdf_path(parent):
    caption = "Save PDF"
    pdf_filter = "PDF Files (*.pdf)"
    pdf_file_ext = ".pdf"
    return get_save_file_path(parent, caption, pdf_filter, pdf_file_ext)


def get_save_file_path(parent, caption, filter, file_extension=""):
    file_path, _ = QFileDialog.getSaveFileName(
        parent=parent,
        caption=caption,
        filter=filter)
    if not file_path.endswith(file_extension):
        file_path += file_extension
    return file_path

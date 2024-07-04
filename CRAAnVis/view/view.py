import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QFileDialog, QStyle
from PyQt6.QtGui import QNativeGestureEvent, QTransform, QBrush, QKeySequence, QActionGroup, QColor
from PyQt6.QtCore import QSettings

from model.app_config import AppConfig, init_settings, store_current_settings, \
    restore_window_settings, restore_default_settings
from model.model_container import ModelContainer
from model.file_reader import read_all_folder_data
from view.exporting.exporting import print_to_pdf, print_to_png, get_sp_placer_folder_path, \
    get_save_cmap_path
from view.full_figure import Figure

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter

from view.ui.main_window_ui import Ui_MainWindow


class CrAAnVisView(QMainWindow, Ui_MainWindow):
    def __init__(self, app_config: AppConfig):
        super().__init__()

        self.app_config = app_config
        self.figure = Figure(self.app_config)
        self.showing_figure = False

        init_settings()

        self.settings = QSettings()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setWindowTitle(self.app_config.window_title)

        restore_window_settings(self)
        self.restore_check_items()
        self.setup_ui_connections()
        # self.app_config.tree_signal_manager.redrawTree.connect(self.redraw_children_switched)
        # self.app_config.tree_signal_manager.show_inner_array.connect(self.show_inner_array)

        self.crispr_element_colors = None
        self.item_groups = None
        self.tree_view_model = None

    def set_standard_window_geometry(self):
        x = self.app_config.window_width / self.scene.itemsBoundingRect().width()
        height = int(self.scene.itemsBoundingRect().height() * x)

        self.resize(self.app_config.window_width, height)
        self.view.resize(self.app_config.window_width, height)

    def show_gui(self):
        # load last file if available
        curr_file = self.settings.value("app/current_file")
        if curr_file is not None:
            self.load_new_data(self.settings.value("app/current_file"))
            #self.figure.produce_vis_from_model(self.model)

        # if no window size is saved, set standard window size
        if self.app_config.headless_mode or self.settings.value("window/geometry") is None:
            self.set_standard_window_geometry()

        # Todo: delete next line
        # QTimer.singleShot(0, self.fit_drawing_to_view)

        if not self.app_config.headless_mode:
            self.show()
        else:
            if "png" in self.app_config.headless_render_type:
                print_to_png(self, self.app_config.headless_output_folder_path)
            if "pdf" in self.app_config.headless_render_type:
                print_to_pdf(self, self.app_config.headless_output_folder_path)

    def keyPressEvent(self, event):
        zoomInFactor = self.app_config.zoom_factor
        zoomOutFactor = 1 / zoomInFactor

        if event.key() == Qt.Key.Key_Plus and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.set_zoom(zoomInFactor)
        elif event.key() == Qt.Key.Key_Minus and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.set_zoom(zoomOutFactor)
        super().keyPressEvent(event)

    def set_zoom(self, factor):
        min_zoom = 0.02
        max_zoom = 10
        current_zoom = self.view.transform().m11()
        zoom = current_zoom * factor
        if zoom < min_zoom:
            zoom = min_zoom
        elif zoom > max_zoom:
            zoom = max_zoom

        if self.showing_figure:
            if zoom < 0.2:
                if self.app_config.color_manager.current_map_name != "sp_frequency":
                    self.app_config.color_manager.set_color_map("sp_frequency")
            else:
                if self.app_config.color_manager.current_map_name == "sp_frequency":
                    self.app_config.color_manager.set_color_map(self.app_config.color_manager.cmap_previous_to_zoom)
        self.view.setTransform(QTransform.fromScale(zoom, zoom))

    def event(self, event):
        if isinstance(event, QNativeGestureEvent) and event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
            return self.zoomNativeEvent(event)
        return super().event(event)

    def zoomNativeEvent(self, event: QNativeGestureEvent):
        zoom_factor = 1 + event.value() / 1.0
        self.set_zoom(zoom_factor)
        return super().event(event)

    def zoom_in(self):
        zoom_factor = self.app_config.zoom_factor
        self.set_zoom(zoom_factor)

    def zoom_out(self):
        zoom_factor = self.app_config.zoom_factor
        self.set_zoom(1 / zoom_factor)

    def setup_ui_connections(self):
        self.ui.actionMinimize.triggered.connect(self.showMinimized)
        self.ui.actionZoom.triggered.connect(self.showMaximized)
        self.ui.actionZoom_In.triggered.connect(self.zoom_in)
        self.ui.actionZoom_Out.triggered.connect(self.zoom_out)

        # Colors
        self.ui.actionSingle_Color_Mode.toggled.connect(self.single_color_mode_toggled)
        self.ui.actionTwo_Color_Mode.toggled.connect(self.two_color_mode_toggled)
        self.ui.actionSplit_Event_Colors_Horizontal.toggled.connect(self.split_event_col_horizontal_toggled)
        self.ui.actionSplit_Event_Colors_InnerOuter.toggled.connect(self.split_event_col_inner_outer_toggled)
        self.ui.actionSave_Color_Map_Template_as_csv.triggered.connect(self.save_cmap_templ)
        self.ui.actionExport_Current_Color_Map_as_csv.triggered.connect(self.save_curr_cmap)

        self.ui.actionImport_Color_Map.triggered.connect(self.load_color_map)

        # coloring group sg two color mode
        self.ui.colorActionGroup = QActionGroup(self)
        self.ui.colorActionGroup.setExclusive(True)

        self.ui.colorActionGroup.addAction(self.ui.actionSingle_Color_Mode)
        self.ui.colorActionGroup.addAction(self.ui.actionTwo_Color_Mode)
        # coloring group two color split mode
        self.ui.colorSplitActionGroup = QActionGroup(self)
        self.ui.colorSplitActionGroup.setExclusive(True)
        self.ui.colorSplitActionGroup.addAction(self.ui.actionSplit_Event_Colors_Horizontal)
        self.ui.colorSplitActionGroup.addAction(self.ui.actionSplit_Event_Colors_InnerOuter)
        # highlight modes
        self.ui.highlightModeActionGroup = QActionGroup(self)
        self.ui.highlightModeActionGroup.setExclusive(True)
        self.ui.highlightModeActionGroup.addAction(self.ui.actionBlinking_Highlights)
        self.ui.highlightModeActionGroup.addAction(self.ui.actionStatic_Highlights)
        self.ui.actionBlinking_Highlights.setChecked(True)
        self.ui.actionBlinking_Highlights.triggered.connect(
            lambda checked: self.app_config.color_manager.set_highlight_blinking(checked))
        self.ui.actionStatic_Highlights.triggered.connect(
            lambda checked: self.app_config.color_manager.set_highlight_blinking(not checked))

        self.ui.menuColor_By_Metadata.setEnabled(False)

        # File
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionClear.triggered.connect(self.clear_toggled)
        self.update_open_recent_menu_actions(self.ui.menuOpen_Recent, self.settings.value("app/recent_files", []))
        openIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        self.ui.actionOpen_SpacerPlacer_Experiment.setIcon(openIcon)
        self.ui.actionOpen_SpacerPlacer_Experiment.triggered.connect(lambda: self.load_new_data(None))
        self.ui.actionOpen_SpacerPlacer_Experiment.setShortcut(QKeySequence.StandardKey.Open)
        self.ui.actionOpen_SpacerPlacer_Experiment.setEnabled(True)
        self.ui.actionExport_as_Pdf.triggered.connect(self.export_to_pdf_toggled)
        self.ui.actionExport_as_Png.triggered.connect(self.export_to_png_toggled)
        self.ui.actionCopy_Image.triggered.connect(self.copy_image_toggled)
        self.ui.actionCopy_Image.setShortcut(QKeySequence.StandardKey.Copy)

        # Tree
        self.ui.actionPool_Evolutionary_Events.triggered.connect(self.pool_event_toggled)
        self.ui.actionExtend_Tree_Length.triggered.connect(lambda: self.adjust_tree_size(1.05))
        self.ui.actionReduce_Tree_Length.triggered.connect(lambda: self.adjust_tree_size(0.95))
        self.ui.actionExtend_Tree_Length.setShortcut("Ctrl+T")
        self.ui.actionReduce_Tree_Length.setShortcut("Ctrl+Shift+T")

        self.ui.actionSet_Tiny_Tree_Scale.triggered.connect(lambda: self.adjust_tree_size(0, "tiny"))
        self.ui.actionReset_Tree_Scale.triggered.connect(lambda: self.adjust_tree_size(0, "reset"))

        # Arrays
        self.ui.actionShow_Template.toggled.connect(self.toggle_template_array_visibility)
        self.ui.actionShow_Original_Names.toggled.connect(self.toggle_original_names_visibility)
        self.ui.actionCollapse_Singular_Leaf_Acquisitions.setChecked(False)
        self.ui.actionCollapse_Singular_Leaf_Acquisitions.triggered.connect(
            lambda checked: self.collapse_singular_leaf_acquisitions(checked))
        self.ui.actionShow_Tags_for_Template_and_Org_Names.triggered.connect(
            lambda checked: self.set_tag_visibility(checked))
        self.ui.actionHighlight_Singular_Leaf_Acquisions.triggered.connect(
            lambda checked: self.highlight_singular_leaf_acquisitions(checked))
        self.ui.actionHighlight_Spacers_with_Duplicates.triggered.connect(
            lambda checked: self.highlight_spacers_with_duplicates(checked))

    def restore_check_items(self):

        if self.settings.value("colors/two_color_mode", type=bool):
            self.ui.actionTwo_Color_Mode.setChecked(True)
            self.ui.actionSingle_Color_Mode.setChecked(False)
            self.ui.actionSplit_Event_Colors_Horizontal.setEnabled(True)
            self.ui.actionSplit_Event_Colors_InnerOuter.setEnabled(True)
        else:
            self.ui.actionSingle_Color_Mode.setChecked(True)
            self.ui.actionTwo_Color_Mode.setChecked(False)
            self.ui.actionSplit_Event_Colors_Horizontal.setEnabled(False)
            self.ui.actionSplit_Event_Colors_InnerOuter.setEnabled(False)

        if self.settings.value("tree_events/color_split", type=str) == "horizontal":
            self.ui.actionSplit_Event_Colors_Horizontal.setChecked(True)
            self.ui.actionSplit_Event_Colors_InnerOuter.setChecked(False)
            if self.ui.actionTwo_Color_Mode.isChecked():
                self.app_config.event_color_mode = "horizontal"
        else:
            self.ui.actionSplit_Event_Colors_Horizontal.setChecked(False)
            self.ui.actionSplit_Event_Colors_InnerOuter.setChecked(True)
            if self.ui.actionTwo_Color_Mode.isChecked():
                self.app_config.event_color_mode = "inner_outer"

        if self.settings.value("tree_events/event_pooling", type=bool):
            self.ui.actionPool_Evolutionary_Events.setChecked(True)
        else:
            self.ui.actionPool_Evolutionary_Events.setChecked(False)

    def setup_ui_for_showing_visualisation(self):
        # Arrays
        self.ui.actionCollapse_Singular_Leaf_Acquisitions.setEnabled(True)
        self.ui.actionShow_Tags_for_Template_and_Org_Names.setEnabled(True)
        self.ui.actionCollapse_Singular_Leaf_Acquisitions.setChecked(False)

        # Colors
        self.ui.actionSingle_Color_Mode.setEnabled(True)
        self.ui.actionTwo_Color_Mode.setEnabled(True)
        if self.ui.actionTwo_Color_Mode.isChecked():
            self.ui.actionSplit_Event_Colors_Horizontal.setEnabled(True)
            self.ui.actionSplit_Event_Colors_InnerOuter.setEnabled(True)
        self.ui.actionSave_Color_Map_Template_as_csv.setEnabled(True)
        self.ui.actionExport_Current_Color_Map_as_csv.setEnabled(True)
        self.ui.actionImport_Color_Map.setEnabled(True)
        self.ui.menuColor_By_Metadata.setEnabled(True)

    def set_ui_vis_active(self):
        self.ui.actionExport_as_Pdf.setEnabled(True)
        self.ui.actionExport_as_Png.setEnabled(True)
        self.ui.actionCopy_Image.setEnabled(True)

        # Array Menu
        self.ui.actionShow_Original_Names.setEnabled(True)
        self.ui.actionShow_Template.setEnabled(True)
        self.ui.actionShow_Original_Names.setChecked(True)
        self.ui.actionShow_Template.setChecked(True)

        # Tree Menu
        self.ui.actionPool_Evolutionary_Events.setEnabled(True)
        self.ui.actionExtend_Tree_Length.setEnabled(True)
        self.ui.actionReduce_Tree_Length.setEnabled(True)

    def clear_toggled(self):
        self.scene.clear()
        self.setWindowTitle(self.app_config.window_title)
        self.ui.actionExport_as_Pdf.setEnabled(False)
        self.ui.actionExport_as_Png.setEnabled(False)
        self.ui.actionCopy_Image.setEnabled(False)

        # tree
        self.ui.actionPool_Evolutionary_Events.setEnabled(False)
        self.ui.actionExtend_Tree_Length.setEnabled(False)
        self.ui.actionReduce_Tree_Length.setEnabled(False)

        # arrays
        self.ui.actionShow_Template.setEnabled(False)
        self.ui.actionShow_Original_Names.setEnabled(False)
        self.ui.actionShow_Tags_for_Template_and_Org_Names.setEnabled(False)
        self.ui.actionCollapse_Singular_Leaf_Acquisitions.setEnabled(False)

        # colors
        self.ui.actionSingle_Color_Mode.setEnabled(False)
        self.ui.actionTwo_Color_Mode.setEnabled(False)
        self.ui.actionSplit_Event_Colors_Horizontal.setEnabled(False)
        self.ui.actionSplit_Event_Colors_InnerOuter.setEnabled(False)
        self.ui.actionSave_Color_Map_Template_as_csv.setEnabled(False)
        self.ui.actionExport_Current_Color_Map_as_csv.setEnabled(False)
        self.ui.actionImport_Color_Map.setEnabled(False)
        self.ui.menuColor_By_Metadata.setEnabled(False)

        print("Clearing scene.")

    def export_to_pdf_toggled(self):
        print_to_pdf(self)

    def export_to_png_toggled(self):
        print_to_png(self)  # , self.app_config.output_folder)

    def copy_image_toggled(self):
        print_to_png(self, None, clipboard=True)

    def pool_event_toggled(self, checked):
        if checked:
            self.settings.setValue("tree_events/event_pooling", True)
            self.show_redraw()
        else:
            self.settings.setValue("tree_events/event_pooling", False)
            self.show_redraw()

    def split_event_col_horizontal_toggled(self, checked):
        if checked:
            self.settings.setValue("tree_events/color_split", "horizontal")
            self.app_config.event_color_mode = "horizontal"
            self.app_config.color_manager.updateEventColorSplit.emit("horizontal")

    def split_event_col_inner_outer_toggled(self, checked):
        if checked:
            self.settings.setValue("tree_events/color_split", "inner_outer")
            self.app_config.event_color_mode = "inner_outer"
            self.app_config.color_manager.updateEventColorSplit.emit("inner_outer")

    def single_color_mode_toggled(self, checked):
        if checked:
            self.settings.setValue("colors/two_color_mode", False)
            self.app_config.event_color_mode = "single_color"
            self.app_config.color_manager.set_color_map("single_color_mode")
            self.app_config.color_manager.updateEventColorSplit.emit("single_color")

    def two_color_mode_toggled(self, checked):
        if checked:
            # enable split color menuitems
            self.ui.actionSplit_Event_Colors_Horizontal.setEnabled(True)
            self.ui.actionSplit_Event_Colors_InnerOuter.setEnabled(True)
            self.settings.setValue("colors/two_color_mode", True)
            split_mode = self.settings.value("tree_events/color_split", type=str)
            self.app_config.event_color_mode = split_mode
            self.app_config.color_manager.set_color_map("two_color_mode")
            self.app_config.color_manager.updateEventColorSplit.emit(split_mode)
        else:
            self.ui.actionSplit_Event_Colors_Horizontal.setEnabled(False)
            self.ui.actionSplit_Event_Colors_InnerOuter.setEnabled(False)

    def update_open_recent_menu_actions(self, menu, list_of_names):
        menu.clear()
        if len(list_of_names) > 0:
            menu.setEnabled(True)
        for name in list_of_names:
            action = QtGui.QAction(self)
            action.setObjectName(name)
            action.setText(name)
            action.triggered.connect(lambda checked=False, name=name: self.load_new_data(name))
            menu.addAction(action)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        store_current_settings(self)
        super().closeEvent(event)

    def fit_drawing_to_view(self):
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def load_new_data(self, folder_path=None):
        """Load data from folder path."""
        if folder_path is None:
            folder_path = get_sp_placer_folder_path(self)
        if not isinstance(folder_path, str):
            self.clear_toggled()
            return
        if not os.path.isdir(folder_path):
            self.clear_toggled()
            return
        recent_files = self.settings.value("app/recent_files")
        if folder_path in recent_files:
            if not recent_files[0] == folder_path:
                recent_files.remove(folder_path)
                recent_files.insert(0, folder_path)
        else:
            recent_files.insert(0, folder_path)
        if len(recent_files) > 50:
            recent_files.pop()
        self.settings.setValue("app/recent_files", recent_files)
        self.settings.setValue("app/current_file", folder_path)
        self.update_open_recent_menu_actions(self.ui.menuOpen_Recent, recent_files)
        self.setup_ui_for_showing_visualisation()

        file_name = folder_path.split("/")[-1]
        self.app_config.file_name = file_name
        self.setWindowTitle(self.app_config.window_title + " \"" + file_name + "\"")
        data = read_all_folder_data(folder_path)
        print(f"data: {data}")

        model = ModelContainer()
        model.load_data(data)

        self.figure.add_model(model)
        self.figure.setup_figure()

        # self.show_redraw()


    def update_color_by_metadata(self, menu, color_options):
        menu.clear()

        for color_option in color_options:
            if color_option.endswith("_groups"):
                color_option_text = color_option[:-7] + " by groups"
            elif color_option == "sp_frequency":
                continue
            else:
                color_option_text = color_option
            action = QtGui.QAction(self)
            action.setObjectName(color_option)
            action.setText(color_option_text)
            action.setCheckable(True)  # Make the action checkable

            # Connect the triggered signal to the desired function using a lambda function
            action.triggered.connect(
                lambda checked=False, co=color_option: self.app_config.color_manager.set_color_map(
                    co) if checked else None)

            menu.addAction(action)
            self.ui.colorActionGroup.addAction(action)  # Add the action to the group

    def save_cmap_templ(self):
        caption = "Select New Filename for Color Map Template .csv File"
        file_path = get_save_cmap_path(self, caption)
        self.app_config.color_manager.save_color_map_template(file_path)

    def save_curr_cmap(self):
        caption = "Select New Filename for Color Map .csv File"
        file_path = get_save_cmap_path(self, caption)
        self.app_config.color_manager.save_curr_color_map(file_path)

    def highlight_spacers_with_duplicates(self, checked):
        if checked:
            for sp in self.model.template.spacers:
                if sp.duplicates:
                    self.app_config.color_manager.highlight_event(sp.name, True)
                else:
                    self.app_config.color_manager.highlight_event(sp.name, False)
        else:
            spacer_names = self.model.get_spacer_names()
            for item in spacer_names:
                self.app_config.color_manager.highlight_event(item, False)

    def show_tags_for_template_and_org_names(self, checked):
        if checked:
            for tag in self.item_groups["template_org_name_tags"]:
                tag.setVisible(True)
        else:
            for tag in self.item_groups["template_org_name_tags"]:
                tag.setVisible(False)


    def load_color_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   caption="Load Color Map from .csv",
                                                   filter="CSV Files (*.csv)")
        if file_path:
            map_name = self.figure.add_loaded_color_map(file_path)
            self.ui.menuColor_By_Imported_Color_Map.setEnabled(True)
            for child in self.ui.menuColor_By_Imported_Color_Map.actions():
                if child.text() == map_name or child.text() == "None":
                    # remove old action
                    self.ui.menuColor_By_Imported_Color_Map.removeAction(child)
            action = QtGui.QAction(self)
            action.setObjectName(map_name)
            action.setText(map_name)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, mn=map_name: self.figure.color_manager.set_color_map(mn))
            self.ui.menuColor_By_Imported_Color_Map.addAction(action)
            self.ui.colorActionGroup.addAction(action)
            action.setChecked(True)
            self.app_config.color_manager.set_color_map(map_name)

        else:
            print("File open operation cancelled.")
        pass

    def toggle_template_array_visibility(self):
        if self.figure:
            self.figure.toggle_template_array_visibility()

    def toggle_original_names_visibility(self):
        if self.figure:
            self.figure.toggle_original_names_visibility()

import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsSimpleTextItem, \
    QGraphicsItemGroup, QGraphicsLineItem, QMainWindow, QFileDialog, QStyle
from PyQt6.QtGui import QNativeGestureEvent, QTransform, QBrush, QKeySequence, QActionGroup, QColor
from PyQt6.QtCore import QPointF, QTimer, QSettings, QLineF

from model.app_config import AppConfig, init_settings, store_current_settings, \
    restore_window_settings, restore_default_settings
from model.arrays import add_array_model
from model.model_container import ModelContainer
from model.file_reader import read_all_folder_data
from model.tree import produce_tree_model
from view.colors.colors import ColorManager
from view.array_rendering.render_arrays import add_arrays_to_dict, produce_inner_array
from view.exporting.exporting import print_to_pdf, print_to_png, get_sp_placer_folder_path, \
    get_save_cmap_path
from view.legend.render_legend import prod_tr_legend_items, LegendsContainer

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter

from view.tree_rendering.tree_view_model import draw_tree, create_edges
from view.ui.main_window_ui import Ui_MainWindow


class CrAAnVisView(QMainWindow, Ui_MainWindow):
    def __init__(self, app_config: AppConfig):
        super().__init__()

        self.model = None
        self.app_config = app_config
        init_settings()

        self.settings = QSettings()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        restore_window_settings(self)
        self.restore_check_items()
        self.setup_ui_connections()
        self.app_config.tree_signal_manager.redrawTree.connect(self.redraw_children_switched)
        self.app_config.tree_signal_manager.show_inner_array.connect(self.show_inner_array)

        self.crispr_element_colors = None
        self.item_groups = None
        self.tree_view_model = None

    def set_tag_visibility(self, checked):
        if checked:
            self.add_tags()
        else:
            self.delete_tags()

    def delete_tags(self):
        txt_templ = "Template of All Spacers:"
        txt_org = "Original Spacer Names:"

        if txt_templ in self.item_groups:
            self.scene.removeItem(self.item_groups[txt_templ])
            del (self.item_groups[txt_templ])
        if txt_org in self.item_groups:
            self.scene.removeItem(self.item_groups[txt_org])
            del (self.item_groups[txt_org])

    def reset_tags(self):
        self.delete_tags()
        self.add_tags()

    def add_tags(self):
        txt_templ = "Template of All Spacers:"
        txt_org = "Original Spacer Names:"

        if not self.ui.actionShow_Tags_for_Template_and_Org_Names.isChecked():
            return
        if self.item_groups["template"][0].isVisible():
            self.add_tag_if_visible(self.item_groups["template"][0], txt_templ)
        if self.item_groups["original_names"][0].isVisible():
            self.add_tag_if_visible(self.item_groups["original_names"][0], txt_org)

    def add_tag_if_visible(self, first_spacer, txt):
        tag = QGraphicsSimpleTextItem(txt)
        tag.setFont(self.app_config.t_leaf_tag_font)
        fs_center_y = first_spacer.sceneBoundingRect().center().y()
        fs_x = first_spacer.sceneBoundingRect().left()
        tag_y = fs_center_y - tag.boundingRect().center().y()
        tag_x = fs_x - tag.boundingRect().width() - self.app_config.array_to_tree_margin
        self.item_groups[txt] = tag
        self.scene.addItem(tag)
        tag.setPos(tag_x, tag_y)

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
        self.update_open_recent_menu_actions(self.ui.menuOpen_Recent, self.settings.value("app/recent_files"))
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

    def toggle_template_array_visibility(self, checked):
        if checked:
            for item in self.item_groups["template"]:
                item.setVisible(checked)
        else:
            for item in self.item_groups["template"]:
                item.setVisible(checked)
        self.reset_tags()

    def toggle_original_names_visibility(self, checked):
        if checked:
            # move template up
            h = self.item_groups["original_names"][0].boundingRect().height()
            for item in self.item_groups["template"]:
                item.moveBy(0, -h)
            for item in self.item_groups["original_names"]:
                item.setVisible(checked)
        else:
            # move template down
            h = self.item_groups["original_names"][0].boundingRect().height()
            for item in self.item_groups["template"]:
                item.moveBy(0, h)
        for item in self.item_groups["original_names"]:
            item.setVisible(checked)
        self.reset_tags()

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
        print(f"self model is {self.model}")
        print(f"self item groups are {self.item_groups}")

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

        self.model = ModelContainer()
        self.model.tree = produce_tree_model(data)
        self.model = add_array_model(data, self.model)

        self.show_redraw()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        store_current_settings(self)
        super().closeEvent(event)

    def show_inner_array(self, name):
        # produce array if not already done
        if name not in self.item_groups:
            self.item_groups[name] = produce_inner_array(name, self.model, self.app_config, self.settings)
            # produce tag and attach to array
            tag = QGraphicsSimpleTextItem(name)
            tag.setFont(self.app_config.t_leaf_tag_font)
            tag.setZValue(1)
            tag.setParentItem(self.item_groups[name][0])
            parent_center_y = self.item_groups[name][0].boundingRect().height() / 2
            tag_y = parent_center_y - tag.boundingRect().height() / 2
            tag_x = - tag.boundingRect().width() - self.app_config.array_to_tree_margin
            tag.setPos(tag_x, tag_y)

        # first clean up other inner arrays drawn
        for node in self.item_groups["tree_container"].tree_view_model.traverse():
            if node.qnode.brush().color() == Qt.GlobalColor.red:
                node.qnode.setBrush(self.app_config.t_node_color)
                # if item in scene remove
                if self.item_groups[node.name][0] in self.scene.items():
                    # move original names and template down
                    for item in self.item_groups["original_names"]:
                        item.moveBy(0, self.app_config.t_dummy_node_width)
                    for item in self.item_groups["template"]:
                        item.moveBy(0, self.app_config.t_dummy_node_width)
                    for sp in self.item_groups[node.name]:
                        self.scene.removeItem(sp)
                    self.scene.update()

                if name == node.name:
                    self.reset_tags()
                    return

        # get correct position
        # min_y = min(self.item_groups["original_names"][0].sceneBoundingRect().bottom(),
        #             self.item_groups["template"][0].sceneBoundingRect().bottom())
        # max_y = top of arrays
        min_y = 0
        array_names = self.model.get_array_names()
        for array_name in array_names:
            min_y = min(min_y, self.item_groups[array_name][0].sceneBoundingRect().top())
        min_y -= self.app_config.t_dummy_node_width - self.app_config.spacer_height

        x = self.item_groups["template"][0].sceneBoundingRect().left() + self.item_groups["template"][
            0].pen().width() / 2

        # then draw inner array
        for node in self.item_groups["tree_container"].tree_view_model.traverse():
            if node.name == name:
                node.qnode.setBrush(QBrush(Qt.GlobalColor.red))
                # if item not in scene add
                if self.item_groups[name][0] not in self.scene.items():
                    # move original names and template up
                    for item in self.item_groups["original_names"]:
                        item.moveBy(0, -self.app_config.t_dummy_node_width)
                    for item in self.item_groups["template"]:
                        item.moveBy(0, -self.app_config.t_dummy_node_width)
                    for sp in self.item_groups[name]:
                        sp.setPos(x, min_y)
                        self.scene.addItem(sp)
                    self.scene.update()
        self.reset_tags()

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

    def highlight_singular_leaf_acquisitions(self, checked):
        spacer_names = self.model.get_spacer_names()
        if checked:
            sgl_leaf_inserts = self.model.get_singular_leaf_inserts()
            sgl_leaf_inserts_set = set()
            for ins in sgl_leaf_inserts.values():
                for item in ins:
                    sgl_leaf_inserts_set.add(item)
            for item in spacer_names:
                if item in sgl_leaf_inserts_set:
                    self.app_config.color_manager.highlight_event(item, True)
                else:
                    self.app_config.color_manager.highlight_event(item, False)
        else:
            for item in spacer_names:
                self.app_config.color_manager.highlight_event(item, False)

    def show_tags_for_template_and_org_names(self, checked):
        if checked:
            for tag in self.item_groups["template_org_name_tags"]:
                tag.setVisible(True)
        else:
            for tag in self.item_groups["template_org_name_tags"]:
                tag.setVisible(False)

    def collapse_singular_leaf_acquisitions(self, checked):
        arrayname_sgl_ins = self.model.get_singular_leaf_inserts()
        singular_stretches = self.model.find_singular_stretches()
        (stretch_array_lenth, stretch_array_order,
         st_max_lenth, st_array_shift) = self.model.array_len_and_ordr_in_collapse_parts()

        # names of arrays to lookout for
        array_names = self.model.get_array_names()
        array_names.append("template")
        array_names.append("original_names")

        x_sp_margin = self.settings.value("margins/x_between_crispr_elements", type=float)

        if checked:
            self.ui.actionExtend_Tree_Length.setEnabled(False)
            self.ui.actionReduce_Tree_Length.setEnabled(False)
            text_addition = " (unavailable due to collapsed arrray parts)"
            text_extend = self.ui.actionExtend_Tree_Length.text() + text_addition
            text_reduce = self.ui.actionReduce_Tree_Length.text() + text_addition
            self.ui.actionExtend_Tree_Length.setText(text_extend)
            self.ui.actionReduce_Tree_Length.setText(text_reduce)

            for node in self.item_groups["tree_container"].tree_view_model.traverse():
                node.can_be_switched = False

            for stretch_ix, stretch in enumerate(singular_stretches):
                ixs_to_make_invisible = [ix for ix, _ in stretch]
                stretch = [sp_name for _, sp_name in stretch]
                last_ix = ixs_to_make_invisible[-1]
                # make stretch template invisable
                for sp in self.item_groups["template"]:
                    if sp.model.index in ixs_to_make_invisible:
                        sp.setVisible(False)
                for sp in self.item_groups["original_names"]:
                    if sp.model.index in ixs_to_make_invisible:
                        sp.setVisible(False)

                # order_arrayname_dict = {v: k for k, v in stretch_array_order[stretch_ix].items()}

                # move inserts to correct place
                non_stretch_shift = len(stretch) - st_max_lenth[stretch_ix]
                non_stretch_shift = non_stretch_shift * x_sp_margin

                # move arrays inside collapsing stretch to correct place
                for array_n in array_names:
                    # only consider arrays in current stretch
                    if array_n not in stretch_array_order[stretch_ix].keys():
                        continue

                    # shift arrays in stretch
                    shift = st_array_shift[stretch_ix][array_n] * x_sp_margin

                    for sp in self.item_groups[array_n]:
                        sp_name = str(sp.model.name)
                        if sp_name in stretch and sp_name in arrayname_sgl_ins[array_n]:
                            sp.moveBy(-shift, 0)

                for bgl in self.item_groups["array_background_lines"].childItems():
                    current_line = bgl.line()
                    new_end_x = current_line.x2() - non_stretch_shift
                    new_line = QLineF(current_line.x1(), current_line.y1(), new_end_x, current_line.y2())
                    bgl.setLine(new_line)

                for array_n in array_names:
                    for sp in self.item_groups[array_n]:
                        sp_name = str(sp.model.name)
                        sp_ix = sp.model.index
                        if sp_name not in stretch and sp_ix > last_ix:
                            sp.moveBy(-non_stretch_shift, 0)

        else:
            text_to_remove = " (unavailable due to collapsed arrray parts)"
            text_extend = self.ui.actionExtend_Tree_Length.text().replace(text_to_remove, "")
            text_reduce = self.ui.actionReduce_Tree_Length.text().replace(text_to_remove, "")
            self.ui.actionExtend_Tree_Length.setText(text_extend)
            self.ui.actionReduce_Tree_Length.setText(text_reduce)
            self.ui.actionReduce_Tree_Length.setEnabled(True)
            self.ui.actionExtend_Tree_Length.setEnabled(True)
            for node in self.item_groups["tree_container"].tree_view_model.traverse():
                node.can_be_switched = True
            for name in array_names:
                for sp in self.item_groups[name]:
                    sp.restore_pos()
                    if name == "template" or name == "original_names":
                        sp.setVisible(True)

            all_shifts = 0
            for stretch_ix, stretch in enumerate(singular_stretches):
                non_stretch_shift = len(stretch) - st_max_lenth[stretch_ix]
                non_stretch_shift = non_stretch_shift * x_sp_margin
                all_shifts += non_stretch_shift

            line_item = self.item_groups["array_background_lines"].childItems()[0]
            line = line_item.line()
            new_end_x = line.x2() + all_shifts
            for bgl in self.item_groups["array_background_lines"].childItems():
                current_line = bgl.line()
                new_line = QLineF(current_line.x1(), current_line.y1(), new_end_x, current_line.y2())
                bgl.setLine(new_line)

        if len(singular_stretches) > 0:
            a_legend_start_x = self.item_groups["legends"].start_x_a
            a_legend_end_x = new_end_x
            self.item_groups["legends"].update_array_dimensions(a_legend_start_x, a_legend_end_x)

    def redraw_children_switched(self):
        # delete old edges, bg_lines
        self.scene.removeItem(self.item_groups["edge_group"])
        old_obj = []
        for item in self.item_groups["events_group"].childItems():
            old_obj.append(item)
            self.scene.removeItem(item)
            self.item_groups["events_group"].removeFromGroup(item)
        self.scene.removeItem(self.item_groups["events_group"])
        for item in self.item_groups["array_background_lines"].childItems():
            self.scene.removeItem(item)
        self.item_groups["array_background_lines"] = QGraphicsItemGroup()

        tree_container = self.item_groups["tree_container"]
        tree_container.redraw_c_swapped()
        tree_container.tree_view_model.set_node_positions()
        # produce new edges
        self.item_groups["edge_group"] = create_edges(tree_container.tree_view_model, self.app_config)
        self.scene.addItem(self.item_groups["edge_group"])

        # adjust tree node offset
        for node_item in self.item_groups["tree_nodes"]:
            node_item.moveBy(0.5, 0.5)

        # reset tag positions
        tree_container.tree_view_model.update_leaf_tag_pos(self.item_groups["names_tags"], self.app_config)
        max_tag_x = 0
        for item in self.item_groups["names_tags"].values():
            max_tag_x = max(max_tag_x, item.sceneBoundingRect().right())
        array_pos_x = max_tag_x + self.app_config.array_to_tree_margin
        # # reallign arrays
        right_array_end_x = self.place_arrays_in_scene(array_pos_x, self.item_groups, self.item_groups["names_tags"],
                                                       add_to_scene=False)
        self.store_current_sp_positions()

        # # produce new bg_lines
        self.item_groups["array_background_lines"] = QGraphicsItemGroup()
        for name in self.item_groups["names_tags"].keys():
            bg_line = self.produce_bg_line_from_unaligned_tag(name, self.item_groups["names_tags"], right_array_end_x)
            self.item_groups["array_background_lines"].addToGroup(bg_line)
        self.item_groups["array_background_lines"].setZValue(-1)
        self.scene.addItem(self.item_groups["array_background_lines"])

        # # reallign tags
        self.right_allign_tags(array_pos_x)

        # update event positions
        self.item_groups["events_group"] = tree_container.tree_view_model.group_and_position_events(self.app_config)
        self.scene.addItem(self.item_groups["events_group"])

    def adjust_tree_size(self, factor, position=None):

        # delete old edges, bg_lines
        self.scene.removeItem(self.item_groups["edge_group"])
        old_obj = []
        for item in self.item_groups["events_group"].childItems():
            old_obj.append(item)
            self.scene.removeItem(item)
            self.item_groups["events_group"].removeFromGroup(item)
        self.scene.removeItem(self.item_groups["events_group"])

        for item in self.item_groups["array_background_lines"].childItems():
            self.scene.removeItem(item)
        self.item_groups["array_background_lines"] = QGraphicsItemGroup()

        # rescale tree
        tree_container = self.item_groups["tree_container"]
        if position == "reset":
            tree_container.reset_scaling()
        elif position == "tiny":
            tree_container.set_scaling_min()
        else:
            tree_container.rescale_x(factor)
        tree_container.tree_view_model.set_node_positions()
        # produce new edges
        self.item_groups["edge_group"] = create_edges(tree_container.tree_view_model, self.app_config)
        self.scene.addItem(self.item_groups["edge_group"])

        # adjust tree node offset
        t_bottom_y = -float('inf')
        t_right_x = 0
        for node_item in self.item_groups["tree_nodes"]:
            node_item.moveBy(0.5, 0.5)
            t_right_x = max(t_right_x, node_item.sceneBoundingRect().right())
            t_bottom_y = max(t_bottom_y, node_item.sceneBoundingRect().bottom())

        # get old tag x
        old_max_tag_x = 0
        for item in self.item_groups["names_tags"].values():
            old_max_tag_x = max(old_max_tag_x, item.sceneBoundingRect().right())
        old_array_pos_x = old_max_tag_x + self.app_config.array_to_tree_margin

        # reset tag positions
        tree_container.tree_view_model.update_leaf_tag_pos(self.item_groups["names_tags"], self.app_config)
        max_tag_x = 0
        for item in self.item_groups["names_tags"].values():
            max_tag_x = max(max_tag_x, item.sceneBoundingRect().right())
        array_pos_x = max_tag_x + self.app_config.array_to_tree_margin

        # move arrays according to difference in tag positions
        additional_arrays = [node.name for node in tree_container.tree_view_model.traverse()
                             if node.name in self.item_groups.keys() and not node.cs == 0]
        x_diff = array_pos_x - old_array_pos_x
        self.readjust_array_x(x_diff, additional_arrays)
        self.store_current_sp_positions()

        # # produce new bg_lines
        right_array_end_x = self.item_groups["template"][-1].sceneBoundingRect().right()
        self.item_groups["array_background_lines"] = QGraphicsItemGroup()
        for name in self.item_groups["names_tags"].keys():
            bg_line = self.produce_bg_line_from_unaligned_tag(name, self.item_groups["names_tags"], right_array_end_x)
            self.item_groups["array_background_lines"].addToGroup(bg_line)
        self.item_groups["array_background_lines"].setZValue(-1)
        self.scene.addItem(self.item_groups["array_background_lines"])

        # # reallign tags
        self.right_allign_tags(array_pos_x)

        # update event positions
        self.item_groups["events_group"] = tree_container.tree_view_model.group_and_position_events(self.app_config)
        self.scene.addItem(self.item_groups["events_group"])

        new_legend_y = t_bottom_y
        t_x_start = self.item_groups["tree_nodes"][0].sceneBoundingRect().left()
        t_x_end = t_right_x

        self.item_groups["legends"]: LegendsContainer
        self.item_groups["legends"].update_legend_dimensions(new_legend_y,
                                                             t_x_start,
                                                             t_x_end,
                                                             array_pos_x,
                                                             right_array_end_x)

        self.reset_tags()

    def layout_scene(self, scene, item_groups):
        tree_nodes = self.item_groups["tree_nodes"]
        edges = self.item_groups["edge_group"]
        events = self.item_groups["events_group"]

        names_tags = self.item_groups["names_tags"]

        t_bottom_y = -float('inf')
        t_right_x = 0

        for node_item in tree_nodes:
            node_item.moveBy(0.5, 0.5)
            self.scene.addItem(node_item)
            t_right_x = max(t_right_x, node_item.sceneBoundingRect().right())
            t_bottom_y = max(t_bottom_y, node_item.sceneBoundingRect().bottom())

        self.scene.addItem(edges)

        self.scene.addItem(events)

        tags_group = QGraphicsItemGroup()
        for item in names_tags.values():
            tags_group.addToGroup(item)
        scene.addItem(tags_group)

        array_pos_x = tags_group.sceneBoundingRect().right() + self.app_config.array_to_tree_margin

        # allign arrays
        right_array_end_x = self.place_arrays_in_scene(array_pos_x, item_groups, names_tags)

        # add array background lines
        self.item_groups["array_background_lines"] = QGraphicsItemGroup()
        for name in item_groups.keys():
            if name == "all_arrays_group" or name == "template" or name == "original_names":
                continue

            if name in names_tags.keys():
                array_bg_line = self.produce_bg_line_from_unaligned_tag(name, names_tags, right_array_end_x)
                self.item_groups["array_background_lines"].addToGroup(array_bg_line)
        self.scene.addItem(self.item_groups["array_background_lines"])
        self.item_groups["array_background_lines"].setZValue(-1)

        if self.app_config.leaf_tag_alignment == "array":
            self.right_allign_tags(array_pos_x)

        new_legend_y = t_bottom_y
        t_x_start = tree_nodes[0].sceneBoundingRect().left()
        t_x_end = t_right_x

        self.item_groups["legends"]: LegendsContainer
        self.item_groups["legends"].set_dimensions(new_legend_y,
                                                   t_x_start,
                                                   t_x_end,
                                                   array_pos_x,
                                                   right_array_end_x)

        self.item_groups["legends"].layout_legends()

    def readjust_array_x(self, move_x_by, other_arrays=None):
        if other_arrays is None:
            other_arrays = []
        arrays_to_mv = [k for k in self.item_groups['names_tags'].keys()]
        arrays_to_mv.append("template")
        arrays_to_mv.append("original_names")
        for name in other_arrays:
            arrays_to_mv.append(name)
        for name in arrays_to_mv:
            for item in self.item_groups[name]:
                item.moveBy(move_x_by, 0)

    def place_arrays_in_scene(self, array_pos_x, item_groups, names_tags, add_to_scene=True):
        min_y = self.scene.itemsBoundingRect().bottom()
        for name in self.model.arrays_dict.keys():
            if name == "template" or name == "original_names":
                continue
            if name in names_tags.keys():
                first_item = item_groups[name][0]
                array_pos_y = (names_tags[name].sceneBoundingRect().center().y()
                               - first_item.boundingRect().center().y())  # / 2) + 3
                for item in item_groups[name]:
                    item.setPos(array_pos_x, array_pos_y)
                    if add_to_scene:
                        self.scene.addItem(item)
                min_y = min(min_y, array_pos_y)
        if self.app_config.show_original_names and "original_names" in item_groups.keys():
            min_y = min_y - self.app_config.t_dummy_node_width
            for item in item_groups["original_names"]:
                item.setPos(array_pos_x, min_y)
                if add_to_scene:
                    self.scene.addItem(item)
        if self.app_config.show_template and "template" in item_groups.keys():
            if self.app_config.show_original_names:
                min_y = min_y - self.app_config.spacer_height - self.app_config.spacer_pen_width + 1
            else:
                min_y = min_y - self.app_config.t_dummy_node_width

            max_x = float('-inf')
            for item in item_groups["template"]:
                item.setPos(array_pos_x, min_y)
                if add_to_scene:
                    self.scene.addItem(item)
                max_x = max(max_x, item.sceneBoundingRect().right())
        right_array_end_x = max_x
        return right_array_end_x

    def produce_bg_line_from_unaligned_tag(self, name, names_tags, rightmost_x):
        node_tag_scene_brect: QRectF
        node_tag_scene_brect = names_tags[name].sceneBoundingRect()
        array_bg_line = QGraphicsLineItem()
        bg_line_x = node_tag_scene_brect.right() + 1.5 * self.app_config.array_to_tree_margin
        bg_line_y = node_tag_scene_brect.center().y()# - self.app_config.spacer_pen_width / 2
        array_bg_line.setLine(bg_line_x, bg_line_y, rightmost_x, bg_line_y)
        array_bg_line.setPen(self.app_config.array_background_line_pen)
        return array_bg_line

    def right_allign_tags(self, rightmost_x):
        for tag in self.item_groups["names_tags"].values():
            curr_x = tag.x()
            curr_y = tag.sceneBoundingRect().center().y()# - self.app_config.spacer_pen_width / 2
            new_point = QPointF(curr_x, curr_y)# + self.app_config.spacer_pen_width / 2)
            tag.setX(rightmost_x - tag.boundingRect().width() - self.app_config.array_to_tree_margin)
            for line in self.item_groups["array_background_lines"].childItems():
                if line.line().y1() == curr_y: # - self.app_config.spacer_pen_width / 2:
                    line: QGraphicsLineItem
                    # line.setLine(new_point.x(), new_point.y(), line.line().x2(), curr_y)
                    line.setLine(new_point.x(), new_point.y(), line.line().x2(), new_point.y())

    def print_headless(self, outformats,
                          input_folder_path, output_folder_path,
                            color_mode, pooling):
        # load new data
        self.app_config.headless_render_type = outformats
        self.app_config.headless_output_folder_path = output_folder_path

        restore_default_settings()
        self.settings.setValue("tree_events/event_pooling", pooling)
        self.load_new_data(input_folder_path)
        if color_mode == "single_color":
            self.single_color_mode_toggled(True)
        elif color_mode == "hsplit":
            self.two_color_mode_toggled(True)
            self.split_event_col_horizontal_toggled(True)
        elif color_mode == "iosplit":
            self.two_color_mode_toggled(True)
            self.split_event_col_inner_outer_toggled(True)
        if "png" in self.app_config.headless_render_type:
            print_to_png(self, self.app_config.headless_output_folder_path)
        if "pdf" in self.app_config.headless_render_type:
            print_to_pdf(self, self.app_config.headless_output_folder_path)




    def print_headless_old(self, outformats,
                         input_folder_path, output_folder_path,
                         color_mode, pooling):  # alternative headless color modes are "single_color", "hsplit" and "iosplit"

        # load new data
        file_name = input_folder_path.split("/")[-1]
        self.app_config.file_name = file_name
        data = read_all_folder_data(input_folder_path)
        self.model = ModelContainer()
        self.model.tree = produce_tree_model(data)
        self.model = add_array_model(data, self.model)
        self.setup_color_manager()

        # set settings
        restore_default_settings()
        if pooling:
            self.settings.setValue("tree_events/event_pooling", True)
            self.app_config.event_pooling = True
        else:
            self.settings.setValue("tree_events/event_pooling", False)
            self.app_config.event_pooling = False

        if color_mode == "single_color":
            self.settings.setValue("colors/two_color_mode", False)
            self.app_config.event_color_mode = "single_color"
            self.app_config.color_manager.set_color_map("single_color_mode")
        elif color_mode == "hsplit":
            self.settings.setValue("colors/two_color_mode", True)
            self.settings.setValue("tree_events/color_split", "horizontal")
            self.app_config.event_color_mode = "horizontal"
            self.app_config.color_manager.set_color_map("two_color_mode")
        elif color_mode == "iosplit":
            self.settings.setValue("colors/two_color_mode", True)
            self.settings.setValue("tree_events/color_split", "inner_outer")
            self.app_config.event_color_mode = "inner_outer"
            self.app_config.color_manager.set_color_map("two_color_mode")

        # produce vis
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.view.setScene(self.scene)
        self.produce_vis_from_model()
        QTimer.singleShot(0, self.fit_drawing_to_view)

        if "png" in outformats:
            print_to_png(self, output_folder_path)
        if "pdf" in outformats:
            print_to_pdf(self, output_folder_path)
        self.scene.clear()
        del self.item_groups
        del self.app_config
        del self.model
        self.scene.deleteLater()
        self.settings.sync()
        del self.settings


    def show_firsttime(self):
        if self.model is None:
            curr_file = self.settings.value("app/current_file")
            if curr_file is not None:
                self.load_new_data(self.settings.value("app/current_file"))
            if not self.app_config.headless_mode:
                self.show()
                return

        self.produce_vis_from_model()

        if self.app_config.headless_mode or self.settings.value("window/geometry") is None:
            x = self.app_config.window_width / self.scene.itemsBoundingRect().width()
            height = int(self.scene.itemsBoundingRect().height() * x)

            self.resize(self.app_config.window_width, height)
            self.view.resize(self.app_config.window_width, height)

        QTimer.singleShot(0, self.fit_drawing_to_view)

        if not self.app_config.headless_mode:
            self.show()

        if "png" in self.app_config.headless_render_type:
            print_to_png(self, self.app_config.headless_output_folder_path)
        if "pdf" in self.app_config.headless_render_type:
            print_to_pdf(self, self.app_config.headless_output_folder_path)

    def show_redraw(self):
        # apply current changes to app_config
        if self.settings.value("tree_events/event_pooling", type=bool, defaultValue=False):
            self.app_config.event_pooling = True
        else:
            self.app_config.event_pooling = False

        self.scene.deleteLater()

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.view.setScene(self.scene)
        # self.scene.clear()
        # self.scene.setSceneRect(QRectF())

        if self.model is None:
            self.show()
            return

        self.produce_vis_from_model()
        QTimer.singleShot(0, self.fit_drawing_to_view)
        self.set_ui_vis_active()

    def produce_vis_from_model(self):
        # self.prod_color_maps_old()
        self.setup_color_manager()

        self.item_groups = dict()
        if self.app_config.show_arrays:
            self.item_groups.update(add_arrays_to_dict(self.model, self.app_config, self.settings))

            first_left_x = self.item_groups["template"][0].boundingRect().left()
            last_right_x = self.item_groups["template"][-1].boundingRect().right()
            array_length = last_right_x - first_left_x
        (self.item_groups["tree_nodes"],
         self.item_groups["edge_group"],
         self.item_groups["events_group"],
         self.item_groups["names_tags"],
         self.item_groups["tree_container"]) = draw_tree(self.model.tree,
                                                         array_length,
                                                         self.app_config)

        self.item_groups["legends"] = LegendsContainer(self.app_config, self.scene)
        self.item_groups["legends"].set_t_leg_items(prod_tr_legend_items(self.app_config,
                                                                         self.model.get_item_types_in_tree()))
        self.layout_scene(self.scene, self.item_groups)

        self.store_current_sp_positions()
        self.add_tags()

    def store_current_sp_positions(self):
        # store positions
        array_names = self.model.get_array_names()
        array_names.append("template")
        array_names.append("original_names")
        for name in array_names:
            for sp in self.item_groups[name]:
                sp.store_pos()

    def fit_drawing_to_view(self):
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def load_color_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   caption="Load Color Map from .csv",
                                                   filter="CSV Files (*.csv)")
        if file_path:
            map_name = self.app_config.color_manager.add_loaded_color_map(file_path)
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
                lambda checked, mn=map_name: self.app_config.color_manager.set_color_map(mn))
            self.ui.menuColor_By_Imported_Color_Map.addAction(action)
            self.ui.colorActionGroup.addAction(action)
            action.setChecked(True)
            self.app_config.color_manager.set_color_map(map_name)
        else:
            print("File open operation cancelled.")
        pass

    def setup_color_manager(self):
        two_color_mode = self.settings.value("colors/two_color_mode", type=bool)
        self.app_config.color_manager = ColorManager(self.app_config, self.model,
                                                     two_color_mode)  # , self.update_array_legend)
        color_options = self.app_config.color_manager.metadata_color_options()
        self.ui.menuColor_By_Metadata.setEnabled(True)
        self.update_color_by_metadata(self.ui.menuColor_By_Metadata, color_options)

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

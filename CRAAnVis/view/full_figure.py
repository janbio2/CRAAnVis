from PyQt6.QtWidgets import QErrorMessage

from view.color.coloring import ColorManager


class Figure:
    """Manages the figure view model"""
    def __init__(self, app_config, model=None):
        self.app_config = app_config
        self.model = model
        self.color_manager = None

        self.tree = None
        self.arrays = None
        self.array_bg_lines = None
        self.legends = None

    def add_model(self, model):
        self.model = model
        print(f"Model added: {model.template}")

    def add_loaded_color_map(self, file_path):
        map_name = self.app_config.color_manager.add_loaded_color_map(file_path)
        return map_name




    def show_template_array(self, show=True):
        return

    def show_original_names_array(self, show=True):
        return

    def show(self):

        return

    def update_legend_layout(self):
        # Todo implement update_legend_layout for updating the legend layout eg when resizing the window
        return



    def setup_color_manager(self):
        two_color_mode = self.app_config.settings.value("colors/two_color_mode", type=bool)
        self.color_manager = ColorManager(self.app_config, self.model,
                                                     two_color_mode)
        color_options = self.color_manager.metadata_color_options()
        # self.ui.menuColor_By_Metadata.setEnabled(True)
        self.update_color_by_metadata(self.ui.menuColor_By_Metadata, color_options)

        # jan you stopped here: the update_color_by_metadata function is not working
        # Todo: figure out a way for the color manager to keep track of metadata color options
        # Todo: and the view to request this information at the right time to update the menu according to update_color_by_metadata


    def setup_figure(self, model=None):
        if model is None and self.model is None:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("No model loaded.")
            error_dialog.exec()
            return
        else:
            print("Model loaded.")
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


    #def show_redraw(self):
    def update_figure(self):
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

    def produce_bg_line_from_unaligned_tag(self, name, names_tags, rightmost_x):
        node_tag_scene_brect: QRectF
        node_tag_scene_brect = names_tags[name].sceneBoundingRect()
        array_bg_line = QGraphicsLineItem()
        bg_line_x = node_tag_scene_brect.right() + 1.5 * self.app_config.array_to_tree_margin
        bg_line_y = node_tag_scene_brect.center().y()  # - self.app_config.spacer_pen_width / 2
        array_bg_line.setLine(bg_line_x, bg_line_y, rightmost_x, bg_line_y)
        array_bg_line.setPen(self.app_config.array_background_line_pen)
        return array_bg_line


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

        # reallign tags
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
        # self.scene.update()
        sc_rect = self.scene.sceneRect()
        new_scene_width = self.item_groups["array_background_lines"].sceneBoundingRect().right() - sc_rect.x()
        sc_rect.setWidth(new_scene_width)
        self.scene.setSceneRect(sc_rect)


from PyQt6.QtCore import QObject

class ArrayFigure(QObject):
    def __init__(self, app_config):
        super().__init__()

        self.app_config = app_config
        self.array_rect = None


    def show_template_array(self, show=True):
        return

    def show_original_names_array(self, show=True):
        return

    def show(self, show=True):
        return


    def store_current_sp_positions(self):
        # store positions
        array_names = self.model.get_array_names()
        array_names.append("template")
        array_names.append("original_names")
        for name in array_names:
            for sp in self.item_groups[name]:
                sp.store_pos()


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

    def delete_tags(self):
        txt_templ = "Template of All Spacers:"
        txt_org = "Original Spacer Names:"

        if txt_templ in self.item_groups:
            self.scene.removeItem(self.item_groups[txt_templ])
            del (self.item_groups[txt_templ])
        if txt_org in self.item_groups:
            self.scene.removeItem(self.item_groups[txt_org])
            del (self.item_groups[txt_org])

    def set_tag_visibility(self, checked):
        if checked:
            self.add_tags()
        else:
            self.delete_tags()

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
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QPen, QColor

from view.colors.colors import TreeSignalManager

EVENT_WIDTH = 20
SPACER_WIDTH = 36
SPACER_HEIGHT = SPACER_WIDTH
RECENT_FILES = []


class AppConfig:
    """This class stores the current settings of the application.
     It is used to pass the settings to the different parts of the application.
     Most of the settings would be better suited as constants."""
    tree_signal_manager: TreeSignalManager

    def __init__(self):
        # App Settings
        self.settings = QSettings()

        self.file_name = ""
        self.headless_mode = False
        self.headless_render_type = []  # select ["pdf"] or  ["png"] or both ["pdf", "png"]
        self.headless_output_folder_path = ""
        self.zoom_factor = 1.1

        # Pdf Settings
        self.pdf_width = 1200
        self.pdf_dpi = 300
        self.add_pdf_header = False
        self.pdf_header_height = -100

        # Color Settings
        self.single_color_mode = False
        self.crispr_element_colors = None

        # Window Settings
        self.window_width = 1000
        self.window_title = "CRISPR Array Ancestry Visualization"

        # Legend and Leaftag Settings
        self.legend_item_width = 20
        self.legend_item_height = self.legend_item_width
        self.legend_item_margin = 6
        self.legend_legend_margin = 10
        self.legend_font = QFont("Courier New", int(self.legend_item_width / 1.3))
        self.legend_y_margin = 40

        self.leaf_tag_alignment = "array"

        # Array Settings
        self.show_arrays = True

        self.show_original_names = True
        # original names settings
        self.original_names_pen_color = Qt.GlobalColor.white

        self.show_template = True
        self.spacer_width = 36
        self.spacer_pen_width = self.spacer_width / 6
        self.spacer_height = self.spacer_width
        self.spacer_font = QFont("Courier New", int(self.spacer_width / 2.8))
        self.bright_deleted_spacers = True

        # self.x_between_crispr_elements = 41

        self.array_to_tree_margin = 20
        self.array_to_template_margin = 20

        self.show_line_background = True
        self.line_background_width = self.spacer_width + self.spacer_pen_width
        self.line_background_color = '#f4f5f5'
        self.array_background_line_pen = QPen(QColor(self.line_background_color), self.line_background_width)
        self.array_background_line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        # Tree Settings
        self.tree_signal_manager = TreeSignalManager()

        self.draw_naive_tree = False

        self.horizontal_mode = True

        # Tree Edges
        self.show_tree_edges = True
        self.vertical_line_width = 2
        self.horizontal_line_width = 2

        self.branch_vertical_margin = 0.1
        self.event_width = EVENT_WIDTH
        self.event_height = self.event_width
        self.event_font = QFont("Courier New", int(self.event_width / 2.7))
        self.event_line_width = 2

        self.leaf_text_height = self.spacer_height
        self.leaf_text_width = self.spacer_width * 8
        self.show_inner_l_tags = False

        self.min_leaf_dist = 0.2 * self.event_width
        self.optimal_array_tree_ratio = 0.5
        self.min_array_tree_ratio = 0.33
        self.max_array_tree_ratio = 0.66
        self.scaling_optimization_rounds = 300

        # Event Settings
        self.event_color_mode = "horizontal"
        self.show_events = True
        self.inter_events_margin = 12

        self.event_positions = {
            "gains": "top-branch",
            "losses": "bottom-branch",
            "contradictions": "top-branch",
            "duplications": "top-branch",
            "transfers": "top-branch",
            "rearrangements": "top-branch",
            "double_gains": "top-branch",
            "independent_gains": "top-branch",
            "dups": "top-branch",
            "reacquisitions": "top-branch"
        }
        self.event_color_dict = {
            "contradictions": QColor("orange"),
            "duplications": QColor("blue"),
            "rearrangements": QColor("purple"),
            "double_gains": QColor("turquoise"),
            "independent_gains": QColor("brown"),
            "dups": QColor("gray"),
            "reacquisitions": QColor("green"),
        }
        self.event_name_dict = {
            "contradictions": "Contradiction",
            "duplications": "Duplication",
            "rearrangements": "Rearrangement",
            "double_gains": "Double Gain",
            "independent_gains": "Independent Gain",
            "dups": "Other Type of Dup. Insertion",
            "reacquisitions": "Reacquisition"
        }
        # Event Pooling
        self.event_pooling = True
        self.epool_width = 3 * self.event_width
        self.epool_sides_width = self.event_width / 2
        self.epool_line_width = 2
        # Node Settings

        # More Tree Settings
        self.t_dummy_node_width = max(self.spacer_height, (2 * self.event_height + self.inter_events_margin))

        self.tree_dummy_node_height_scale_factor = 250
        self.t_node_color = Qt.GlobalColor.blue
        self.t_node_width = 10
        self.t_node_height = self.t_node_width
        self.t_leaf_tag_font = QFont('Arial', 12)

        self.t_edge_color = Qt.GlobalColor.black
        self.t_edge_linewidth = 2
        self.t_edge_pen = QPen(self.t_edge_color)
        self.t_edge_pen.setWidth(self.t_edge_linewidth)
        self.t_extension_edge_pen = QPen(self.t_edge_color)
        self.t_extension_edge_pen.setStyle(Qt.PenStyle.DashLine)
        self.t_extension_pos = "node"

        # debugging
        self.show_inner_l_tags = False


def restore_default_settings():
    """Restores the default settings. Several of the settings would be better suited as constants."""

    settings = QSettings()
    settings.setValue("app/recent_files", RECENT_FILES)
    settings.setValue("app/current_file", None)

    settings.setValue("colors/two_color_mode", True)

    settings.setValue("array/spacer_width", SPACER_WIDTH)
    settings.setValue("array/spacer_pen_width", SPACER_WIDTH / 6)
    settings.setValue("array/spacer_height", SPACER_HEIGHT)

    settings.setValue("margins/x_between_crispr_elements", 41)
    settings.setValue("tree_events/event_font", QFont("Courier New", int(EVENT_WIDTH / 2.7)))

    settings.setValue("tree_events/color_split", "horizontal")

    settings.setValue("tree_events/event_pooling", True)

    settings.setValue("settings/exist", True)

    settings.sync()


def store_current_settings(window):
    """Saves the current window state and some of the visualisation settings."""

    settings = QSettings()

    # Window
    settings.setValue("window/geometry", window.saveGeometry())
    settings.setValue("window/state", window.saveState())
    settings.setValue("window/window_position", window.pos())

    # Colors
    if window.ui.actionTwo_Color_Mode.isChecked():
        settings.setValue("colors/two_color_mode", True)
    else:
        settings.setValue("colors/two_color_mode", False)
    settings.sync()


def restore_window_settings(window):
    settings = QSettings()
    window.restoreGeometry(settings.value("window/geometry"))
    window.restoreState(settings.value("window/state"))
    window.move(settings.value("window/window_position"))
    settings.sync()


def init_settings():
    settings = QSettings()
    if not settings.value("settings/exist"):
        restore_default_settings()
        print("Settings initialised.")


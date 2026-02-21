from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QScrollArea, QPushButton, QWidget,
    QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox
)

# ---------------------------------------------------------------------------
# Field definitions
# Each entry: (key, label, widget_type, row, col, row_span, col_span, validator, options)
# widget_type: "line" | "combo"
# validator:   None | "int" | "double" | ("int", min, max) | ("double", min, max)
# options:     list of strings for combos, None for line edits
# ---------------------------------------------------------------------------

BRIDGE_DATA_FIELDS = [
    ("bridge_type",       "Bridge Type *",                    "combo", 0, 1, 1, 2, None,                       ["Beam", "Arch", "Truss", "Suspension", "Cable-Stayed", "Box Girder", "Other"]),
    ("primary_material",  "Primary Structural Material *",    "combo", 1, 1, 1, 2, None,                       ["RCC", "Prestressed Concrete", "Steel", "Composite", "Timber", "Other"]),
    ("bridge_length",     "Total Bridge Length *",            "line",  2, 1, 1, 2, "double",                   None),
    ("span_length",       "Span Length *",                    "line",  3, 1, 1, 2, "double",                   None),
    ("deck_width",        "Deck Width",                       "line",  4, 1, 1, 2, "double",                   None),
    ("num_lanes",         "Number of Lanes *",                "line",  5, 1, 1, 1, ("int", 1, 10),             None),
    ("latitude",          "Coordinates (Latitude) *",         "line",  6, 1, 1, 1, ("double", -90.0, 90.0),    None),
    ("longitude",         "Coordinates (Longitude) *",        "line",  7, 1, 1, 1, ("double", -180.0, 180.0),  None),
    ("design_life",       "Design Life of Bridge (Years) *",  "combo", 8, 1, 1, 1, None,                       ["50", "75", "100", "120", "Custom"]),
    ("design_life_unit",  "",                                 "combo", 8, 2, 1, 1, None,                       ["Months", "Years"]),
    ("construction_time", "Time for Construction *",          "line",  9, 1, 1, 1, None,                       None),
]

BRIDGE_DATA_DEFAULTS = {
    "bridge_type":       "Beam",
    "primary_material":  "RCC",
    "bridge_length":     "",
    "span_length":       "",
    "deck_width":        "",
    "num_lanes":         "",
    "latitude":          "",
    "longitude":         "",
    "design_life":       "100",
    "design_life_unit":  "Years",
    "construction_time": "",
}


# ---------------------------------------------------------------------------

class BridgeData(QWidget):
    next = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("central_panel_widget")

        self.widgets = {}  # key -> QLineEdit | QComboBox

        left_panel_vlayout = QVBoxLayout(self)
        left_panel_vlayout.setContentsMargins(0, 0, 0, 0)
        left_panel_vlayout.setSpacing(0)

        # --- Scroll Area Setup ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        scroll_content_widget.setObjectName("scroll_content_widget")
        self.scroll_area.setWidget(scroll_content_widget)
        scroll_content_layout = QVBoxLayout(scroll_content_widget)
        scroll_content_layout.addStretch(1)

        # --- Form Widget ---
        self.general_widget = QWidget()
        self.general_widget.setObjectName("general_info_form_widget")
        grid_layout = QGridLayout(self.general_widget)
        grid_layout.setContentsMargins(30, 20, 30, 20)
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)

        # --- Build rows from BRIDGE_DATA_FIELDS ---
        for key, label, widget_type, row, col, row_span, col_span, validator, options in BRIDGE_DATA_FIELDS:

            # Label (skip empty labels e.g. design_life_unit)
            if label:
                lbl = QLabel(label)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                grid_layout.addWidget(lbl, row, 0, 1, 1)

            if widget_type == "line":
                w = QLineEdit(self.general_widget)
                if validator == "double":
                    w.setValidator(QDoubleValidator())
                elif validator == "int":
                    w.setValidator(QIntValidator())
                elif isinstance(validator, tuple) and validator[0] == "int":
                    w.setValidator(QIntValidator(validator[1], validator[2]))
                elif isinstance(validator, tuple) and validator[0] == "double":
                    w.setValidator(QDoubleValidator(bottom=validator[1], top=validator[2]))

            elif widget_type == "combo":
                w = QComboBox(self.general_widget)
                if options:
                    w.addItems(options)
                default = BRIDGE_DATA_DEFAULTS.get(key, "")
                idx = w.findText(default)
                if idx >= 0:
                    w.setCurrentIndex(idx)

            self.widgets[key] = w
            grid_layout.addWidget(w, row, col, row_span, col_span)

        scroll_content_layout.insertWidget(0, self.general_widget)

        next_btn = QPushButton("Next")
        scroll_content_layout.insertWidget(2, next_btn, alignment=Qt.AlignRight)

        left_panel_vlayout.addWidget(self.scroll_area)

        self.bottom_widget = QWidget()
        self.bottom_widget.setObjectName("bottom_widget")

    # --- Data access methods ---

    def get_data(self):
        """Returns current field values as a dict keyed by field name."""
        return {
            key: (w.currentText() if isinstance(w, QComboBox) else w.text())
            for key, w in self.widgets.items()
        }

    def set_data(self, data: dict):
        """Populates fields from a dict. Missing keys are left unchanged."""
        for key, value in data.items():
            if key not in self.widgets:
                continue
            w = self.widgets[key]
            if isinstance(w, QComboBox):
                idx = w.findText(str(value))
                if idx >= 0:
                    w.setCurrentIndex(idx)
            else:
                w.setText(str(value))

    def reset_defaults(self):
        """Resets all fields to their defined defaults."""
        self.set_data(BRIDGE_DATA_DEFAULTS)
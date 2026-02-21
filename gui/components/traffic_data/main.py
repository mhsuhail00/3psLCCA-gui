from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QSizePolicy, QGridLayout, QComboBox,
    QHBoxLayout, QLineEdit, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

# ---------------------------------------------------------------------------
# Simple field definitions (top-level grid fields)
# Each: (key, label, widget_type, unit, has_custom, options)
# ---------------------------------------------------------------------------

TRAFFIC_FIELDS = [
    ("alternate_road_carriageway",   "Alternate Road Carriageway",    "combo", "",                       False, [
        "Single Lane Roads", "Intermediate Lane Roads", "Two Lane Roads",
        "Four Lane Divided Roads", "Six Lane Divided Roads",
        "Four Lane Divided Expressways", "Six Lane Divided Expressways",
        "Eight Lane Divided Urban Expressways",
    ]),
    ("additional_reroute_distance",  "Additional Re-Route Distance",  "line",  "(km)",                   False, None),
    ("additional_travel_time",       "Additional Travel Time",        "line",  "(min)",                  False, None),
    ("road_roughness",               "Road Roughness",                "combo", "(mm/km)",                True,  [
        "2000", "3000", "4000", "5000", "6000", "7000", "8000", "9000", "10000",
    ]),
    ("road_rise",                    "Road Rise",                     "combo", "(m/km)",                 True,  [
        "0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50",
        "55", "60", "65", "70", "75", "80", "85", "90", "95", "100",
    ]),
    ("road_fall",                    "Road Fall",                     "combo", "(m/km)",                 True,  [
        "0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50",
        "55", "60", "65", "70", "75", "80", "85", "90", "95", "100",
    ]),
    ("road_type",                    "Type of Road",                  "combo", "",                       False, [
        "Urban Road", "Rural Road",
    ]),
    ("crash_rate",                   "Crash Rate",                    "line",  "(accidents/million km)", False, None),
]

TRAFFIC_DEFAULTS = {
    "alternate_road_carriageway":  "",
    "additional_reroute_distance": "",
    "additional_travel_time":      "",
    "road_roughness":              "",
    "road_rise":                   "",
    "road_fall":                   "",
    "road_type":                   "",
    "crash_rate":                  "",
}

# ---------------------------------------------------------------------------
# Accident distribution rows
# Each: (key, label)
# ---------------------------------------------------------------------------

ACCIDENT_TYPES = [
    ("minor_injury", "Minor Injury"),
    ("major_injury", "Major Injury"),
    ("fatal",        "Fatal"),
]

# ---------------------------------------------------------------------------
# Vehicle table rows
# Each: (key, label)
# Two inputs per row: daily traffic (int) + accident distribution (float)
# ---------------------------------------------------------------------------

VEHICLE_TYPES = [
    ("two_wheeler",   "Two Wheeler"),
    ("small_cars",    "Small Cars"),
    ("big_cars",      "Big Cars"),
    ("ordinary_bus",  "Ordinary Buses"),
    ("deluxe_bus",    "Deluxe Buses"),
    ("lcv",           "LCV"),
    ("hcv",           "HCV"),
    ("mcv",           "MCV"),
]


# ---------------------------------------------------------------------------

class TrafficData(QWidget):
    def __init__(self):
        super().__init__()

        self.widgets = {}              # key -> QLineEdit | QComboBox  (top fields)
        self.daily_traffic = {}        # vehicle key -> QLineEdit
        self.vehicle_distribution = {} # vehicle key -> QLineEdit
        self.accident_distribution = {}# accident key -> QLineEdit

        self.text_box_width = 200

        self.setObjectName("central_panel_widget")
        left_panel_vlayout = QVBoxLayout(self)
        left_panel_vlayout.setContentsMargins(0, 0, 0, 0)
        left_panel_vlayout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        scroll_content_widget = QWidget()
        scroll_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scroll_content_widget.setObjectName("scroll_content_widget")
        self.scroll_area.setWidget(scroll_content_widget)

        self.scroll_content_layout = QVBoxLayout(scroll_content_widget)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_content_layout.setSpacing(0)

        self.general_widget = QWidget()
        self.general_layout = QVBoxLayout(self.general_widget)
        self.general_layout.setContentsMargins(10, 20, 10, 10)
        self.general_layout.setSpacing(10)

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(20)

        # --- Top-level fields (rows 0–7) ---
        for row, (key, label, widget_type, unit, has_custom, options) in enumerate(TRAFFIC_FIELDS):
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            grid_layout.addWidget(lbl, row, 0, 1, 1)

            if widget_type == "combo":
                w = QComboBox(self.general_widget)
                w.setFixedWidth(self.text_box_width)
                w.setPlaceholderText("Select")
                w.addItems(list(options) + (["Custom"] if has_custom else []))
                if has_custom:
                    w.currentIndexChanged.connect(
                        lambda idx, c=w: self.custom_combo_input(idx, c)
                    )
            else:
                w = QLineEdit(self.general_widget)
                w.setFixedWidth(self.text_box_width)

            self.widgets[key] = w
            grid_layout.addWidget(w, row, 1, 1, 1)

            unit_lbl = QLabel(unit if unit.strip() else " ")
            unit_lbl.setAlignment(Qt.AlignLeft)
            grid_layout.addWidget(unit_lbl, row, 2, 1, 1)

        # --- Accident distribution table (row 8) ---
        accident_widget = QWidget(self.general_widget)
        accident_layout = QGridLayout(accident_widget)
        accident_layout.setContentsMargins(8, 8, 8, 8)
        accident_layout.addWidget(QLabel("Type of Accident"), 0, 0)
        accident_layout.addWidget(QLabel("Percentage Accident Distribution"), 0, 1)

        for i, (key, label) in enumerate(ACCIDENT_TYPES):
            lbl = QLabel(f"{label}:")
            lbl.setFixedHeight(40)
            lbl.setAlignment(Qt.AlignCenter)
            inp = QLineEdit()
            inp.setFixedWidth(self.text_box_width * 2)
            self.accident_distribution[key] = inp
            accident_layout.addWidget(lbl, i + 1, 0)
            accident_layout.addWidget(inp, i + 1, 1)

        acc_row_widget = QWidget(self.general_widget)
        acc_row_layout = QHBoxLayout(acc_row_widget)
        acc_row_layout.setContentsMargins(0, 0, 0, 0)
        acc_row_layout.addWidget(accident_widget, alignment=Qt.AlignTop)
        grid_layout.addWidget(acc_row_widget, 8, 0, 1, 4)

        # --- Vehicle composition table (row 9) ---
        vehicle_widget = QWidget(self.general_widget)
        vehicle_layout = QGridLayout(vehicle_widget)
        vehicle_layout.setContentsMargins(8, 8, 8, 8)
        vehicle_layout.addWidget(QLabel("Type of Vehicle"), 0, 0)
        vehicle_layout.addWidget(QLabel("Composition of Various Vehicles"), 0, 1)
        vehicle_layout.addWidget(QLabel("Percentage Accident Distribution"), 0, 2)

        for i, (key, label) in enumerate(VEHICLE_TYPES):
            lbl = QLabel(f"{label}:")
            lbl.setFixedHeight(40)
            lbl.setAlignment(Qt.AlignCenter)

            daily_inp = QLineEdit()
            daily_inp.setValidator(QIntValidator(daily_inp))
            daily_inp.setFixedWidth(self.text_box_width)
            self.daily_traffic[key] = daily_inp

            dist_inp = QLineEdit()
            dist_inp.setFixedWidth(self.text_box_width)
            self.vehicle_distribution[key] = dist_inp

            vehicle_layout.addWidget(lbl, i + 1, 0)
            vehicle_layout.addWidget(daily_inp, i + 1, 1)
            vehicle_layout.addWidget(dist_inp, i + 1, 2)

        veh_row_widget = QWidget(self.general_widget)
        veh_row_layout = QHBoxLayout(veh_row_widget)
        veh_row_layout.setContentsMargins(0, 0, 0, 0)
        veh_row_layout.addWidget(vehicle_widget, alignment=Qt.AlignTop)
        grid_layout.addWidget(QLabel("(Vehicles/Day)"), 9, 4, 1, 4)
        grid_layout.addWidget(veh_row_widget, 9, 0, 1, 4)

        self.general_layout.addLayout(grid_layout)
        self.general_layout.addStretch(1)
        self.scroll_content_layout.addWidget(self.general_widget, alignment=Qt.AlignLeft)

        self.button_h_layout = QHBoxLayout()
        self.button_h_layout.setSpacing(10)
        self.button_h_layout.setContentsMargins(10, 10, 10, 10)
        self.button_h_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.scroll_content_layout.addLayout(self.button_h_layout)
        self.scroll_content_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        left_panel_vlayout.addWidget(self.scroll_area)

    # --- Data access methods ---

    def get_data(self):
        """Returns all traffic form data as structured dicts."""
        return {
            "traffic_fields": {
                key: (w.currentText() if isinstance(w, QComboBox) else w.text())
                for key, w in self.widgets.items()
            },
            "daily_traffic": {
                key: int(w.text()) if w.text() else 0
                for key, w in self.daily_traffic.items()
            },
            "vehicle_distribution": {
                key: float(w.text()) if w.text() else 0.0
                for key, w in self.vehicle_distribution.items()
            },
            "accident_distribution": {
                key: float(w.text()) if w.text() else 0.0
                for key, w in self.accident_distribution.items()
            },
        }

    def set_data(self, data: dict):
        """Populates all fields from a structured dict (mirrors get_data shape)."""
        for key, value in data.get("traffic_fields", {}).items():
            if key not in self.widgets:
                continue
            w = self.widgets[key]
            if isinstance(w, QComboBox):
                idx = w.findText(str(value))
                if idx >= 0:
                    w.setCurrentIndex(idx)
            else:
                w.setText(str(value))

        for key, value in data.get("daily_traffic", {}).items():
            if key in self.daily_traffic:
                self.daily_traffic[key].setText(str(value))

        for key, value in data.get("vehicle_distribution", {}).items():
            if key in self.vehicle_distribution:
                self.vehicle_distribution[key].setText(str(value))

        for key, value in data.get("accident_distribution", {}).items():
            if key in self.accident_distribution:
                self.accident_distribution[key].setText(str(value))

    def reset_defaults(self):
        """Resets all fields to defaults and clears table inputs."""
        self.set_data({
            "traffic_fields":        TRAFFIC_DEFAULTS,
            "daily_traffic":         {k: "" for k, _ in VEHICLE_TYPES},
            "vehicle_distribution":  {k: "" for k, _ in VEHICLE_TYPES},
            "accident_distribution": {k: "" for k, _ in ACCIDENT_TYPES},
        })

    def custom_combo_input(self, index, combo):
        if combo.itemText(index) == "Custom":
            combo.setEditable(True)
            combo.lineEdit().setText("")
            combo.lineEdit().setPlaceholderText("Type here...")
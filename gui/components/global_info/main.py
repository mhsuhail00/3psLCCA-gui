from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QTextEdit, QScrollArea, QPushButton, QWidget,
    QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox
)

# ---------------------------------------------------------------------------
# Field definitions
# Each entry: (key, placeholder, widget_type, row, col, row_span, col_span)
# widget_type: "line" | "text" | "combo"
# ---------------------------------------------------------------------------

GENERAL_INFO_FIELDS = [
    ("company_name",  "Company Name *",      "line",  0, 1, 1, 2),
    ("project_title", "Project Title *",     "line",  1, 1, 1, 2),
    ("description",   "Project Description", "text",  2, 1, 1, 2),
    ("valuer_name",   "Name of Valuer *",    "line",  3, 1, 1, 1),
    ("job_number",    "Job Number *",        "line",  4, 1, 1, 1),
    ("client",        "Client *",            "line",  5, 1, 1, 1),
    ("country",       "Country *",           "combo", 6, 1, 1, 1),
    ("base_year",     "Base Year *",         "line",  7, 1, 1, 1),
]

GENERAL_INFO_DEFAULTS = {
    "company_name":  "",
    "project_title": "",
    "description":   "",
    "valuer_name":   "",
    "job_number":    "",
    "client":        "",
    "country":       "India",
    "base_year":     "",
}

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize",
    "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
    "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
    "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad",
    "Chile", "China", "Colombia", "Comoros", "Congo (Congo-Brazzaville)", "Costa Rica",
    "Croatia", "Cuba", "Cyprus", "Czechia (Czech Republic)",
    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica",
    "Dominican Republic",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
    "Eswatini (fmr. Swaziland)", "Ethiopia",
    "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala",
    "Guinea", "Guinea-Bissau", "Guyana",
    "Haiti", "Holy See", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan",
    "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
    "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
    "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
    "Montenegro", "Morocco", "Mozambique", "Myanmar (formerly Burma)",
    "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
    "Nigeria", "North Korea", "North Macedonia", "Norway",
    "Oman",
    "Pakistan", "Palau", "Palestine State", "Panama", "Papua New Guinea", "Paraguay",
    "Peru", "Philippines", "Poland", "Portugal",
    "Qatar",
    "Romania", "Russia", "Rwanda",
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa",
    "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands",
    "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka",
    "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga",
    "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States of America", "Uruguay", "Uzbekistan",
    "Vanuatu", "Venezuela", "Vietnam",
    "Yemen",
    "Zambia", "Zimbabwe",
]

# Country info tooltip (specific to the country field)
COUNTRY_INFO_TOOLTIP = "Social Cost of Carbon varies as per selected region"

# ---------------------------------------------------------------------------

class GeneralInfo(QWidget):
    closed = Signal()
    created = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("central_panel_widget")

        self.widgets = {}  # key -> QLineEdit | QTextEdit | QComboBox

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

        # --- General Information Form Widget ---
        self.general_widget = QWidget()
        self.general_widget.setObjectName("general_info_form_widget")
        grid_layout = QGridLayout(self.general_widget)
        grid_layout.setContentsMargins(30, 20, 30, 20)
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)

        # --- Build rows from GENERAL_INFO_FIELDS ---
        for key, placeholder, widget_type, row, col, row_span, col_span in GENERAL_INFO_FIELDS:

            if widget_type == "line":
                w = QLineEdit(self.general_widget, placeholderText=placeholder)

            elif widget_type == "text":
                w = QTextEdit(self.general_widget)
                w.setPlaceholderText(placeholder)

            elif widget_type == "combo":
                w = QComboBox(self.general_widget, placeholderText=placeholder)
                w.setMaxVisibleItems(10)
                w.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                w.addItems(COUNTRIES)
                default_index = w.findText(GENERAL_INFO_DEFAULTS.get(key, ""))
                if default_index >= 0:
                    w.setCurrentIndex(default_index)

                # Info icon specific to the country field
                info_icon = QLabel("ⓘ")
                info_icon.setStyleSheet("color: grey; font-size: 14px;")
                info_icon.setObjectName("info_button")
                info_icon.setToolTip(COUNTRY_INFO_TOOLTIP)
                info_icon.setCursor(Qt.PointingHandCursor)
                info_icon.setAlignment(Qt.AlignRight)
                grid_layout.addWidget(info_icon, row, col + col_span, 1, 1)

            self.widgets[key] = w
            grid_layout.addWidget(w, row, col, row_span, col_span)

        scroll_content_layout.insertWidget(0, self.general_widget)

        create_proj_btn = QPushButton("Create Project")
        create_proj_btn.clicked.connect(lambda: self.created.emit())
        scroll_content_layout.insertWidget(2, create_proj_btn, alignment=Qt.AlignRight)

        left_panel_vlayout.addWidget(self.scroll_area)

    # --- Data access methods ---

    def get_data(self):
        """Returns current field values as a dict keyed by field name."""
        result = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, QComboBox):
                result[key] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                result[key] = widget.toPlainText()
            else:
                result[key] = widget.text()
        return result

    def set_data(self, data: dict):
        """Populates fields from a dict. Missing keys are left unchanged."""
        for key, value in data.items():
            if key not in self.widgets:
                continue
            widget = self.widgets[key]
            if isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(value))
            else:
                widget.setText(str(value))

    def reset_defaults(self):
        """Resets all fields to their defined defaults."""
        self.set_data(GENERAL_INFO_DEFAULTS)

    def close_widget(self):
        self.closed.emit()
        self.setParent(None)
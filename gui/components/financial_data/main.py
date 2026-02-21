from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QGridLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator

# ---------------------------------------------------------------------------
# Field definitions
# Each entry: (key, label, default, unit, has_suggested, int_only)
# ---------------------------------------------------------------------------

FINANCIAL_FIELDS = [
    ("discount_rate",           "Discount Rate (Inflation Adjusted)", "6.70",   "(%)",     True,  False),
    ("inflation_rate",          "Inflation Rate",                      "5.15",   "(%)",     True,  False),
    ("interest_rate",           "Interest Rate",                       "7.75",   "(%)",     True,  False),
    ("investment_ratio",        "Investment Ratio",                    "0.5000", "",        True,  False),
    ("design_life",             "Design Life",                         "50",     "(years)", True,  True),
    ("duration_of_construction","Duration of Construction",            "",       "(years)", False, False),
    ("analysis_period",         "Analysis Period",                     "50",     "(years)", True,  True),
]

# ---------------------------------------------------------------------------
# Defaults isolated (for easy mapping / serialization)
# ---------------------------------------------------------------------------

FINANCIAL_DEFAULTS = {key: default for key, label, default, unit, suggested, int_only in FINANCIAL_FIELDS}

class FinancialData(QWidget):
    closed = Signal()
    next = Signal(str)
    back = Signal(str)

    def __init__(self):
        super().__init__()

        self.widgets = {}  # key -> QLineEdit (changed from list to dict for mapping)

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
        field_width = 200

        # --- Build rows from FINANCIAL_FIELDS ---
        for row, (key, label, default, unit, has_suggested, int_only) in enumerate(FINANCIAL_FIELDS):

            # Label (first field gets an info icon)
            if key == "discount_rate":
                label_widget = QWidget()
                label_layout = QHBoxLayout(label_widget)
                label_layout.setContentsMargins(0, 0, 0, 0)
                label_layout.setSpacing(4)
                label_layout.addWidget(QLabel(label))
                label_layout.addWidget(QLabel("ⓘ"))
                label_layout.addStretch(1)
                grid_layout.addWidget(label_widget, row, 0, alignment=Qt.AlignVCenter)
            else:
                lbl = QLabel(label)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                grid_layout.addWidget(lbl, row, 0, alignment=Qt.AlignVCenter)

            # Input
            field = QLineEdit()
            field.setAlignment(Qt.AlignLeft)
            field.setFixedWidth(field_width)
            field.setText(default)
            if int_only:
                field.setValidator(QIntValidator(field))
            self.widgets[key] = field
            grid_layout.addWidget(field, row, 1, alignment=Qt.AlignVCenter)

            # Unit
            if unit:
                grid_layout.addWidget(QLabel(unit), row, 2, alignment=Qt.AlignVCenter)
            else:
                grid_layout.addWidget(QWidget(), row, 2)

            # Suggested
            if has_suggested:
                grid_layout.addWidget(
                    QLabel("Suggested", parent=self.general_widget), row, 3, alignment=Qt.AlignVCenter
                )
            else:
                grid_layout.addWidget(QWidget(), row, 3)

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

    def get_data(self):
        """Returns current field values as a dict keyed by field name."""
        data = {key: widget.text() for key, widget in self.widgets.items()}
        # print("Financial Data", data)

    def reset_defaults(self):
        """Resets all fields to their defined defaults."""
        for key, widget in self.widgets.items():
            widget.setText(FINANCIAL_DEFAULTS.get(key, ""))

    def close_widget(self):
        self.closed.emit()
        self.setParent(None)
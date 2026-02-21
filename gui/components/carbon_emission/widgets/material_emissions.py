from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class MaterialEmissions(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("Welcome to Material Emissions"))
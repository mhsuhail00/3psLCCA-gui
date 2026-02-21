from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from .widgets.foundation import Foundation
from .widgets.super_structure import SuperStruct
from .widgets.substructure import SubStruct
from .widgets.misc_widget import Misc

class StructureTabView(QWidget):
    def __init__(self, ):
        super().__init__()
        
        # Define Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Top Area
        top_area = QWidget()
        top_layout = QHBoxLayout()
        top_area.setLayout(top_layout)
        region_info = QWidget()
        region_info_layout = QVBoxLayout()
        region_info_layout.addWidget(QLabel("Region Info: India"))
        region_info_layout.addWidget(QLabel("Selected DB: Maharashtra PWD"))
        region_info.setLayout(region_info_layout)
        top_layout.addWidget(region_info)
        
        top_layout.addStretch()
        upload_excel_btn = QPushButton("Upload Excel")
        top_layout.addWidget(upload_excel_btn)
        trash_btn = QPushButton("Trash")
        top_layout.addWidget(trash_btn)

        # Tab View
        tab_view = QTabWidget()
        self.tab_view = tab_view
        tab_view.addTab(Foundation(), "Foundation")
        tab_view.addTab(SuperStruct(), "Super-Structure")
        tab_view.addTab(SubStruct(), "Substructure")
        tab_view.addTab(Misc(), "Miscellaneous")
        
        # Adding Widgets
        main_layout.addWidget(top_area)
        main_layout.addWidget(tab_view)
    
    def select_tab(self, name):
        tabs = ["Foundation", "Super-Structure", "Substructure", "Miscellaneous"]
        self.tab_view.setCurrentIndex(tabs.index(name))
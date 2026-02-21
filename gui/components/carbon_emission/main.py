from PySide6.QtWidgets import  QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget
from .widgets.material_emissions import MaterialEmissions
from .widgets.transport_emissions import TransportEmissions
from .widgets.machinery_emissions import MachineryEmissions
from .widgets.traffic_emissions import TrafficEmissions
from .widgets.social_cost import SocialCost


class CarbonEmissionTabView(QWidget):
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
        # upload_excel_btn = QPushButton("Upload Excel")
        # top_layout.addWidget(upload_excel_btn)
        # trash_btn = QPushButton("Trash")
        # top_layout.addWidget(trash_btn)

        # Tab View
        tab_view = QTabWidget()
        self.tab_view = tab_view
        tab_view.addTab(MaterialEmissions(), "Material Emissions")
        tab_view.addTab(TransportEmissions(), "Transportation Emissions")
        tab_view.addTab(MachineryEmissions(), "Machinery Emissions")
        tab_view.addTab(TrafficEmissions(), "Traffic Diversion Emissions")
        tab_view.addTab(SocialCost(), "Social Cost of Carbon")
        
        # Adding Widgets
        main_layout.addWidget(top_area)
        main_layout.addWidget(tab_view)
    
    def select_tab(self, name):
        tabs = ["Material Emissions", "Transportation Emissions", "Machinery Emissions", "Traffic Diversion Emissions", "Social Cost of Carbon"]
        self.tab_view.setCurrentIndex(tabs.index(name))
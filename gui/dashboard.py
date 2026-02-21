import os
import json

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt


class DashboardPage(QWidget):
    """
    The home / project management screen.
    Displays all local projects with Open, Delete actions.
    Highlights projects that need recovery (main file missing/corrupt but .bak exists).
    """

    def __init__(self, on_new_cb, on_open_cb, on_delete_cb, on_return_cb):
        super().__init__()
        self.on_open = on_open_cb
        self.on_delete = on_delete_cb
        self.on_return = on_return_cb

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        header = QLabel("LCCA Project Manager")
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)

        self.btn_new = QPushButton("＋  Create New Project")
        self.btn_new.setFixedSize(220, 50)
        self.btn_new.clicked.connect(on_new_cb)
        btn_row.addWidget(self.btn_new)

        self.btn_return = QPushButton("↩  Return to Active Project")
        self.btn_return.setFixedSize(220, 50)
        self.btn_return.setStyleSheet(
            "background-color: #2ecc71; color: white; font-weight: bold;"
        )
        self.btn_return.setVisible(False)
        self.btn_return.clicked.connect(self.on_return)
        btn_row.addWidget(self.btn_return)

        layout.addLayout(btn_row)

        # Recent projects list
        layout.addWidget(QLabel("<h3>Recent Projects</h3>"))

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(10)

        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll)

    def refresh(self, projects_dir, has_active_project=False):
        """
        Scans the projects directory and rebuilds the project card list.
        Cards highlighted in yellow indicate the project needs recovery from .bak.
        """
        self.btn_return.setVisible(has_active_project)

        # Clear existing cards
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.itemAt(i).widget()
            if item:
                item.setParent(None)

        if not os.path.exists(projects_dir):
            return

        found_any = False
        for p_id in sorted(os.listdir(projects_dir)):
            p_path = os.path.join(projects_dir, p_id)
            if not os.path.isdir(p_path):
                continue

            json_path = os.path.join(p_path, "project.json")
            bak_path = os.path.join(p_path, "project.json.bak")

            main_ok = os.path.exists(json_path) and os.path.getsize(json_path) > 0
            bak_ok = os.path.exists(bak_path) and os.path.getsize(bak_path) > 0

            if not main_ok and not bak_ok:
                continue  # Not a valid project folder

            is_recovering = not main_ok and bak_ok
            target_file = json_path if main_ok else bak_path

            display_name = p_id
            try:
                with open(target_file, "r") as f:
                    data = json.load(f)
                    display_name = data.get("metadata", {}).get("project_name", p_id)
            except Exception:
                if bak_ok:
                    is_recovering = True
                    try:
                        with open(bak_path, "r") as f:
                            data = json.load(f)
                            display_name = data.get("metadata", {}).get("project_name", p_id)
                    except Exception:
                        pass

            # Build project card
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setMinimumHeight(75)
            if is_recovering:
                card.setStyleSheet("QFrame { background-color: #FFDB58; }")

            cl = QHBoxLayout(card)
            cl.setContentsMargins(15, 8, 15, 8)

            status_tag = (
                "<br><span style='color: #d9534f;'>⚠️  Recovery Mode</span>"
                if is_recovering
                else ""
            )
            info_label = QLabel(
                f"<b>{display_name}</b>{status_tag}<br><small>ID: {p_id}</small>"
            )
            cl.addWidget(info_label)
            cl.addStretch()

            btn_open = QPushButton("Open && Repair" if is_recovering else "Open Project")
            btn_open.setFixedWidth(130)
            btn_open.clicked.connect(lambda checked=False, i=p_id: self.on_open(i))
            cl.addWidget(btn_open)

            btn_del = QPushButton("Delete")
            btn_del.setFixedWidth(80)
            btn_del.setStyleSheet("color: #c0392b;")
            btn_del.clicked.connect(lambda checked=False, i=p_id: self.on_delete(i))
            cl.addWidget(btn_del)

            self.list_layout.addWidget(card)
            found_any = True

        if not found_any:
            empty = QLabel("No local projects found. Create one to get started!")
            empty.setStyleSheet("color: gray; font-style: italic;")
            self.list_layout.addWidget(empty, alignment=Qt.AlignmentFlag.AlignCenter)

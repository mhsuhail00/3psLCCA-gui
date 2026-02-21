"""
LCCA - Life Cycle Cost Analysis
Merged application:
  - Project management & persistence from New App
    (dashboard, atomic save, .bak recovery, lock files, checkpoints/version history)
  - Full LCCA GUI from osbridgelcca_new
    (sidebar navigation, all component tabs, splitter layout)
"""

import os
import sys
import uuid
import json
import shutil
import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QButtonGroup,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QAction

# --- LCCA GUI Components ---
from gui.components.global_info.main import GeneralInfo
from gui.components.bridge_data.main import BridgeData
from gui.components.structure.main import StructureTabView
from gui.components.traffic_data.main import TrafficData
from gui.components.financial_data.main import FinancialData
from gui.components.carbon_emission.main import CarbonEmissionTabView
from gui.components.maintenance.main import Maintenance
from gui.components.recycling.main import Recycling
from gui.components.demolition.main import Demolition
from gui.components.logs import Logs

# --- Core persistence & model ---
from core.model import ProjectModel
from core.persistence import PersistenceService

# --- Dashboard ---
from gui.dashboard import DashboardPage


# ---------------------------------------------------------------------------
# Recovery / Version History Dialog
# ---------------------------------------------------------------------------

class RecoveryDialog(QDialog):
    """Lets the user pick a checkpoint to restore from."""

    def __init__(self, display_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Version History")
        self.setMinimumWidth(450)
        self.setMinimumHeight(300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Select a version to restore:</b>"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.group = QButtonGroup(self)
        for i, name in enumerate(display_names):
            radio = QRadioButton(name)
            scroll_layout.addWidget(radio)
            self.group.addButton(radio, i)
            if i == 0:
                radio.setChecked(True)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_index(self):
        return self.group.checkedId()


# ---------------------------------------------------------------------------
# Main Project Window
# ---------------------------------------------------------------------------

class ProjectWindow(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.project_id = None
        self.model = None
        self.persistence = None

        # --- Auto-save timers ---
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(1500)
        self.save_timer.timeout.connect(self.execute_save)

        self.force_save_timer = QTimer()
        self.force_save_timer.setSingleShot(True)
        self.force_save_timer.setInterval(4000)
        self.force_save_timer.timeout.connect(self.execute_save)

        self.setWindowTitle("LCCA - Home")
        self.resize(1200, 750)

        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._build_dashboard()
        self._build_project_ui()

        self.show_home()

    # ------------------------------------------------------------------
    # Dashboard (home screen)
    # ------------------------------------------------------------------

    def _build_dashboard(self):
        self.dashboard = DashboardPage(
            on_new_cb=lambda: self.manager.request_new(self),
            on_open_cb=lambda p_id: self.manager.request_open(p_id, self),
            on_delete_cb=lambda p_id: self.manager.delete_project(p_id),
            on_return_cb=self._return_to_editor,
        )
        self.main_stack.addWidget(self.dashboard)

    # ------------------------------------------------------------------
    # Project editor UI
    # ------------------------------------------------------------------

    def _build_project_ui(self):
        self.project_widget = QWidget()
        master_layout = QVBoxLayout(self.project_widget)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        # ── Top bar (menu + action buttons) ──────────────────────────
        bar = QWidget()
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(4, 2, 4, 2)

        self.menubar = QMenuBar()

        # Home shortcut
        home_action = QAction("Home", self)
        home_action.triggered.connect(self.show_home)
        self.menubar.addAction(home_action)

        # File menu
        menu_file = QMenu("&File", self.menubar)
        self.menubar.addMenu(menu_file)

        self.actionNew = QAction("New", self)
        self.actionNew.triggered.connect(lambda: self.manager.request_new(self))
        self.actionOpen = QAction("Open Project...", self)
        self.actionOpen.triggered.connect(self.show_home)
        self.actionSave = QAction("Save", self)
        self.actionSave.triggered.connect(self.execute_save)
        self.actionCheckpoint = QAction("Create Checkpoint...", self)
        self.actionCheckpoint.triggered.connect(self.create_checkpoint)
        self.actionVersionHistory = QAction("Version History / Recover...", self)
        self.actionVersionHistory.triggered.connect(self.recover)
        self.actionSaveAs = QAction("Save As...", self)
        self.actionCreateCopy = QAction("Create a Copy", self)
        self.actionPrint = QAction("Print", self)
        self.actionRename = QAction("Rename", self)
        self.actionExport = QAction("Export", self)
        self.actionInfo = QAction("Info", self)

        menu_file.addAction(self.actionNew)
        menu_file.addAction(self.actionOpen)
        menu_file.addSeparator()
        menu_file.addAction(self.actionSave)
        menu_file.addAction(self.actionSaveAs)
        menu_file.addAction(self.actionCreateCopy)
        menu_file.addAction(self.actionPrint)
        menu_file.addSeparator()
        menu_file.addAction(self.actionRename)
        menu_file.addAction(self.actionExport)
        menu_file.addAction(self.actionCheckpoint)
        menu_file.addAction(self.actionVersionHistory)
        menu_file.addSeparator()
        menu_file.addAction(self.actionInfo)

        # Help menu
        menu_help = QMenu("&Help", self.menubar)
        self.menubar.addMenu(menu_help)
        menu_help.addAction(QAction("Contact us", self))
        menu_help.addAction(QAction("Feedback", self))
        menu_help.addSeparator()
        menu_help.addAction(QAction("Video Tutorials", self))
        menu_help.addAction(QAction("Join our Community", self))

        # Tutorials & Logs in menu bar
        self.menubar.addAction(QAction("&Tutorials", self.menubar))
        log_action = QAction("&Logs", self.menubar)
        self.menubar.addAction(log_action)

        bar_layout.addWidget(self.menubar)
        bar_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.execute_save)
        bar_layout.addWidget(self.btn_save)
        bar_layout.addWidget(QPushButton("Calculate"))
        bar_layout.addWidget(QPushButton("Lock"))

        # ── Workspace (sidebar + content) ────────────────────────────
        self.log_window = Logs()
        log_action.triggered.connect(
            lambda: self.content_stack.setCurrentWidget(self.log_window)
        )

        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setMaximumWidth(350)

        # Outputs / metadata page
        self.metadata_page = QLabel()
        self.metadata_page.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sidebar_info = {
            "General Information": {},
            "Bridge Data": {},
            "Input Parameters": {
                "Construction Work Data": [
                    "Foundation",
                    "Super-Structure",
                    "Substructure",
                    "Miscellaneous",
                ],
                "Traffic Data": [],
                "Financial Data": [],
                "Carbon Emission Data": [
                    "Material Emissions",
                    "Transportation Emissions",
                    "Machinery Emissions",
                    "Traffic Diversion Emissions",
                    "Social Cost of Carbon",
                ],
                "Maintenance and Repair": [],
                "Recycling": [],
                "Demolition": [],
            },
            "Outputs": {},
        }

        self.widget_map = {
            "General Information": GeneralInfo(),
            "Bridge Data": BridgeData(),
            "Construction Work Data": StructureTabView(),
            "Traffic Data": TrafficData(),
            "Financial Data": FinancialData(),
            "Carbon Emission Data": CarbonEmissionTabView(),
            "Maintenance and Repair": Maintenance(),
            "Recycling": Recycling(),
            "Demolition": Demolition(),
            "Outputs": self.metadata_page,
        }

        for header, subheaders in sidebar_info.items():
            top_item = QTreeWidgetItem(self.sidebar)
            top_item.setText(0, header)
            for subheader, subitems in subheaders.items():
                sub_item = QTreeWidgetItem(top_item)
                sub_item.setText(0, subheader)
                for subitem in subitems:
                    leaf = QTreeWidgetItem(sub_item)
                    leaf.setText(0, subitem)

        # Content stack
        self.content_stack = QStackedWidget()
        for w in self.widget_map.values():
            self.content_stack.addWidget(w)
        self.content_stack.addWidget(self.log_window)

        self.sidebar.itemPressed.connect(self._on_sidebar_item)

        workspace.addWidget(self.sidebar)
        workspace.addWidget(self.content_stack)
        workspace.setStretchFactor(0, 0)
        workspace.setStretchFactor(1, 1)
        workspace.setSizes([220, 980])

        master_layout.setMenuBar(bar)
        master_layout.addWidget(workspace)

        self.main_stack.addWidget(self.project_widget)

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def show_home(self):
        """Save pending work then switch to the dashboard."""
        if self.save_timer.isActive() or self.force_save_timer.isActive():
            self.execute_save()
        projects_path = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_path, exist_ok=True)
        self.dashboard.refresh(
            projects_path, has_active_project=(self.project_id is not None)
        )
        self.setWindowTitle("LCCA - Home")
        self.main_stack.setCurrentWidget(self.dashboard)

    def _return_to_editor(self):
        if self.project_id:
            self.setWindowTitle(
                f"LCCA - {self.model.get_metadata('project_name')} ({self.project_id})"
            )
            self.main_stack.setCurrentWidget(self.project_widget)

    def _on_sidebar_item(self, item: QTreeWidgetItem):
        header = item.text(0)
        parent = item.parent()
        item.setExpanded(True)
        if header in self.widget_map:
            self.content_stack.setCurrentWidget(self.widget_map[header])
        elif parent:
            parent_header = parent.text(0)
            if parent_header == "Construction Work Data":
                self.content_stack.setCurrentWidget(
                    self.widget_map["Construction Work Data"]
                )
                self.widget_map["Construction Work Data"].select_tab(header)
            elif parent_header == "Carbon Emission Data":
                self.content_stack.setCurrentWidget(
                    self.widget_map["Carbon Emission Data"]
                )
                self.widget_map["Carbon Emission Data"].select_tab(header)

    # ------------------------------------------------------------------
    # Project loading
    # ------------------------------------------------------------------

    def load_project(self, p_id):
        """
        Full project load sequence:
          1. Acquire file lock (prevent multi-window conflicts)
          2. Verify file health; auto-repair from .bak if needed
          3. Load data into model
          4. Refresh editor UI
        """
        # Phase 1: Locking
        if self.persistence is None or self.project_id != p_id:
            self.persistence = PersistenceService(p_id)
            if not self.persistence.acquire_lock():
                is_elsewhere = any(
                    w for w in self.manager.wins if w is not self and w.project_id == p_id
                )
                if is_elsewhere:
                    QMessageBox.warning(
                        self,
                        "Project Locked",
                        "This project is already open in another window.",
                    )
                    self.show_home()
                    return
                else:
                    reply = QMessageBox.question(
                        self,
                        "Force Open?",
                        "This project has a stale lock from a previous session. Force open?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        self.persistence.release_lock()
                        self.persistence.acquire_lock()
                    else:
                        self.show_home()
                        return

        self.project_id = p_id

        # Phase 2: File health check + auto-repair from .bak
        if not self.persistence.is_file_healthy(self.persistence.json_path):
            if self.persistence.is_file_healthy(self.persistence.bak_path):
                shutil.copy2(self.persistence.bak_path, self.persistence.json_path)
                self.status_bar.showMessage(
                    "Main file was corrupt — auto-restored from backup.", 5000
                )
            else:
                QMessageBox.critical(
                    self, "Error", "Project files are corrupted and cannot be recovered."
                )
                self.show_home()
                return

        # Phase 3: Load data
        try:
            with open(self.persistence.json_path, "r") as f:
                self.model = ProjectModel(json.load(f))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
            self.show_home()
            return

        # Phase 4: Refresh UI
        self._sync_ui()

    def _sync_ui(self):
        name = self.model.get_metadata("project_name", self.project_id)
        self.metadata_page.setText(
            f"<h2>Project Metadata</h2>"
            f"<p><b>Name:</b> {name}</p>"
            f"<p><b>ID:</b> {self.project_id}</p>"
            f"<p><b>Created:</b> {self.model.get_metadata('created_at', 'Unknown')}</p>"
        )
        self.status_bar.showMessage(f"Project: {name}  |  ID: {self.project_id}")
        self.sidebar.setCurrentItem(self.sidebar.topLevelItem(0))
        self.setWindowTitle(f"LCCA - {name} ({self.project_id})")
        self.main_stack.setCurrentWidget(self.project_widget)

    # ------------------------------------------------------------------
    # Save / Persistence
    # ------------------------------------------------------------------

    def trigger_delayed_save(self):
        """Start debounced save timers - call whenever data changes."""
        if not self.save_timer.isActive():
            self.status_bar.showMessage("Syncing changes...", 1000)
        self.save_timer.start()
        if not self.force_save_timer.isActive():
            self.force_save_timer.start()

    def execute_save(self):
        """Immediately flush data to disk."""
        if self.persistence and self.model:
            self.save_timer.stop()
            self.force_save_timer.stop()
            self.persistence.save(self.model.to_dict())
            self.status_bar.showMessage("All changes saved.", 2500)

    # ------------------------------------------------------------------
    # Checkpoints & Version History / Recovery
    # ------------------------------------------------------------------

    def create_checkpoint(self):
        """Save a named snapshot of the current project state."""
        if not self.persistence or not self.model:
            QMessageBox.information(self, "No Project", "Open a project first.")
            return
        name, ok = QInputDialog.getText(
            self, "Create Checkpoint", "Enter a name for this version:"
        )
        if ok:
            label = name.strip() or "Manual_Backup"
            filename = self.persistence.create_checkpoint(self.model.to_dict(), label)
            if filename:
                self.status_bar.showMessage(f"Checkpoint saved: {filename}", 5000)
            else:
                QMessageBox.warning(self, "Error", "Failed to create checkpoint.")

    def recover(self):
        """Show version history and let the user restore a checkpoint."""
        if not self.persistence:
            QMessageBox.information(self, "No Project", "Open a project first.")
            return

        cp_dir = self.persistence.checkpoint_dir
        if not os.path.exists(cp_dir):
            QMessageBox.information(
                self, "No Checkpoints", "No checkpoints found for this project."
            )
            return

        files = sorted(
            [f for f in os.listdir(cp_dir) if f.endswith(".json")], reverse=True
        )
        if not files:
            QMessageBox.information(
                self, "No Checkpoints", "No checkpoints found for this project."
            )
            return

        # Build human-readable labels
        display_data = []
        for f in files:
            parts = f.replace(".json", "").split("__")
            if len(parts) == 2:
                name, ts = parts
                try:
                    pretty = (
                        f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}  "
                        f"{ts[8:10]}:{ts[10:12]}:{ts[12:14]}"
                    )
                except Exception:
                    pretty = ts
                display_data.append((f"{name}  (saved: {pretty})", f))
            else:
                display_data.append((f, f))

        dlg = RecoveryDialog([d[0] for d in display_data], self)
        if dlg.exec() != QDialog.Accepted:
            return

        selected_idx = dlg.get_selected_index()
        if selected_idx == -1:
            return

        # Safety gate: offer to save current state first
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Safety Recommendation")
        msg.setText("<b>Save current version before restoring?</b>")
        msg.setInformativeText(
            "Restoring will permanently overwrite your current workspace.\n\n"
            "We recommend creating a Safety Checkpoint of your current work first."
        )
        btn_save = msg.addButton("Save Current & Restore", QMessageBox.ActionRole)
        btn_restore = msg.addButton("Restore Without Saving", QMessageBox.DestructiveRole)
        btn_cancel = msg.addButton(QMessageBox.Cancel)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_cancel:
            return

        if clicked == btn_save:
            cp_name, ok = QInputDialog.getText(
                self, "Safety Checkpoint", "Name for current version:"
            )
            if ok:
                self.persistence.create_checkpoint(
                    self.model.to_dict(), cp_name.strip() or "Pre_Restore_State"
                )
            else:
                return  # User cancelled naming — abort entire restore

        # Perform the restore
        actual_file = display_data[selected_idx][1]
        full_path = os.path.join(cp_dir, actual_file)
        try:
            with open(full_path, "r") as f:
                restored_data = json.load(f)
            self.model = ProjectModel(restored_data)
            self.persistence.save(self.model.to_dict())
            self._sync_ui()
            self.status_bar.showMessage(
                f"Restored: {display_data[selected_idx][0]}", 5000
            )
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", str(e))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def has_project_loaded(self):
        return self.project_id is not None

    def closeEvent(self, event):
        if self.save_timer.isActive() or self.force_save_timer.isActive():
            self.execute_save()
        if self.persistence:
            self.persistence.release_lock()
        self.manager.unregister(self)
        event.accept()


# ---------------------------------------------------------------------------
# Manager -- multi-window coordinator
# ---------------------------------------------------------------------------

class Manager:
    def __init__(self):
        self.wins = []

    def spawn(self):
        w = ProjectWindow(self)
        self.wins.append(w)
        w.show()
        return w

    def _broadcast_dashboard(self):
        path = os.path.join(os.getcwd(), "projects")
        for w in self.wins:
            w.dashboard.refresh(path, has_active_project=(w.project_id is not None))

    def request_new(self, caller):
        name, ok = QInputDialog.getText(caller, "New Project", "Project Name:")
        if not (ok and name.strip()):
            return
        p_id = str(uuid.uuid4())[:8]
        p_dir = os.path.join(os.getcwd(), "projects", p_id)
        os.makedirs(p_dir, exist_ok=True)
        data = {
            "metadata": {
                "project_name": name.strip(),
                "created_at": str(datetime.datetime.now()),
            }
        }
        with open(os.path.join(p_dir, "project.json"), "w") as f:
            json.dump(data, f, indent=4)
        self._broadcast_dashboard()
        target = caller if caller.project_id is None else self.spawn()
        target.load_project(p_id)

    def request_open(self, p_id, caller):
        # If already open in any window, focus that window
        for w in self.wins:
            if w.project_id == p_id:
                w._return_to_editor()
                w.raise_()
                w.activateWindow()
                return
        target = caller if caller.project_id is None else self.spawn()
        target.load_project(p_id)

    def delete_project(self, p_id):
        reply = QMessageBox.question(
            None,
            "Delete Project",
            f"Permanently delete project '{p_id}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            shutil.rmtree(
                os.path.join(os.getcwd(), "projects", p_id), ignore_errors=True
            )
            self._broadcast_dashboard()
            for w in self.wins:
                if w.project_id == p_id:
                    w.project_id = None
                    w.model = None
                    if w.persistence:
                        w.persistence.release_lock()
                    w.persistence = None
                    w.show_home()

    def unregister(self, w):
        if w in self.wins:
            self.wins.remove(w)
        if not self.wins:
            QApplication.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Optionally load stylesheet:
    # from PySide6.QtCore import QFile, QTextStream
    # file = QFile("gui/assets/themes/lightstyle.qss")
    # if file.open(QFile.ReadOnly | QFile.Text):
    #     stream = QTextStream(file)
    #     app.setStyleSheet(stream.readAll())

    m = Manager()
    m.spawn()
    sys.exit(app.exec())

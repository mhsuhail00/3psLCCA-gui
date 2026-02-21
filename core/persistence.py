import os
import json
import shutil
import datetime


class PersistenceService:
    """
    Handles all file I/O for a single project:
    - Atomic save with .bak backup
    - File lock to prevent multi-window conflicts
    - Versioned checkpoints for recovery
    """

    def __init__(self, project_id):
        self.project_id = project_id
        self.base_path = os.path.join(os.getcwd(), "projects", project_id)
        self.json_path = os.path.join(self.base_path, "project.json")
        self.bak_path = os.path.join(self.base_path, "project.json.bak")
        self.lock_path = os.path.join(self.base_path, "project.lock")
        self.checkpoint_dir = os.path.join(self.base_path, "checkpoints")

    def is_file_healthy(self, path):
        """Checks if a file exists and contains valid JSON."""
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return False
        try:
            with open(path, "r") as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def acquire_lock(self):
        """Creates a lock file. Returns False if already locked."""
        if os.path.exists(self.lock_path):
            return False
        with open(self.lock_path, "w") as f:
            f.write("LOCKED")
        return True

    def release_lock(self):
        """Removes the lock file if it exists."""
        if os.path.exists(self.lock_path):
            os.remove(self.lock_path)

    def save(self, data):
        """
        Atomic save:
        1. Back up current file to .bak
        2. Write to a .tmp file
        3. Atomically replace the main file
        """
        if os.path.exists(self.json_path):
            shutil.copy2(self.json_path, self.bak_path)

        tmp_path = self.json_path + ".tmp"
        try:
            with open(tmp_path, "w") as f:
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.json_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

    def create_checkpoint(self, data, custom_name):
        """
        Saves a named snapshot of the current data into the checkpoints folder.
        Filename pattern: Name__YYYYMMDDHHMMSS.json
        """
        try:
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            clean_name = "".join(
                c for c in custom_name if c.isalnum() or c in (" ", "_")
            ).strip()
            if not clean_name:
                clean_name = "Backup"
            filename = f"{clean_name}__{ts}.json"
            cp_path = os.path.join(self.checkpoint_dir, filename)
            with open(cp_path, "w") as f:
                json.dump(data, f, indent=4)
            return filename
        except Exception as e:
            print(f"Checkpoint error: {e}")
            return None

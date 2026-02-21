import uuid
from datetime import datetime


class ProjectModel:
    """
    The Data Model for the LCCA application.
    Stores project metadata and any future structured data.
    """

    def __init__(self, initial_data=None):
        if initial_data and "metadata" in initial_data:
            self._storage = initial_data
        else:
            self._storage = {
                "metadata": {
                    "project_name": "New Project",
                    "author": "User",
                    "created_at": str(datetime.now()),
                },
            }

    def get_metadata(self, key, default=""):
        """Retrieves a value from the metadata dictionary."""
        return self._storage.get("metadata", {}).get(key, default)

    def update_metadata(self, key, value):
        """Updates a metadata field."""
        self._storage["metadata"][key] = value

    def to_dict(self):
        return self._storage

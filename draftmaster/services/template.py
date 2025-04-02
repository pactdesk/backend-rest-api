import json
from pathlib import Path

from traitlets import Any


class TemplateService:
    base_path: Path = Path("templates")

    def load(self, path: Path) -> dict[str, Any]:
        with Path.open(path) as f:
            return json.load(f)

    def load_legal_entity(self) -> dict[str, Any]:
        return self.load(self.base_path / "general" / "parties" / "legal_entity.json")

    def load_natural_person(self) -> dict[str, Any]:
        return self.load(self.base_path / "general" / "parties" / "natural_person.json")

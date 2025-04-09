import json
from pathlib import Path
from typing import Any, cast

from loguru import logger


class TemplateService:
    base_path: Path = Path("templates")

    def load(self, path: Path) -> dict[str, Any]:
        logger.debug(f"Loading template from path: {path}")
        try:
            with Path.open(path) as f:
                content = f.read()
                logger.debug(f"File content length: {len(content)}")
                if not content:
                    logger.error(f"Empty file at path: {path}")
                    return {}
                
                return cast(dict[str, Any], json.loads(content))
            
        except FileNotFoundError:
            logger.error(f"Template file not found: {path}")
            raise
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in file {path}: {str(e)}")
            raise
        
        except Exception as e:
            logger.error(f"Error loading template from {path}: {str(e)}")
            raise

    def load_legal_entity(self) -> dict[str, Any]:
        return self.load(self.base_path / "general" / "parties" / "legal_entity.json")

    def load_natural_person(self) -> dict[str, Any]:
        return self.load(self.base_path / "general" / "parties" / "natural_person.json")
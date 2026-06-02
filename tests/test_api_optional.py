from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@unittest.skipIf(importlib.util.find_spec("fastapi") is None, "FastAPI is optional")
class ApiOptionalTest(unittest.TestCase):
    def test_create_app_exposes_health_route(self) -> None:
        from marketplace_automation.api import create_app

        app = create_app()
        paths = {route.path for route in app.routes}
        self.assertIn("/health", paths)
        self.assertIn("/ads/report", paths)
        self.assertIn("/reviews/drafts", paths)
        self.assertIn("/competitors/opportunities", paths)
        self.assertIn("/integrations/telegram/digest", paths)
        self.assertIn("/integrations/notion/tasks", paths)


if __name__ == "__main__":
    unittest.main()

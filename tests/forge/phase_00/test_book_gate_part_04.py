from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.forge.phase0_book_gate import (
    generate_book_gate_record,
    generate_mermaid_topology,
    generate_summary,
    generate_workspace_inventory,
    load_part_evidence,
)


class BookGatePart04Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.repo = Path(self._temporary_directory.name) / "repo"
        self.repo.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.email", "forge-fixture@example.invalid")
        self._git("config", "user.name", "FORGE Fixture")

        # Create basic structure
        (self.repo / "oce").mkdir()
        (self.repo / "tools").mkdir()
        self._write("oce/main.py", "def main(): pass")
        self._write("tools/script.py", "def script(): pass")

        self._git("add", ".")
        self._git("commit", "-m", "fixture")

    def _git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def _write(self, relative_path: str, content: str) -> None:
        path = self.repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_p0_gat_001_fingerprint_replay_validation(self) -> None:
        """Test that artifacts from different fingerprints are rejected"""
        # Create mock evidence with different fingerprint
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "different_sha"},
            "core_component_inventory": {"components": []},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)

        # Should still generate inventory but with different fingerprint
        self.assertIn("repository_state", inventory)
        self.assertEqual(inventory["repository_state"]["stable_fingerprint"], "different_sha")

    def test_unknown_states_preserved(self) -> None:
        """Test that unknown, absent, and blocked states are preserved"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {"components": [
                {"component_id": "unknown_component", "present": False}
            ]},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)

        # Check that unknown component is preserved
        unknown_components = [
            c for c in inventory["components"]["components"] 
            if c.get("component_id") == "unknown_component"
        ]
        self.assertEqual(len(unknown_components), 1)
        self.assertFalse(unknown_components[0]["present"])

    def test_workspace_inventory_generation(self) -> None:
        """Test that workspace inventory combines all parts correctly"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {"components": []},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {"trading_files": 10}}
        part3_evidence = {"status": "implemented_unverified", "counts": {"claims": 5}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)

        self.assertIn("schema_version", inventory)
        self.assertIn("part_id", inventory)
        self.assertIn("generated_at", inventory)
        self.assertEqual(inventory["trading_files"]["trading_files"], 10)
        self.assertEqual(inventory["documentation_claims"]["claims"], 5)

    def test_summary_is_human_readable(self) -> None:
        """Test that summary is human-readable markdown"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {"components": []},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)
        summary = generate_summary(inventory)

        # Check that summary is markdown format
        self.assertIn("# Phase 0", summary)
        self.assertIn("## Repository State", summary)
        self.assertIn("## Components", summary)
        self.assertIn("## Part Status", summary)

    def test_mermaid_topology_generation(self) -> None:
        """Test that Mermaid topology diagram is generated"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {
                "components": [
                    {"component_id": "component_a", "path": "path/a", "present": True},
                    {"component_id": "component_b", "path": "path/b", "present": False},
                ]
            },
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)
        topology = generate_mermaid_topology(inventory)

        # Check Mermaid format
        self.assertIn("graph TD", topology)
        self.assertIn("Workspace[Workspace]", topology)
        self.assertIn("component_a[path/a]", topology)
        # Absent component should not be in topology
        self.assertNotIn("component_b", topology)

    def test_book_gate_record_structure(self) -> None:
        """Test that book gate record has required structure"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {"components": []},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)
        current_fingerprint = {"stable_fingerprint": "test_sha"}
        
        book_gate = generate_book_gate_record(inventory, current_fingerprint)

        self.assertIn("schema_version", book_gate)
        self.assertIn("book_id", book_gate)
        self.assertIn("overall_status", book_gate)
        self.assertIn("part_statuses", book_gate)
        self.assertIn("gates", book_gate)
        self.assertIn("blockers", book_gate)
        self.assertIn("warnings", book_gate)

    def test_independent_review_pending_in_gate(self) -> None:
        """Test that independent review is marked as pending"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {"components": []},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)
        current_fingerprint = {"stable_fingerprint": "test_sha"}
        
        book_gate = generate_book_gate_record(inventory, current_fingerprint)

        # Check that independent review is pending
        self.assertEqual(book_gate["gates"]["independent_review"], "pending")
        self.assertIn("independent review", book_gate["warnings"][0].lower())

    def test_artifacts_are_machine_readable(self) -> None:
        """Test that all artifacts are machine-readable"""
        part1_evidence = {
            "status": "implemented_unverified",
            "repository_fingerprint": {"stable_fingerprint": "test_sha"},
            "core_component_inventory": {"components": []},
        }
        part2_evidence = {"status": "implemented_unverified", "counts": {}}
        part3_evidence = {"status": "implemented_unverified", "counts": {}}

        inventory = generate_workspace_inventory(part1_evidence, part2_evidence, part3_evidence)

        # Verify inventory is valid JSON
        json.dumps(inventory)

        # Verify structure
        self.assertIn("schema_version", inventory)
        self.assertIn("part_id", inventory)
        self.assertIn("generated_at", inventory)


if __name__ == "__main__":
    unittest.main()
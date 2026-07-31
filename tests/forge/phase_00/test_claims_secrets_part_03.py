from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.forge.phase0_claims_secrets import (
    generate_claims_inventory,
)


class ClaimsSecretsPart03Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.repo = Path(self._temporary_directory.name) / "repo"
        self.repo.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.email", "forge-fixture@example.invalid")
        self._git("config", "user.name", "FORGE Fixture")

        # Create documentation files
        self._write("README.md", "# Test Repository\n\nThe system supports feature X.")
        self._write("ARCHITECTURE.md", "# Architecture\n\nThe application will use microservices.")
        self._write("docs/SECURITY.md", "# Security\n\nNo secrets in this file.")

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

    def test_p0_doc_001_claim_provenance(self) -> None:
        """Test that claims include source provenance information"""
        inventory = generate_claims_inventory(self.repo)

        for doc in inventory["documents"]:
            self.assertIn("path", doc)
            self.assertIn("claims", doc)
            for claim in doc["claims"]:
                self.assertIn("line_number", claim)
                self.assertIn("category", claim)

    def test_p0_sec_001_redaction(self) -> None:
        """Test that secret patterns are redacted without retaining actual values"""
        # Create file with secret pattern
        self._write("CONFIG.md", "api_key=ghp_test123456789")
        self._git("add", ".")
        self._git("commit", "-m", "add config")

        inventory = generate_claims_inventory(self.repo)

        # Check that secrets are redacted
        for doc in inventory["documents"]:
            for secret in doc["secrets"]:
                self.assertIn("redacted_match", secret)
                self.assertIn("[REDACTED:", secret["redacted_match"])
                # Original pattern should not be in redacted match
                self.assertNotIn("ghp_test123456789", secret["redacted_match"])

    def test_contradictions_identification_mechanism(self) -> None:
        """Test that contradiction identification mechanism exists"""
        # Create file with contradictory claims
        self._write("SPECS.md", "The system supports feature X. The system does not support feature X.")
        self._git("add", ".")
        self._git("commit", "-m", "add specs")

        inventory = generate_claims_inventory(self.repo)

        # Check that contradictions field exists and has proper structure
        self.assertIn("contradictions", inventory)
        self.assertIsInstance(inventory["contradictions"], list)

    def test_findings_contain_metadata_not_secret_material(self) -> None:
        """Test that findings contain category/location metadata but no secret material"""
        # Create file with secret
        self._write("SECRETS.md", "api_key=secret123")
        self._git("add", ".")
        self._git("commit", "-m", "add secrets")

        inventory = generate_claims_inventory(self.repo)

        # Check that secret findings have metadata
        for doc in inventory["documents"]:
            for secret in doc["secrets"]:
                self.assertIn("line_number", secret)
                self.assertIn("column", secret)
                self.assertIn("pattern", secret)
                # Check no actual secret value is stored
                self.assertNotIn("secret123", str(secret))

    def test_claim_categorization(self) -> None:
        """Test that claims are categorized by keyword"""
        # Create test document with different claim categories
        self._write("CATEGORIES.md", "The system architecture supports microservices. The security requires encryption.")
        self._git("add", ".")
        self._git("commit", "-m", "add categories")

        inventory = generate_claims_inventory(self.repo)

        # Check that different categories are present
        self.assertIn("category_counts", inventory)
        self.assertGreater(len(inventory["category_counts"]), 0)

    def test_excluded_directories_not_scanned(self) -> None:
        """Test that excluded directories are not scanned"""
        # Create file in excluded directory
        excluded_dir = self.repo / ".git"
        excluded_dir.mkdir(exist_ok=True)
        self._write(".git/config", "[user]\nname = test")

        inventory = generate_claims_inventory(self.repo)

        # Check that .git files are not in inventory
        git_files = [doc for doc in inventory["documents"] if ".git" in doc["path"]]
        self.assertEqual(len(git_files), 0)

    def test_empty_documentation_handling(self) -> None:
        """Test that documents without claims are handled correctly"""
        self._write("EMPTY.md", "# Empty\n\nNo claims here.")
        self._git("add", ".")
        self._git("commit", "-m", "add empty")

        inventory = generate_claims_inventory(self.repo)

        # Check that the inventory can handle documents with no claims
        self.assertIn("documents", inventory)
        self.assertIsInstance(inventory["documents"], list)

    def test_artifacts_are_machine_readable(self) -> None:
        """Test that generated artifacts are machine-readable JSON"""
        inventory = generate_claims_inventory(self.repo)

        # Verify structure
        self.assertIn("schema_version", inventory)
        self.assertIn("part_id", inventory)
        self.assertIn("generated_at", inventory)
        self.assertIn("documents", inventory)
        self.assertIn("contradictions", inventory)

        # Verify all documents have required fields
        for doc in inventory["documents"]:
            self.assertIn("path", doc)
            self.assertIn("claims", doc)
            self.assertIn("secrets", doc)

    def test_deterministic_behavior(self) -> None:
        """Test that inventory generation is deterministic"""
        first_inventory = generate_claims_inventory(self.repo)
        second_inventory = generate_claims_inventory(self.repo)

        self.assertEqual(first_inventory["total_documents"], second_inventory["total_documents"])
        self.assertEqual(first_inventory["total_claims"], second_inventory["total_claims"])


if __name__ == "__main__":
    unittest.main()
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.forge.phase0_trading_census import (
    generate_data_inventory,
    generate_dependency_inventory,
    generate_trading_census,
    scan_data_files,
    scan_dependency_manifests,
    scan_trading_files,
)


class InventoryPart02Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.repo = Path(self._temporary_directory.name) / "repo"
        self.repo.mkdir()
        self._git("init", "-b", "main")
        self._git("config", "user.email", "forge-fixture@example.invalid")
        self._git("config", "user.name", "FORGE Fixture")

        # Create relevant directory structure
        (self.repo / "forge").mkdir()
        (self.repo / "srrs_opc").mkdir()
        (self.repo / "tools").mkdir()

        # Create sample trading files
        self._write("forge/data/test.py", "def test(): pass")
        self._write("srrs_opc/main.py", "def main(): pass")
        self._write("tools/script.py", "def script(): pass")
        self._write("forge/data/market.csv", "symbol,price\nBTC,50000")
        self._write("forge/config.yaml", "key: value")
        # Create dependency manifests in relevant directories
        self._write("forge/requirements.txt", "numpy==1.0.0")
        self._write("tools/pyproject.toml", "[project]")

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

    def test_p0_dat_001_trading_census_generates_metadata_only(self) -> None:
        """Test that trading census generates metadata without operational classification"""
        census = generate_trading_census(self.repo)

        self.assertIn("schema_version", census)
        self.assertIn("part_id", census)
        self.assertIn("generated_at", census)
        self.assertIn("total_files", census)
        self.assertIn("files", census)

        # Verify component field is "unknown" (no operational classification)
        for file_record in census["files"]:
            self.assertEqual(file_record["component"], "unknown")

    def test_p0_dat_002_large_files_are_skipped_not_hashed(self) -> None:
        """Test that large files are skipped for performance"""
        # Create a large file (>100MB threshold)
        large_file = self.repo / "forge/large_file.csv"
        large_file.write_bytes(b"x" * (101 * 1024 * 1024))  # 101MB

        census = generate_trading_census(self.repo)

        # Find the large file in census
        large_file_record = [
            f for f in census["files"] if f["path"] == "forge/large_file.csv"
        ]
        self.assertTrue(len(large_file_record) > 0)
        self.assertEqual(large_file_record[0]["hash"], "skipped_large_file")

    def test_p0_dat_003_trading_file_belongs_to_one_component(self) -> None:
        """Test that each trading file belongs to exactly one component"""
        census = generate_trading_census(self.repo)

        # All files should have component field
        for file_record in census["files"]:
            self.assertIn("component", file_record)
            self.assertIsInstance(file_record["component"], str)

    def test_p0_dat_004_dependency_manifest_identity_reproducibility(self) -> None:
        """Test that dependency manifests produce reproducible identity"""
        first_inventory = generate_dependency_inventory(self.repo)
        second_inventory = generate_dependency_inventory(self.repo)

        self.assertEqual(len(first_inventory["manifests"]), len(second_inventory["manifests"]))

        for first, second in zip(first_inventory["manifests"], second_inventory["manifests"]):
            self.assertEqual(first["path"], second["path"])
            self.assertEqual(first["name"], second["name"])
            self.assertEqual(first["hash"], second["hash"])

    def test_p0_dat_005_dependency_manifests_found_in_relevant_locations(self) -> None:
        """Test that dependency manifests are found in relevant directories"""
        inventory = generate_dependency_inventory(self.repo)

        # Verify at least some manifests were found
        self.assertGreater(len(inventory["manifests"]), 0)

        # Verify manifest structure
        for manifest in inventory["manifests"]:
            self.assertIn("path", manifest)
            self.assertIn("name", manifest)
            self.assertIn("hash", manifest)

        # Verify expected manifests are in relevant directories
        manifest_paths = {m["path"] for m in inventory["manifests"]}
        self.assertTrue(any("forge" in path and "requirements.txt" in path for path in manifest_paths))

    def test_p0_dat_006_unknown_metadata_remains_unknown(self) -> None:
        """Test that data metadata fields remain unknown unless evidenced"""
        data_inventory = generate_data_inventory(self.repo)

        for data_file in data_inventory["files"]:
            self.assertEqual(data_file["symbol"], "unknown")
            self.assertEqual(data_file["timeframe"], "unknown")
            self.assertEqual(data_file["timezone"], "unknown")
            self.assertEqual(data_file["adjustment"], "unknown")
            self.assertEqual(data_file["provenance"], "unknown")
            self.assertEqual(data_file["reproduction_state"], "unknown")

    def test_p0_dat_007_trading_census_scans_relevant_directories_only(self) -> None:
        """Test that trading census scans only relevant directories"""
        # Create file in excluded directory
        excluded_dir = self.repo / ".windsurf"
        excluded_dir.mkdir()
        self._write(".windsurf/config.json", '{"key": "value"}')

        census = generate_trading_census(self.repo)

        # Files in excluded directories should not appear
        excluded_files = [f for f in census["files"] if ".windsurf" in f["path"]]
        self.assertEqual(len(excluded_files), 0)

    def test_p0_dat_008_data_files_identified_by_pattern(self) -> None:
        """Test that data files are identified by their extensions"""
        inventory = generate_data_inventory(self.repo)

        # Should find the CSV file
        csv_files = [f for f in inventory["files"] if f["path"].endswith(".csv")]
        self.assertTrue(len(csv_files) > 0)

        # Should not find Python files in data inventory
        py_files = [f for f in inventory["files"] if f["path"].endswith(".py")]
        self.assertEqual(len(py_files), 0)

    def test_p0_dat_009_census_generation_is_deterministic(self) -> None:
        """Test that census generation produces consistent results"""
        first_census = generate_trading_census(self.repo)
        second_census = generate_trading_census(self.repo)

        self.assertEqual(first_census["total_files"], second_census["total_files"])
        self.assertEqual(len(first_census["files"]), len(second_census["files"]))

        for first, second in zip(first_census["files"], second_census["files"]):
            self.assertEqual(first["path"], second["path"])
            self.assertEqual(first["hash"], second["hash"])

    def test_p0_dat_010_census_includes_file_size_information(self) -> None:
        """Test that census includes accurate file size information"""
        census = generate_trading_census(self.repo)

        for file_record in census["files"]:
            self.assertIn("size_bytes", file_record)
            self.assertIsInstance(file_record["size_bytes"], int)
            self.assertGreater(file_record["size_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
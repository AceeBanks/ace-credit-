from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.forge.phase0_environment_fingerprint import (
    get_environment_fingerprint,
    get_tool_version,
)


class EnvironmentFingerprintTests(unittest.TestCase):
    def test_p0_env_001_environment_completeness(self) -> None:
        """Test that all required tools are recorded as present, absent, or not applicable"""
        fingerprint = get_environment_fingerprint()
        
        # Check that tools section exists
        self.assertIn("tools", fingerprint)
        
        # Check that required tools are present
        required_tools = ["python", "python3"]
        for tool in required_tools:
            self.assertIn(tool, fingerprint["tools"])
            self.assertIn("present", fingerprint["tools"][tool])
            self.assertIn("version", fingerprint["tools"][tool])
            self.assertIn("path", fingerprint["tools"][tool])
    
    def test_tool_version_detection(self) -> None:
        """Test that tool version detection works for available tools"""
        python_version = get_tool_version("python")
        
        # Python should always be present
        self.assertTrue(python_version["present"])
        self.assertIsNotNone(python_version["version"])
        self.assertIsNotNone(python_version["path"])
    
    def test_tool_absent_handling(self) -> None:
        """Test that absent tools are handled gracefully"""
        absent_tool = get_tool_version("nonexistent_tool_xyz")
        
        self.assertFalse(absent_tool["present"])
        self.assertIsNone(absent_tool["version"])
        self.assertIsNone(absent_tool["path"])
    
    def test_fingerprint_structure(self) -> None:
        """Test that fingerprint has required structure"""
        fingerprint = get_environment_fingerprint()
        
        # Check top-level fields
        self.assertIn("schema_version", fingerprint)
        self.assertIn("part_id", fingerprint)
        self.assertIn("generated_at", fingerprint)
        self.assertIn("system", fingerprint)
        self.assertIn("python", fingerprint)
        self.assertIn("tools", fingerprint)
        self.assertIn("environment", fingerprint)
        self.assertIn("resources", fingerprint)
    
    def test_system_information(self) -> None:
        """Test that system information is collected"""
        fingerprint = get_environment_fingerprint()
        
        system = fingerprint["system"]
        self.assertIn("os", system)
        self.assertIn("architecture", system)
        self.assertIn("hostname", system)
    
    def test_python_information(self) -> None:
        """Test that Python information is collected"""
        fingerprint = get_environment_fingerprint()
        
        python_info = fingerprint["python"]
        self.assertIn("version", python_info)
        self.assertIn("executable", python_info)
        self.assertIn("implementation", python_info)
    
    def test_environment_variables_names_only(self) -> None:
        """Test that only environment variable names are collected, not values"""
        fingerprint = get_environment_fingerprint()
        
        env = fingerprint["environment"]
        self.assertIn("variable_names", env)
        self.assertIn("variable_count", env)
        
        # Ensure values are not stored
        for var_name in env["variable_names"]:
            self.assertNotIn(":", var_name)  # No key=value format
            self.assertNotIn("=", var_name)
    
    def test_disk_space_information(self) -> None:
        """Test that disk space information is collected"""
        fingerprint = get_environment_fingerprint()
        
        resources = fingerprint["resources"]
        self.assertIn("disk", resources)
        
        if fingerprint["resources"]["disk"]:
            disk = fingerprint["resources"]["disk"]
            self.assertIn("total_gb", disk)
            self.assertIn("free_gb", disk)
            self.assertIn("used_gb", disk)
    
    def test_artifact_is_machine_readable(self) -> None:
        """Test that fingerprint is valid JSON"""
        fingerprint = get_environment_fingerprint()
        
        # Should be serializable
        json.dumps(fingerprint)
        
        # Should have valid schema
        self.assertIsInstance(fingerprint["schema_version"], str)
        self.assertIsInstance(fingerprint["part_id"], str)
        self.assertIsInstance(fingerprint["generated_at"], str)


if __name__ == "__main__":
    unittest.main()
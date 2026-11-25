
import unittest
from monitor import compare_scans
from monitor import hash_file
from pathlib import Path
import tempfile



class TestCompareScans(unittest.TestCase):

    def test_added_file(self):
        old_hashes = {"notes.txt": "abc123"}
        new_hashes = {
            "notes.txt": "abc123",
            "report.txt": "xyz789"
        }

        added, modified, deleted = compare_scans(
            old_hashes, new_hashes
        )

        self.assertEqual(added, ["report.txt"])
        self.assertEqual(modified, [])
        self.assertEqual(deleted, [])

    def test_modified_file(self):
        old_hashes = {
            "notes.txt" : "abc123" 
        }
        new_hashes = {
            "notes.txt" : "xyz789"
        }

        added, modified, deleted = compare_scans(
            old_hashes, new_hashes
        )

        self.assertEqual(added, [])
        self.assertEqual(modified, ["notes.txt"])
        self.assertEqual(deleted, [])

    def test_deleted_file(self):
        old_hashes = {
            "notes.txt": "abc123", 
            "report.txt": "xyz789"
        }
        new_hashes = {
            "notes.txt" : "abc123"
        }
        
        added, modified, deleted = compare_scans(
        old_hashes, new_hashes
        )
        
        self.assertEqual(added, [])
        self.assertEqual(modified, [])
        self.assertEqual(deleted, ["report.txt"])

    def test_no_changes(self):
        old_hashes = {
            "notes.txt": "abc123",
            "program.py": "def456"
        }

        new_hashes = {
            "notes.txt": "abc123",
            "program.py": "def456"
        }

        added, modified, deleted = compare_scans(
        old_hashes, new_hashes
        )

        self.assertEqual(added, [])
        self.assertEqual(modified, [])
        self.assertEqual(deleted, [])


class TestHashFile(unittest.TestCase):

    def test_hash_changes_when_content_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            test_file = Path(folder) / "hello.txt"

            test_file.write_text("Hello")
            first_hash = hash_file(test_file)

            test_file.write_text("Goodbye")
            second_hash = hash_file(test_file)

        self.assertNotEqual(first_hash, second_hash)

    def test_correct_sha256(self):
        with tempfile.TemporaryDirectory() as folder:
            test_file = Path(folder) / "hello.txt"

            test_file.write_text("Hello")

            hash_num = hash_file(test_file)

        self.assertEqual(hash_num, "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969")
    
from monitor import scan_directory

class TestScanDirectory(unittest.TestCase):

    def test_scans_multiple_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)

            (root / "hello.txt").write_text("Hello")
            (root / "notes.txt").write_text("Some notes")

            documents = root / "documents"
            documents.mkdir()
            (documents / "report.txt").write_text("Report contents")

            results = scan_directory(root)

            self.assertIn("hello.txt", results)
            self.assertIn("notes.txt", results)
            self.assertIn("documents/report.txt", results)
            self.assertEqual(
                results["hello.txt"],
                hash_file(root / "hello.txt")
            )
            self.assertEqual(
                results["documents/report.txt"],
                hash_file(documents / "report.txt")
            )
            self.assertEqual(len(results), 3)

from monitor import load_baseline
import json
class TestLoadBaseline(unittest.TestCase):

    def test_missing_baseline(self):
        with tempfile.TemporaryDirectory() as folder:
            missing_file = Path(folder) / "nonexistent.json"

            with self.assertRaises(FileNotFoundError):
                load_baseline(missing_file)

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            invalid_file = Path(folder) / "invalid.json"

            invalid_file.write_text("This is not valid JSON!")

            with self.assertRaises(json.JSONDecodeError):
                load_baseline(invalid_file) 

from unittest.mock import patch
from monitor import main

class TestMain(unittest.TestCase):

    def test_no_command(self):
        with patch("sys.argv", ["monitor.py"]):
            with patch("builtins.print") as mock_print:
                main()

            mock_print.assert_called_once_with(
                "Please provide a command."
            )

    def test_unknown_command(self):
        with patch("sys.argv", ["monitor.py", "banana"]):
            with patch("builtins.print") as mock_print:
                main()

            mock_print.assert_called_once_with(
                "Unknown command"
            ) 

    def test_check_missing_baseline(self):
        with patch("sys.argv", ["monitor.py", "check", "sample_files", "baseline.json"]):
            with patch("monitor.load_baseline", side_effect=FileNotFoundError):
                with patch("builtins.print") as mock_print:
                    main()

        mock_print.assert_any_call("Checking file integrity...")  
        mock_print.assert_any_call("Error: No baseline found\n 'Run py monitor.py init' first")

    def test_check_invalid_json(self):
        error = json.JSONDecodeError("Invalid JSON", "invalid", 0)

        with patch("sys.argv", ["monitor.py", "check", "sample_files", "baseline.json"]):
            with patch("monitor.load_baseline", side_effect=error):
                with patch("builtins.print") as mock_print:
                    main()

        mock_print.assert_any_call(
            "Checking file integrity..."
        )
        mock_print.assert_any_call(
            "Error: Baseline file contains invalid JSON."
        )

    def test_invalid_arguments(self):

        with patch("sys.argv", ["monitor.py", "check", "sample_files"]):
            with patch("builtins.print") as mock_print:
                main()

        mock_print.assert_any_call("Error: Invalid number of arguments.")
        mock_print.assert_any_call("Usage: py monitor.py <init|check> <folder_path> <baseline_path>")

    def test_init_invalid_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            missing_folder = root / "nonexistent"
            baseline = root / "baseline.json"

            with patch("sys.argv", ["monitor.py", "init", str(missing_folder), str(baseline)]):
                with patch("builtins.print") as mock_print:
                    main()

            mock_print.assert_any_call("Error: Invalid directory.")
            self.assertFalse(baseline.exists())

    def test_check_invalid_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            missing_folder = root / "nonexistent"
            baseline = root / "baseline.json"

            with patch("sys.argv", ["monitor.py", "check", str(missing_folder), str(baseline)]):
                with patch("monitor.load_baseline") as mock_load:
                    with patch("builtins.print") as mock_print:
                        main()
                
            mock_load.assert_not_called()    
            mock_print.assert_any_call("Error: Invalid directory.")

if __name__ == "__main__":
    unittest.main()

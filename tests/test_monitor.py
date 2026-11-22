
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
    



if __name__ == "__main__":
    unittest.main()

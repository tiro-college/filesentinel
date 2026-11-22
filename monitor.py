
import hashlib
from pathlib import Path

def hash_file(file_path):
    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()

def scan_directory(folder_path):
    file_hashes = {}

    folder = Path(folder_path)
    
    for file in folder.rglob("*"):
        if file.is_file():
            hash_num = hash_file(file)
            relative_path = file.relative_to(folder).as_posix()
            file_hashes[relative_path] = hash_num
    return file_hashes

import json

def save_baseline(file_hashes, output_file):
    with open(output_file,"w") as file:
        json.dump(file_hashes,file, indent = 4)
    
def load_baseline(input_file):
    with open(input_file, "r") as file:
       return json.load(file)

def compare_scans(old_hashes, new_hashes):

    added = []
    modified = []
    deleted = []

    for item in new_hashes:
        if item not in old_hashes:
            added.append(item)

        elif old_hashes[item] != new_hashes[item]:
            modified.append(item)
            
    for item in old_hashes:
        if item not in new_hashes:
            deleted.append(item)

        
    return added, modified, deleted

import sys

def main():
    if len(sys.argv) < 2:
        print("Please provide a command.")
        return

    command = sys.argv[1]

    if command == "init":
        print("Initializing FileSentinel...")

        baseline = Path("baseline.json")

        if baseline.exists():
            print("Error: Baseline already exists.")
            return

        file_hashes = scan_directory("sample_files")
        save_baseline(file_hashes, "baseline.json")

        print("Baseline created successfully!")


    
    elif command == "check":
        print("Checking file integrity...")

        try:
            old_hashes = load_baseline("baseline.json")

        except FileNotFoundError:
            return print("Error: No baseline found\n 'Run py monitor.py init' first")
            
        
        new_hashes = scan_directory("sample_files")

        added, modified, deleted = compare_scans(old_hashes, new_hashes)

        print("Added:", added)
        print("Modified:", modified)
        print("Deleted:", deleted)


    else:
        print("Unknown command")

# TESTING OUR FUNCTIONS

# Test 1: Hash one file
print("TEST 1: Hashing")
print(hash_file("sample_files/example.txt"))

# Test 2: Scan a directory
print("\nTEST 2: Directory scanning")
results = scan_directory("sample_files")
print(results)

# Test 3: Save baseline
print("\nTEST 3: Saving baseline")
save_baseline(results, "baseline.json")
print("Baseline saved!")

# Test 4: Load baseline
saved_hashes = load_baseline("baseline.json")
print("Previously saved hashes:")
print(saved_hashes)

# Test 5: Comparing scans
old_hashes = {
    "notes.txt": "abc123",
    "program.py": "def456",
    "old_file.txt": "ghi789"
}

new_hashes = {
    "notes.txt": "xyz123",
    "program.py": "def456",
    "new_file.txt": "jkl012"
}

added, modified, deleted = compare_scans(
    old_hashes, new_hashes
)

print("Added:", added)
print("Modified:", modified)
print("Deleted:", deleted)

# Load previously saved fingerprints
old_hashes = load_baseline("baseline.json")

# Scan the folder again
new_hashes = scan_directory("sample_files")

# Compare the results
added, modified, deleted = compare_scans(old_hashes, new_hashes)

print("Added:", added)
print("Modified:", modified)
print("Deleted:", deleted)



if __name__ == "__main__":
    main()












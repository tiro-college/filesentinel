
import hashlib
from pathlib import Path
import json

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

    if command in ("init", 'check'):
        if len(sys.argv) != 4:
            print("Error: Invalid number of arguments.")
            print("Usage: py monitor.py <init|check> <folder_path> <baseline_path>")
            return
        folder_path = sys.argv[2]
        baseline_path = sys.argv[3]


    if command == "init":
        print("Initializing FileSentinel...")

        baseline = Path(baseline_path)

        if baseline.exists():
            print("Error: Baseline already exists.")
            return

        file_hashes = scan_directory(folder_path)
        save_baseline(file_hashes, baseline_path)

        print("Baseline created successfully!")


    
    elif command == "check":
        print("Checking file integrity...")

        try:
            old_hashes = load_baseline(baseline_path)

        except FileNotFoundError:
            print("Error: No baseline found\n 'Run py monitor.py init' first")
            return
        except json.JSONDecodeError:
            print("Error: Baseline file contains invalid JSON.")
            return
        
        new_hashes = scan_directory(folder_path)

        added, modified, deleted = compare_scans(old_hashes, new_hashes)

        print("Added:", added)
        print("Modified:", modified)
        print("Deleted:", deleted)


    else:
        print("Unknown command")

if __name__ == "__main__":
    main()












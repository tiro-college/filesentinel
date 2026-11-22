
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


# Test with our example file
path = Path("sample_files/example.txt")
print(hash_file(path))

import blake3
import os
import json
from pathlib import Path

def hash_file(path):
    h = blake3.blake3()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def compute_merkle_root(file_hashes):
    leaves = sorted(file_hashes.items())
    layer = [blake3.blake3(v.encode()).hexdigest() for k, v in leaves]
    while len(layer) > 1:
        if len(layer) % 2 != 0:
            layer.append(layer[-1])
        layer = [
            blake3.blake3((layer[i] + layer[i+1]).encode()).hexdigest()
            for i in range(0, len(layer), 2)
        ]
    return layer[0]

data_dir = Path("data")
file_hashes = {
    str(f.relative_to(data_dir)): hash_file(f)
    for f in sorted(data_dir.rglob("*")) if f.is_file()
}

merkle_root = compute_merkle_root(file_hashes)

result = {
    "dataset": "veraxis-demo-v1",
    "merkle_root": merkle_root,
    "file_count": len(file_hashes),
    "file_hashes": file_hashes
}

print(json.dumps(result, indent=2))

with open("merkle_manifest.json", "w") as f:
    json.dump(result, f, indent=2)

print("\nMerkle manifest saved to merkle_manifest.json")

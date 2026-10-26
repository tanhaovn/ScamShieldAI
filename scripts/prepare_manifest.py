import hashlib
import random
import csv
from pathlib import Path
from collections import defaultdict

random.seed(42)
dataset_dir = Path("phishing_dataset")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

phish_subdirs = [p for p in (dataset_dir / "phishing").iterdir() if p.is_dir()]
legit_subdirs = [p for p in (dataset_dir / "legitimate").iterdir() if p.is_dir()]
random.shuffle(legit_subdirs)
selected_legit_subdirs = legit_subdirs[:500]

seen_hashes = {}
def collect_from_folders(folders, label):
    groups = defaultdict(list)
    for folder in folders:
        tpl = f"{label}_{folder.name}"
        for p in folder.glob("*"):
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                h = sha256(p)
                if h in seen_hashes:
                    continue
                seen_hashes[h] = (p, tpl, label)
                groups[tpl].append(p)
    return groups

phish_groups = collect_from_folders(phish_subdirs, "phishing")
legit_groups = collect_from_folders(selected_legit_subdirs, "legitimate")

def split_groups(groups, train_ratio=0.7, val_ratio=0.15):
    tpl_keys = sorted(groups.keys())
    random.shuffle(tpl_keys)
    n = len(tpl_keys)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    return set(tpl_keys[:n_train]), set(tpl_keys[n_train:n_train + n_val]), set(tpl_keys[n_train + n_val:])

p_train, p_val, p_test = split_groups(phish_groups)
l_train, l_val, l_test = split_groups(legit_groups)

rows = []
def add_records(group_dict, train_keys, val_keys, test_keys, label):
    for tpl, files in group_dict.items():
        if tpl in train_keys:
            split = "train"
        elif tpl in val_keys:
            split = "validation"
        elif tpl in test_keys:
            split = "test"
        else:
            continue
        source = f"{label}_{split}"
        for f in files:
            rel = f.relative_to(dataset_dir).as_posix()
            rows.append({
                "path": rel,
                "label": label,
                "source": source,
                "template_id": tpl,
                "split": split
            })

add_records(phish_groups, p_train, p_val, p_test, "phishing")
add_records(legit_groups, l_train, l_val, l_test, "legitimate")

out_manifest = dataset_dir / "manifest.csv"
with out_manifest.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["path", "label", "source", "template_id", "split"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully generated {len(rows)} records in {out_manifest}")

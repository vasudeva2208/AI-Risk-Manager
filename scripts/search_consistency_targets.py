import os
import re

base_dir = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager"
exclude_dirs = {".git", ".venv", "node_modules", "dist", ".pytest_cache"}

targets = [
    "54,61,027",
    "5461027",
    "57,87,447",
    "5787447",
    "lower false negative",
    "lower False Negative",
    "lower false-negative",
    "lower False-Negative",
    "lowest false negative",
    "lowest False Negative",
    "fewer false negative",
    "fewer False Negative",
    "893",
]

found = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith((".md", ".py", ".json", ".ts", ".tsx", ".html")) and not file.startswith("search_"):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_dir)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    for t in targets:
                        if t.lower() in line.lower():
                            safe_line = line.strip().encode("ascii", errors="replace").decode("ascii")
                            found.append((rel_path, line_no, t, safe_line))

print(f"Total occurrences found: {len(found)}")
for item in found:
    print(f"{item[0]}:{item[1]} [{item[2]}] -> {item[3]}")

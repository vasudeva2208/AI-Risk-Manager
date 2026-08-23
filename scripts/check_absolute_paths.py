import os
import re

base_dir = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager"
exclude_dirs = {".git", ".venv", "node_modules", "dist", ".pytest_cache"}

path_pattern = re.compile(r'([A-Za-z]:\\[Users|home|tmp][^"\';\s]+)')

findings = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in files:
        if f.endswith((".py", ".ts", ".tsx", ".json", ".yaml", ".yml", ".env", ".example")) and not f.startswith("check_") and not f.startswith("search_") and not f.startswith("audit_"):
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, base_dir)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fo:
                for line_no, line in enumerate(fo, 1):
                    match = path_pattern.search(line)
                    if match:
                        findings.append((rel_path, line_no, match.group(0), line.strip()))

print(f"Absolute Path Check: {len(findings)} issues found.")
for f in findings:
    print(f"{f[0]}:{f[1]} -> {f[2]}")

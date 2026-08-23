import os

patterns = [
    "authorization label",
    "auto-approved",
    "auto-approval",
    "ai decision",
    "ai approved",
    "ai denied",
    "automated approval",
    "automated refund",
    "automatic approval",
]

base_dir = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager"
exclude_dirs = {".git", ".venv", "node_modules", "dist", ".pytest_cache"}

found_instances = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith((".py", ".ts", ".tsx", ".md", ".json", ".html")) and file != "search_terms_extended.py" and file != "search_prohibited_terms.py":
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        lower_line = line.lower()
                        for p in patterns:
                            if p in lower_line:
                                found_instances.append({
                                    "file": os.path.relpath(file_path, base_dir),
                                    "line": line_num,
                                    "term": p,
                                    "content": line.strip()
                                })
            except Exception as e:
                pass

print(f"Total instances found: {len(found_instances)}")
for inst in found_instances:
    print(f"{inst['file']}:{inst['line']} [{inst['term']}] -> {inst['content']}")

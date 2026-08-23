import os

prohibited_terms = [
    "automated authorization label",
    "ai approved",
    "automatically approved",
    "ai authorization",
    "automatic refund approval",
    "automated refund authorization",
    "ai decision",
    "system approved refund",
    "ai denied",
    "automated authorization",
]

base_dir = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager"
exclude_dirs = {".git", ".venv", "node_modules", "dist", ".pytest_cache"}

found_instances = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith((".py", ".ts", ".tsx", ".md", ".json", ".html")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        lower_line = line.lower()
                        for term in prohibited_terms:
                            if term in lower_line:
                                found_instances.append({
                                    "file": os.path.relpath(file_path, base_dir),
                                    "line": line_num,
                                    "term": term,
                                    "content": line.strip()
                                })
            except Exception as e:
                pass

print(f"Total instances found: {len(found_instances)}")
for inst in found_instances:
    print(f"{inst['file']}:{inst['line']} [{inst['term']}] -> {inst['content']}")

import os

patterns = ["ai decision", "ai approved", "ai denied", "auto-approval", "auto-approved", "auto approval", "auto approved"]
frontend_src = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager\\frontend\\src"

for root, dirs, files in os.walk(frontend_src):
    for f in files:
        if f.endswith((".ts", ".tsx")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file_obj:
                for line_no, line in enumerate(file_obj, 1):
                    for p in patterns:
                        if p in line.lower():
                            print(f"{f}:{line_no} [{p}] -> {line.strip()}")

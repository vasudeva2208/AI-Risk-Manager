import os
import re

base_dir = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager"
exclude_dirs = {".git", ".venv", "node_modules", "dist", ".pytest_cache"}

secret_patterns = [
    (re.compile(r'(?i)(api_key|apikey|secret_key|private_key|auth_token|bearer)\s*[:=]\s*["\']([^"\']+)["\']'), "API/Auth Secret"),
    (re.compile(r'(?i)postgres(?:ql)?://([^:]+):([^@]+)@'), "Postgres Credential"),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), "GitHub Personal Token"),
    (re.compile(r'AKIA[0-9A-Z]{16}'), "AWS Access Key"),
    (re.compile(r'AIza[0-9A-Za-z-_]{35}'), "Google API Key"),
]

findings = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for f in files:
        if f.endswith((".py", ".ts", ".tsx", ".js", ".json", ".md", ".env", ".example", ".yaml", ".yml", ".toml")):
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, base_dir)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fo:
                for line_no, line in enumerate(fo, 1):
                    for pat, desc in secret_patterns:
                        match = pat.search(line)
                        if match:
                            val = match.group(0)
                            # Exclude known development placeholders and documentation examples
                            if "change_in_production" in val or "postgres:postgres@localhost" in val or "USER:PASSWORD" in val or "change_this_in_production" in val:
                                continue
                            findings.append((rel_path, line_no, desc, line.strip()))

print(f"Secret Scan Results: {len(findings)} potential issues found.")
for f in findings:
    print(f"{f[0]}:{f[1]} [{f[2]}] -> {f[3][:60]}...")

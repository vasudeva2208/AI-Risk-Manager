import os
import re

frontend_src = "c:\\Users\\rayud\\OneDrive\\Desktop\\AI Risk Manager\\frontend\\src"

gradient_pattern = re.compile(r'(gradient|linear-gradient|bg-gradient)', re.IGNORECASE)
glow_neon_pattern = re.compile(r'(glow|neon|shadow-glow)', re.IGNORECASE)
prohibited_terms = [
    "ai decision",
    "ai approved",
    "ai denied",
    "fraud confirmed",
    "immutable",
    "fraudster",
    "guaranteed savings",
]
hardcoded_metrics = ["75.00", "85.07", "0.7983", "0.9242", "57,87,447", "5787447"]
hover_opacity_pattern = re.compile(r'opacity-0\s+group-hover:opacity-100')

issues = []

for root, dirs, files in os.walk(frontend_src):
    for f in files:
        if f.endswith((".ts", ".tsx", ".css")):
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, frontend_src)
            with open(file_path, "r", encoding="utf-8") as file_obj:
                for line_num, line in enumerate(file_obj, 1):
                    # Check emojis
                    for char in line:
                        if ord(char) > 0x1F300 and ord(char) < 0x1FAFF:
                            issues.append(f"{rel_path}:{line_num} [EMOJI] -> {line.strip()}")

                    # Check gradients
                    if gradient_pattern.search(line):
                        issues.append(f"{rel_path}:{line_num} [GRADIENT] -> {line.strip()}")

                    # Check glow/neon
                    if glow_neon_pattern.search(line):
                        issues.append(f"{rel_path}:{line_num} [GLOW/NEON] -> {line.strip()}")

                    # Check prohibited terms
                    lower_line = line.lower()
                    for term in prohibited_terms:
                        if term in lower_line:
                            issues.append(f"{rel_path}:{line_num} [PROHIBITED TERM: {term}] -> {line.strip()}")

                    # Check hardcoded metrics in TSX markup
                    if f.endswith(".tsx"):
                        for hm in hardcoded_metrics:
                            if hm in line and not line.strip().startswith("//") and not line.strip().startswith("*"):
                                issues.append(f"{rel_path}:{line_num} [HARDCODED METRIC: {hm}] -> {line.strip()}")

                    # Check hover-hidden controls
                    if hover_opacity_pattern.search(line):
                        issues.append(f"{rel_path}:{line_num} [HIDDEN HOVER CONTROL] -> {line.strip()}")

print(f"Total UI issues found: {len(issues)}")
for iss in issues:
    print(iss)

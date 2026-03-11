print("Fixing global baseline + stronger form regression...")

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Fix 1: Find where GLOBAL_GF and GLOBAL_GA are calculated
# Show the relevant section
lines = code.split('\n')
print("=== Finding global baseline code ===")
for i, line in enumerate(lines):
    if 'GLOBAL_GF' in line or 'GLOBAL_GA' in line:
        print(f"  {i+1}: {line.rstrip()}")

# Find the baseline calculation
print("\n=== Lines around baseline ===")
for i, line in enumerate(lines):
    if 'baseline' in line.lower() or 'global' in line.lower():
        start = max(0, i-2)
        for j in range(start, min(i+5, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print()

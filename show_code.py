with open('content_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Lines 120-160 (ranking/blend section) ===")
for i in range(119, min(160, len(lines))):
    print(f"  {i+1}: {lines[i].rstrip()}")

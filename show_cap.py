with open('content_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Lines 155-175 (star + cap section) ===")
for i in range(154, min(175, len(lines))):
    print(f"  {i+1}: {lines[i].rstrip()}")

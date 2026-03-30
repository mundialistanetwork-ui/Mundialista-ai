with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print("Total lines:", len(lines))
for i in range(max(0, 465), min(len(lines), 490)):
    print(str(i+1) + ": " + repr(lines[i].rstrip()))

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

count = content.count('use_container_width=True')
content = content.replace('use_container_width=True', "width='stretch'")
print("Fixed " + str(count) + " deprecation warnings")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

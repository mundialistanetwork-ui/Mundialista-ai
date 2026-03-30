with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the admin panel section and the else block
# The admin panel (with st.sidebar) needs to go AFTER the if/else, not BETWEEN them

# Find where admin panel starts
admin_start = content.find("# === SIDEBAR: Admin Panel ===")
if admin_start == -1:
    admin_start = content.find("with st.sidebar:")

# Find the else block that follows it
else_block_start = content.find("\nelse:\n", admin_start)

if admin_start > -1 and else_block_start > -1:
    # Extract admin panel code
    admin_code = content[admin_start:else_block_start]
    
    # Remove admin panel from current position
    content = content[:admin_start] + content[else_block_start:]
    
    # Now put admin panel at the very end
    content = content.rstrip() + "\n\n" + admin_code + "\n"
    
    print("Moved admin panel after if/else block")
else:
    print("Could not find admin panel or else block")
    print("admin_start:", admin_start)
    print("else_block_start:", else_block_start)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Lines:", len(content.splitlines()))

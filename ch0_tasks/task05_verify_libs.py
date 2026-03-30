"""
Task 05: Verify all libraries are installed correctly.
"""
libraries = {
    "numpy": "numpy",
    "scipy": "scipy", 
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "streamlit": "streamlit",
    "pymc": "pymc",
    "arviz": "arviz",
    "pytensor": "pytensor",
}

print("=" * 50)
print("MUNDIALISTA AI — Library Verification")
print("=" * 50)

all_ok = True
for name, import_name in libraries.items():
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"  ✅ {name:<15} version {version}")
    except ImportError as e:
        print(f"  ❌ {name:<15} FAILED — {e}")
        all_ok = False

print("=" * 50)
if all_ok:
    print("🎉 ALL LIBRARIES INSTALLED SUCCESSFULLY!")
else:
    print("⚠️  Some libraries failed. Re-run: pip install -r requirements.txt")
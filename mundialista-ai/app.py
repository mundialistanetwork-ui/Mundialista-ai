import runpy
import os
import sys

here = os.path.dirname(__file__)
root_dir = os.path.normpath(os.path.join(here, ".."))
root_app = os.path.join(root_dir, "app.py")

if not os.path.exists(root_app):
    raise FileNotFoundError(f"Expected root app at {root_app} not found")

# Ensure root directory is in Python path so imports work
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Execute the root app as __main__ so CLI entrypoints behave the same.
runpy.run_path(root_app, run_name="__main__")

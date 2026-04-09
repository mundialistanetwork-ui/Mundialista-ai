import kagglehub
import pandas as pd
import shutil
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

print("Downloading football data from Kaggle...")
path = Path(kagglehub.dataset_download(
    "martj42/international-football-results-from-1872-to-2017"))
print(f"Downloaded to: {path}")

for f in ["results.csv", "goalscorers.csv", "shootouts.csv", "rankings.csv"]:
    src = path / f
    if src.exists():
        shutil.copy2(src, DATA_DIR / f)
        print(f"  Copied: {f}")

df = pd.read_csv(DATA_DIR / "results.csv", parse_dates=["date"])
print(f"\nTotal matches: {len(df):,}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")

print("\nData downloaded. Running auto-updates...")

# Auto-run rankings update
print("\n" + "=" * 60)
print("AUTO-RUNNING: update_rankings.py")
print("=" * 60)
subprocess.run([sys.executable, "update_rankings.py"])

# Auto-run star player builder v2
print("\n" + "=" * 60)
print("AUTO-RUNNING: star_player_builder_v2.py")
print("=" * 60)
subprocess.run([sys.executable, "star_player_builder_v2.py"])

print("\n" + "=" * 60)
print("ALL DONE! Data + Rankings + Star Players updated.")
print("=" * 60)

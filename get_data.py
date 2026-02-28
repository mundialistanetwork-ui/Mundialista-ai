import kagglehub
import pandas as pd
import shutil
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
print(f"\nDONE! Now run: python data_loader.py")
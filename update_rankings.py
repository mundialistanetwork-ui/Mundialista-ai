import kagglehub
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def download_kaggle_rankings():
    try:
        import kagglehub
    except ImportError:
        print("  kagglehub not installed")
        return None

    print("  Downloading davidcariboo/player-scores...")
    try:
        dataset_path = Path(kagglehub.dataset_download("davidcariboo/player-scores"))
    except Exception as e:
        print(f"  Kaggle download failed: {e}")
        return None

    nt_files = list(dataset_path.rglob("national_teams.csv"))
    if not nt_files:
        print("  national_teams.csv not found!")
        return None

    df = pd.read_csv(nt_files[0])
    df = df.dropna(subset=["fifa_ranking"])
    df["fifa_ranking"] = df["fifa_ranking"].astype(int)

    NAME_FIXES = {
        "Korea, South": "South Korea",
        "Korea Republic": "South Korea",
        "Korea, North": "North Korea",
        "Cote d Ivoire": "Ivory Coast",
        "Cabo Verde": "Cape Verde",
        "Czechia": "Czech Republic",
        "Turkiye": "Turkey",
        "Bosnia-Herzegovina": "Bosnia and Herzegovina",
        "USA": "United States",
        "IR Iran": "Iran",
        "China": "China PR",
        "Congo DR": "DR Congo",
    }
    df["country_name"] = df["country_name"].replace(NAME_FIXES)

    result = pd.DataFrame({
        "rank": df["fifa_ranking"].values,
        "country_full": df["country_name"].values,
        "confederation": df["confederation"].values,
        "market_value": df["total_market_value"].values,
        "squad_size": df["squad_size"].values,
        "average_age": df["average_age"].values,
        "source": "kaggle_fifa",
    })
    result = result.sort_values("rank").reset_index(drop=True)
    result = result.drop_duplicates(subset=["country_full"], keep="first")

    print("  " + str(len(result)) + " teams with official FIFA rankings")
    return result


def classify_tournament(name):
    t = str(name).lower()
    if "world cup" in t and "qualif" not in t: return 60
    if "world cup" in t: return 40
    if any(x in t for x in ["copa am", "euro ", "european championship",
        "uefa euro", "african cup", "africa cup", "asian cup",
        "gold cup", "concacaf nations"]): return 50
    if "nations league" in t: return 35
    if "qualif" in t: return 40
    return 20


def build_elo_rankings():
    rpath = DATA_DIR / "results.csv"
    if not rpath.exists():
        print("  results.csv not found!")
        return pd.DataFrame()

    df = pd.read_csv(rpath)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    print("  Processing " + str(len(df)) + " matches...")

    teams = set(df["home_team"].unique()) | set(df["away_team"].unique())
    elo = {t: 1500.0 for t in teams}

    for _, row in df.iterrows():
        h, a = row["home_team"], row["away_team"]
        hs, aws = row["home_score"], row["away_score"]
        if pd.isna(hs) or pd.isna(aws):
            continue
        hs, aws = int(hs), int(aws)

        k = classify_tournament(row.get("tournament", "Friendly"))
        neutral = bool(row.get("neutral", False))
        h_elo = elo[h] + (0 if neutral else 100)
        a_elo = elo[a]

        exp_h = 1.0 / (1.0 + 10 ** ((a_elo - h_elo) / 400.0))

        if hs > aws:   act = 1.0
        elif hs < aws: act = 0.0
        else:          act = 0.5

        gd = abs(hs - aws)
        if gd <= 1: w = 1.0
        elif gd == 2: w = 1.5
        elif gd == 3: w = 1.75
        else: w = 1.75 + (gd - 3) * 0.5

        elo[h] += k * w * (act - exp_h)
        elo[a] += k * w * ((1.0 - act) - (1.0 - exp_h))

    rows = [{"country_full": t, "elo": round(r, 1)} for t, r in elo.items()]
    result = pd.DataFrame(rows).sort_values("elo", ascending=False).reset_index(drop=True)
    result["rank"] = result.index + 1
    result["source"] = "elo_calculated"
    print("  ELO computed for " + str(len(result)) + " teams")
    return result


def update_rankings(force_elo=False):
    print("")
    print("=" * 60)
    print("MUNDIALISTA AI  Rankings Update")
    print("=" * 60)

    kaggle = None
    if not force_elo:
        print("")
        print("Layer 1: Kaggle FIFA Rankings")
        kaggle = download_kaggle_rankings()

    print("")
    print("Layer 2: ELO from match history")
    elo = build_elo_rankings()

    if kaggle is not None and not kaggle.empty:
        kaggle_teams = set(kaggle["country_full"])
        elo_only = elo[~elo["country_full"].isin(kaggle_teams)].copy()
        max_rank = kaggle["rank"].max()
        elo_only = elo_only.sort_values("elo", ascending=False).reset_index(drop=True)
        elo_only["rank"] = range(max_rank + 1, max_rank + 1 + len(elo_only))

        elo_lookup = dict(zip(elo["country_full"], elo["elo"]))
        kaggle["elo"] = kaggle["country_full"].map(elo_lookup)

        merged = pd.concat([kaggle, elo_only], ignore_index=True)
        merged = merged.sort_values("rank").reset_index(drop=True)
        print("")
        print("Merged: " + str(len(kaggle)) + " FIFA + " + str(len(elo_only)) + " ELO-only = " + str(len(merged)) + " total")
    elif not elo.empty:
        merged = elo
        print("")
        print("Using ELO only: " + str(len(merged)) + " teams")
    else:
        print("FATAL: No rankings generated!")
        return pd.DataFrame()

    merged["updated"] = datetime.now().isoformat()

    out = DATA_DIR / "rankings.csv"
    merged.to_csv(out, index=False)
    print("")
    print("Saved: " + str(out))

    print("")
    print("Top 20:")
    for _, r in merged.head(20).iterrows():
        print("  #" + str(r["rank"]) + " " + str(r["country_full"]))

    print("")
    print("WC 2026 Teams:")
    for t in ["Argentina","Brazil","France","England","Spain","Germany",
              "United States","Mexico","Canada","Japan","South Korea",
              "Morocco","Senegal","Croatia","Uruguay","Colombia"]:
        row = merged[merged["country_full"] == t]
        if not row.empty:
            print("  " + t + " -> rank " + str(int(row.iloc[0]["rank"])))
        else:
            print("  " + t + " -> NOT FOUND")

    return merged


if __name__ == "__main__":
    force = "--elo" in sys.argv
    r = update_rankings(force_elo=force)
    if not r.empty:
        print("")
        print("=" * 60)
        print("Rankings ready! No more rank 100!")
        print("=" * 60)
    else:
        sys.exit(1)

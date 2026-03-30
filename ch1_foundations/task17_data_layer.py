"""
Task 17: Data Layer — Extract Team Statistics from Match History
================================================================
"""
import pandas as pd
import numpy as np

# ── PART A: Create the example dataset ─────────────────────────
data = {
    "team": ["Jamaica"]*9 + ["New Caledonia"]*9,
    "opponent": [
        "Honduras", "Mexico", "Costa Rica", "Panama", "Canada",
        "Trinidad", "El Salvador", "New Caledonia", "New Caledonia",
        "Fiji", "Tahiti", "Vanuatu", "Solomon Islands", "Papua NG",
        "Samoa", "Tonga", "Jamaica", "Jamaica",
    ],
    "goals_for": [1, 0, 2, 1, 0, 3, 2, 2, 1,
                  1, 0, 2, 1, 0, 1, 3, 1, 0],
    "goals_against": [0, 1, 1, 1, 2, 0, 0, 1, 0,
                      1, 2, 1, 0, 4, 1, 0, 2, 1],
    "is_home": [1, 0, 1, 0, 0, 1, 1, 1, 0,
                1, 0, 1, 0, 0, 1, 1, 0, 1],
    "match_date": [
        "2024-06-01", "2024-06-08", "2024-03-22", "2024-03-18",
        "2024-01-15", "2023-11-20", "2023-11-16", "2024-07-01",
        "2024-07-15",
        "2024-05-10", "2024-05-03", "2024-04-12", "2024-04-05",
        "2024-02-20", "2023-12-10", "2023-12-05", "2024-07-01",
        "2024-07-15",
    ],
}

df = pd.DataFrame(data)
df["match_date"] = pd.to_datetime(df["match_date"])

print("=== FULL DATASET ===")
print(df.to_string())
print(f"\nShape: {df.shape}")

# ── PART B: Write get_team_stats() ─────────────────────────────
def get_team_stats(df: pd.DataFrame, team: str,
                   opponent: str) -> dict:
    """
    Extract statistics for a team from their match history.
    """
    team_df = df[df["team"] == team]
    
    # Regular matches (not H2H)
    regular = team_df[team_df["opponent"] != opponent]
    
    # H2H matches
    h2h = team_df[team_df["opponent"] == opponent]
    
    # Regular stats
    if len(regular) > 0:
        avg_gf = regular["goals_for"].mean()
        avg_ga = regular["goals_against"].mean()
        std_gf = regular["goals_for"].std()
        std_ga = regular["goals_against"].std()
        n_matches = len(regular)
        home_pct = regular["is_home"].mean()
    else:
        avg_gf = 1.0
        avg_ga = 1.0
        std_gf = 0.5
        std_ga = 0.5
        n_matches = 0
        home_pct = 0.5
    
    # Handle NaN std (happens with 1 match)
    if pd.isna(std_gf) or std_gf == 0:
        std_gf = 0.5
    if pd.isna(std_ga) or std_ga == 0:
        std_ga = 0.5
    
    # H2H stats
    if len(h2h) > 0:
        h2h_gf = h2h["goals_for"].mean()
        h2h_ga = h2h["goals_against"].mean()
    else:
        h2h_gf = avg_gf
        h2h_ga = avg_ga
    
    return {
        "avg_gf": avg_gf,
        "avg_ga": avg_ga,
        "std_gf": std_gf,
        "std_ga": std_ga,
        "n_matches": n_matches,
        "h2h_gf": h2h_gf,
        "h2h_ga": h2h_ga,
        "home_pct": home_pct,
    }

# ── PART C: Test with both teams ───────────────────────────────
print("\n=== JAMAICA STATS ===")
jamaica_stats = get_team_stats(df, "Jamaica", "New Caledonia")
for key, val in jamaica_stats.items():
    print(f"  {key}: {val:.3f}")

print("\n=== NEW CALEDONIA STATS ===")
newcal_stats = get_team_stats(df, "New Caledonia", "Jamaica")
for key, val in newcal_stats.items():
    print(f"  {key}: {val:.3f}")

# ── PART D: Edge cases ─────────────────────────────────────────
print("\n=== EDGE CASE: No H2H matches ===")
no_h2h_stats = get_team_stats(df, "Jamaica", "Brazil")
print(f"  H2H goals for: {no_h2h_stats['h2h_gf']:.3f} (defaults to avg_gf)")
print(f"  H2H goals against: {no_h2h_stats['h2h_ga']:.3f} (defaults to avg_ga)")

# Test with minimal data
print("\n=== EDGE CASE: Minimal data ===")
small_df = pd.DataFrame({
    "team": ["TestTeam", "TestTeam"],
    "opponent": ["OpponentA", "OpponentB"],
    "goals_for": [2, 3],
    "goals_against": [1, 0],
    "is_home": [1, 0],
    "match_date": pd.to_datetime(["2024-01-01", "2024-01-08"]),
})
small_stats = get_team_stats(small_df, "TestTeam", "OpponentC")
print(f"  avg_gf: {small_stats['avg_gf']:.3f}")
print(f"  n_matches: {small_stats['n_matches']}")
print("  ✅ No crash with minimal data!")

# ── PART E: CSV placeholder ────────────────────────────────────
def load_data_from_csv(path: str) -> pd.DataFrame:
    """Try to load CSV, fall back to example data."""
    try:
        loaded_df = pd.read_csv(path)
        loaded_df["match_date"] = pd.to_datetime(loaded_df["match_date"])
        print(f"✅ Loaded data from {path}")
        return loaded_df
    except FileNotFoundError:
        print(f"⚠️ File '{path}' not found. Using example data.")
        return df

print("\n=== CSV LOADER TEST ===")
test_df = load_data_from_csv("nonexistent.csv")
print(f"  Loaded {len(test_df)} rows")
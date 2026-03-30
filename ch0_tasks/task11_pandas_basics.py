"""
Task 11: Pandas Fundamentals
=============================
"""
import pandas as pd
import numpy as np

# ── PART A: Create a DataFrame from scratch ────────────────────
data = {
    "opponent": ["Honduras", "Mexico", "Costa Rica", "Panama",
                 "Canada", "Trinidad and Tobago", "El Salvador"],
    "goals_for": [1, 0, 2, 1, 0, 3, 2],
    "goals_against": [0, 1, 1, 1, 2, 0, 0],
    "is_home": [1, 0, 1, 0, 0, 1, 1],
    "match_date": ["2024-06-01", "2024-06-08", "2024-03-22",
                   "2024-03-18", "2024-01-15", "2023-11-20",
                   "2023-11-16"],
}

df = pd.DataFrame(data)
df["match_date"] = pd.to_datetime(df["match_date"])

print("=== FULL DATAFRAME ===")
print(df)
print(f"\nShape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Data types:\n{df.dtypes}")

# ── PART B: Accessing data ─────────────────────────────────────
print("\n=== ACCESSING DATA ===")
print(f"Goals for: {df['goals_for'].values}")
print(f"\nFirst match:\n{df.iloc[0]}")
print(f"\nScores only:\n{df[['goals_for', 'goals_against']]}")

# ── PART C: Filtering rows ─────────────────────────────────────
print("\n=== FILTERING ===")
home_matches = df[df["is_home"] == 1]
print(f"Home matches:\n{home_matches}")

big_wins = df[df["goals_for"] >= 2]
print(f"\nMatches with 2+ goals:\n{big_wins}")

vs_mexico = df[df["opponent"] == "Mexico"]
print(f"\nVs Mexico:\n{vs_mexico}")

# ── PART D: Computing statistics ───────────────────────────────
print("\n=== STATISTICS ===")
print(f"Average goals scored: {df['goals_for'].mean():.2f}")
print(f"Average goals conceded: {df['goals_against'].mean():.2f}")
print(f"Total goals scored: {df['goals_for'].sum()}")
print(f"Std dev of goals: {df['goals_for'].std():.2f}")

wins = df[df["goals_for"] > df["goals_against"]]
win_rate = len(wins) / len(df)
print(f"Win rate: {win_rate:.1%}")

# ── PART E: Sorting ────────────────────────────────────────────
print("\n=== SORTING ===")
sorted_df = df.sort_values("match_date", ascending=False)
print(sorted_df[["opponent", "match_date"]])

last_3 = sorted_df.head(3)
print(f"\nLast 3 opponents: {last_3['opponent'].tolist()}")

# ── PART F: Adding columns ─────────────────────────────────────
print("\n=== NEW COLUMNS ===")
df["result"] = np.where(
    df["goals_for"] > df["goals_against"], "W",
    np.where(df["goals_for"] == df["goals_against"], "D", "L")
)
df["goal_diff"] = df["goals_for"] - df["goals_against"]

print(df[["opponent", "goals_for", "goals_against",
          "result", "goal_diff"]])

# ── PART G: Connecting to our engine ────────────────────────────
print("\nI understand that our engine's data layer is just "
      "Pandas filtering and statistics!")
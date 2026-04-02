with open('prediction_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# === FIX 1: Patch load_results to merge recent ===
old_results = '''    try:
        df = pd.read_csv("data/results.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        _results_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()'''

new_results = '''    try:
        df = pd.read_csv("data/results.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        try:
            recent = pd.read_csv("data/recent_results.csv")
            if not recent.empty:
                if "date" in recent.columns:
                    recent["date"] = pd.to_datetime(recent["date"], errors="coerce")
                df = pd.concat([df, recent], ignore_index=True)
                df = df.drop_duplicates(subset=["date", "home_team", "away_team"], keep="last")
                df = df.sort_values("date").reset_index(drop=True)
        except FileNotFoundError:
            pass
        _results_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()'''

if old_results in content:
    content = content.replace(old_results, new_results)
    print("  [1] load_results() now merges recent_results.csv")
    changes += 1
else:
    print("  [1] WARN: Could not match load_results block")

# === FIX 2: Patch load_goalscorers to merge recent ===
old_gs = '''    try:
        df = pd.read_csv("data/goalscorers.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        _goalscorers_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()'''

new_gs = '''    try:
        df = pd.read_csv("data/goalscorers.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        try:
            recent = pd.read_csv("data/recent_goalscorers.csv")
            if not recent.empty:
                if "date" in recent.columns:
                    recent["date"] = pd.to_datetime(recent["date"], errors="coerce")
                df = pd.concat([df, recent], ignore_index=True)
                df = df.drop_duplicates(subset=["date", "team", "scorer", "minute"], keep="last")
                df = df.sort_values("date").reset_index(drop=True)
        except FileNotFoundError:
            pass
        _goalscorers_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()'''

if old_gs in content:
    content = content.replace(old_gs, new_gs)
    print("  [2] load_goalscorers() now merges recent_goalscorers.csv")
    changes += 1
else:
    print("  [2] WARN: Could not match load_goalscorers block")

with open('prediction_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("\nChanges: " + str(changes))

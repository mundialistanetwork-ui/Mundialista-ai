"""
Mundialista AI - FIFA Rankings Auto-Updater
Fetches latest rankings from FIFA API or fallback sources.
Run: python update_rankings.py
"""
import pandas as pd
import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RANKINGS_CSV = os.path.join(DATA_DIR, "rankings.csv")

def fetch_rankings_from_api():
    """Try to fetch from FIFA API"""
    try:
        import urllib.request
        url = "https://www.fifa.com/fifa-world-ranking/ranking-table/men/rank/ranking.json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read())
        print(f"Fetched {len(data)} entries from FIFA API")
        return data
    except Exception as e:
        print(f"FIFA API failed: {e}")
        return None

def fetch_rankings_from_scrape():
    """Fallback: try unofficial API"""
    try:
        import urllib.request
        url = "https://raw.githubusercontent.com/martj42/international_results/master/rankings.csv"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode("utf-8")
        
        # Save raw and parse
        lines = content.strip().split("\n")
        if len(lines) > 10:
            # Write to temp file and read with pandas
            temp_path = os.path.join(DATA_DIR, "rankings_raw.csv")
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            df = pd.read_csv(temp_path)
            print(f"Fetched {len(df)} ranking entries from GitHub source")
            
            # Get latest date only
            if "rank_date" in df.columns:
                latest_date = df["rank_date"].max()
                df = df[df["rank_date"] == latest_date]
                print(f"Latest ranking date: {latest_date}, {len(df)} teams")
            
            os.remove(temp_path)
            return df
        return None
    except Exception as e:
        print(f"GitHub scrape failed: {e}")
        return None

def update_rankings():
    """Main update function"""
    print(f"Updating FIFA rankings...")
    print(f"Current file: {RANKINGS_CSV}")
    
    if os.path.exists(RANKINGS_CSV):
        current = pd.read_csv(RANKINGS_CSV)
        print(f"Current rankings: {len(current)} teams")
        if "rank_date" in current.columns:
            print(f"Current date: {current['rank_date'].iloc[0]}")
    
    # Try sources in order
    new_data = fetch_rankings_from_scrape()
    
    if new_data is not None and isinstance(new_data, pd.DataFrame) and len(new_data) > 50:
        # Standardize columns
        col_map = {}
        for col in new_data.columns:
            cl = col.lower().strip()
            if "rank" == cl or cl == "ranking":
                col_map[col] = "rank"
            elif "country" in cl or "team" in cl or "country_full" in cl:
                col_map[col] = "country_full"
            elif "point" in cl or "total" in cl:
                col_map[col] = "total_points"
            elif "abrv" in cl or "abr" in cl or "code" in cl:
                col_map[col] = "country_abrv"
            elif "confed" in cl:
                col_map[col] = "confederation"
            elif "date" in cl:
                col_map[col] = "rank_date"
        
        new_data = new_data.rename(columns=col_map)
        
        # Ensure required columns
        for req in ["rank", "country_full", "total_points"]:
            if req not in new_data.columns:
                print(f"Missing column: {req}")
                print(f"Available: {list(new_data.columns)}")
                return False
        
        for opt in ["country_abrv", "confederation", "rank_date"]:
            if opt not in new_data.columns:
                new_data[opt] = ""
        
        new_data = new_data.sort_values("rank").reset_index(drop=True)
        
        # Backup old file
        if os.path.exists(RANKINGS_CSV):
            backup = RANKINGS_CSV.replace(".csv", "_backup.csv")
            current.to_csv(backup, index=False)
            print(f"Backup saved: {backup}")
        
        new_data.to_csv(RANKINGS_CSV, index=False)
        print(f"\nUpdated! {len(new_data)} teams saved to {RANKINGS_CSV}")
        print(f"Top 10:")
        print(new_data.head(10)[["rank", "country_full", "total_points"]].to_string(index=False))
        return True
    else:
        print("\nCould not fetch new rankings. Keeping current file.")
        return False

def verify_rankings():
    """Quick check that rankings are working"""
    if not os.path.exists(RANKINGS_CSV):
        print("No rankings file!")
        return False
    
    df = pd.read_csv(RANKINGS_CSV)
    print(f"\nVerification:")
    print(f"  Teams: {len(df)}")
    print(f"  Rank range: {df['rank'].min()} - {df['rank'].max()}")
    
    # Check key teams
    key_teams = ["Argentina", "Brazil", "France", "Germany", "Mexico", "Bolivia", "Suriname"]
    for team in key_teams:
        row = df[df["country_full"] == team]
        if len(row) > 0:
            print(f"  {team}: rank={row.iloc[0]['rank']}, pts={row.iloc[0]['total_points']:.0f}")
        else:
            print(f"  {team}: NOT FOUND")
    
    return True

if __name__ == "__main__":
    import sys
    if "--verify" in sys.argv:
        verify_rankings()
    else:
        success = update_rankings()
        verify_rankings()
        if success:
            print("\nDone! Rankings updated successfully.")
        else:
            print("\nUsing existing rankings.")

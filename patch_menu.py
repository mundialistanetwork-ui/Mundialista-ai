path = "content_automation.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

start_marker = "def interactive_menu():"
end_marker = 'if __name__ == "__main__":'

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find markers")
    exit()

before = text[:start_idx]
after = text[end_idx:]

new_menu = """def interactive_menu():
    I = ICONS
    sep = I["DSEP"]
    line = "-" * 50

    print("")
    print(sep)
    print("  " + I["BALL"] + " MUNDIALISTA AI -- Content Generator v3")
    print("  " + I["CHART"] + " " + str(len(get_all_teams())) + " Teams | Dixon-Coles Poisson Engine")
    print(sep)

    while True:
        print("")
        print("  " + line)
        print("  " + I["MEMO"] + " CONTENT MENU:")
        print("  " + line)
        print("   1. " + I["GB"] + " Match Preview (English)")
        print("   2. " + I["ES"] + " Match Preview (Espanol)")
        print("   3. " + I["BIRD"] + " Twitter/X Thread")
        print("   4. " + I["ALERT"] + " Underdog Alert Check")
        print("   5. " + I["ZAP"] + " Quick Head-to-Head")
        print("  " + line)
        print("  " + I["TROPHY"] + " WORLD CUP 2026:")
        print("  " + line)
        print("   6. " + I["CHART"] + " Predict One Group (A-L)")
        print("   7. " + I["GLOBE"] + " Predict ALL Groups")
        print("  " + line)
        print("  BROADCAST TOOLS:")
        print("  " + line)
        print("   8. Winner Meter")
        print("   9. " + I["BOT"] + " Commentator Intro")
        print("  10. Lower Third Graphic")
        print("  11. Chaos Meter")
        print("  12. Key Battle")
        print("  13. Top 5 Storylines")
        print("  14. Star Impact Card")
        print("  15. " + I["BRAIN"] + " AI Verdict")
        print("  16. Producer Notes")
        print("  17. Headline Pack")
        print("  18. On-Air Tease")
        print("  19. " + I["TARGET"] + " Match Card")
        print("  20. Three Keys to the Match")
        print("  21. " + I["ALERT"] + " Upset Scale")
        print("  22. Scoreline Panel")
        print("  23. Full Broadcast Pack")
        print("  " + line)
        print("  24. " + I["LIST"] + " Show All Teams")
        print("  25. " + I["EXIT"] + " Exit")
        print("  " + line)

        choice = input("  Select (1-25): ").strip()

        if choice == "25":
            print("")
            print("  " + I["BALL"] + " Hasta la vista! Follow @MundialistaNetwork & @Mundialist4109 on X")
            break

        elif choice == "24":
            show_teams()

        elif choice == "6":
            grp = input("  Enter group letter (A-L): ").strip().upper()
            result = predict_wc2026_group(grp)
            if result:
                save_q = input("  Save results to JSON? (y/n): ").strip().lower()
                if save_q == "y":
                    save_group_predictions({grp: result})

        elif choice == "7":
            results = predict_all_wc2026_groups()
            save_q = input("  Save all results to JSON? (y/n): ").strip().lower()
            if save_q == "y":
                save_group_predictions(results)

        elif choice == "5":
            home = select_team("  Home team: ")
            away = select_team("  Away team: ")
            neutral_q = input("  Neutral venue? (y/n, default y): ").strip().lower()
            is_neutral = neutral_q != "n"
            print("  " + I["BRAIN"] + " Analyzing " + home + " vs " + away + "...")
            a = analyze_match(home, away, neutral=is_neutral)
            print("")
            print("  " + sep)
            print("  " + home + " vs " + away)
            print("  " + line)
            print("  " + home + ": " + str(round(a["home_win_pct"], 1)) + "%  |  Draw: " + str(round(a["draw_pct"], 1)) + "%  |  " + away + ": " + str(round(a["away_win_pct"], 1)) + "%")
            print("  xG: " + home + " " + str(round(a["home_exp"], 2)) + " vs " + str(round(a["away_exp"], 2)) + " " + away)
            if a["top5_scorelines"]:
                ts = a["top5_scorelines"][0]
                print("  " + I["TARGET"] + " Most likely: " + str(ts[0]) + " (" + str(round(ts[1], 1)) + "%)")
            print("  " + sep)

        elif choice in ["1", "2", "3", "4"]:
            home = select_team("  Home team (name or number): ")
            away = select_team("  Away team: ")
            print("  " + I["BRAIN"] + " Running prediction: " + home + " vs " + away + "...")
            a = analyze_match(home, away)
            print("")
            print(sep)
            if choice == "1":
                print("  " + I["GB"] + " ENGLISH PREVIEW:")
                print(sep)
                print(generate_match_preview(home, away, a))
            elif choice == "2":
                print("  " + I["ES"] + " PREVIEW EN ESPANOL:")
                print(sep)
                print(generate_spanish_preview(home, away, a))
            elif choice == "3":
                print("  " + I["BIRD"] + " TWITTER/X THREAD:")
                print(sep)
                thread = generate_twitter_thread(home, away, a)
                for i, tweet in enumerate(thread, 1):
                    print("  " + line)
                    print("  Tweet " + str(i) + "/" + str(len(thread)) + " (" + str(len(tweet)) + " chars):")
                    print("  " + line)
                    print("  " + tweet)
            elif choice == "4":
                alert = generate_underdog_alert(home, away, a)
                if alert:
                    print("  " + I["ALERT"] + " UNDERDOG ALERT:")
                    print(sep)
                    print("  " + alert)
                else:
                    print("  " + I["OK"] + " No upset alert -- " + a["favourite"] + " is a clear favorite (" + str(round(a["upset_prob"], 1)) + "% upset chance)")
                print(sep)
            print("  Content ready! Copy the text above.")

        elif choice in [str(i) for i in range(8, 24)]:
            home = select_team("  Home team (name or number): ")
            away = select_team("  Away team: ")
            print("  " + I["BRAIN"] + " Running prediction: " + home + " vs " + away + "...")
            a = analyze_match(home, away)
            print("")
            print(sep)
            if choice == "8":
                print("  WINNER METER:")
                print(sep)
                print(bf.generate_winner_meter(home, away, a))
            elif choice == "9":
                print("  COMMENTATOR INTRO:")
                print(sep)
                print(bf.generate_commentator_intro(home, away, a))
            elif choice == "10":
                print("  LOWER THIRD GRAPHIC:")
                print(sep)
                print(bf.generate_lower_third(home, away, a))
            elif choice == "11":
                print("  CHAOS METER:")
                print(sep)
                print(bf.generate_chaos_meter(home, away, a))
            elif choice == "12":
                print("  KEY BATTLE:")
                print(sep)
                print(bf.generate_key_battle(home, away, a))
            elif choice == "13":
                print("  TOP 5 STORYLINES:")
                print(sep)
                print(bf.generate_storylines(home, away, a))
            elif choice == "14":
                print("  STAR IMPACT CARD:")
                print(sep)
                print(bf.generate_star_impact_card(home, away, resolve_team_name, get_team_star_impact))
            elif choice == "15":
                print("  AI VERDICT:")
                print(sep)
                print(bf.generate_prediction_verdict(home, away, a))
            elif choice == "16":
                print("  PRODUCER NOTES:")
                print(sep)
                print(bf.generate_producer_notes(home, away, a))
            elif choice == "17":
                print("  HEADLINE PACK:")
                print(sep)
                print(bf.generate_headline_pack(home, away, a))
            elif choice == "18":
                print("  ON-AIR TEASE:")
                print(sep)
                print(bf.generate_on_air_tease(home, away, a))
            elif choice == "19":
                print("  MATCH CARD:")
                print(sep)
                print(bf.generate_match_card(home, away, a))
            elif choice == "20":
                print("  THREE KEYS TO THE MATCH:")
                print(sep)
                print(bf.generate_three_keys(home, away, a))
            elif choice == "21":
                print("  UPSET SCALE:")
                print(sep)
                print(bf.generate_upset_scale(home, away, a))
            elif choice == "22":
                print("  SCORELINE PANEL:")
                print(sep)
                print(bf.generate_scoreline_panel(home, away, a))
            elif choice == "23":
                print("  FULL BROADCAST PACK:")
                print(sep)
                print(bf.generate_full_broadcast_pack(home, away, a))
            print("  Broadcast content ready!")

        else:
            print("  Invalid option. Enter 1-25.")


"""

text = before + new_menu + "\n\n" + after

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("Menu replaced successfully")

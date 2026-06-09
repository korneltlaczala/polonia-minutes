from mincal.objects import Club

def get_team_minutes_by_league_df(team, show_zeros=False):
    """
    Tworzy DataFrame z minutami zawodników w poszczególnych ligach.
    
    :param team: Obiekt drużyny, dla której generujemy dane.
    :param show_zeros: Jeśli True, pokazuje również ligi, w których zawodnicy nie grali (minuty = 0).
    :return: DataFrame z kolumnami: 'player_id', 'player_name', 'league', 'minutes'.
    """
    import pandas as pd
    data = []
    
    for player in team.players:
        player_row = {
                "player_id": player.id,
                "firstname": player.firstname,
                "lastname": player.lastname,
            }
        for app in player.appearances:
            league_name = app.league.name
            row = {
                **player_row,
                "league": league_name,
                "duration": app.duration,
                "minute_in": app.minute_in,     
                "minute_out": app.minute_out,
                "app_type": app.app_type,
                "number": app.number,
                "isCaptain": app.isCaptain,
                "isKeeper": app.isKeeper,
                "isJunior": app.isJunior,
                "goals": app.goals,
                "cards": app.cards,
                "played": app.played
            }
            data.append(row)

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    # 1. Inicjalizacja klubu i załadowanie statystyk z plików JSON
    club = Club("Polonia Warszawa", "polonia")
    club.prep_stats()
    
    # 2. Wybór drużyny (bierzemy pierwszą dostępną z listy)
    if club.teams:
        team = club.teams[4]
        print(f"Generowanie danych dla zespołu: {team.category_age}...")
        
        # 3. Wywołanie funkcji tworzącej DataFrame
        df_stats = get_team_minutes_by_league_df(team, show_zeros=True)
        
        # 4. ZAPISYWANIE PLIKÓW (Wybierz format, który Ci najbardziej odpowiada):
        
        # Opcja B: Zapis do CSV (standard, np. do dalszej obróbki w Pythonie/R)
        csv_path = f"minute_stats_{team.category_age}.csv"
        df_stats.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")
        print(f"[OK] Zapisano do CSV: {csv_path}")
        
    else:
        print("Nie znaleziono żadnych zespołów w klubie.")
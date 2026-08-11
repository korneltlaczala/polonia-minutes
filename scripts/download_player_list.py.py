from mincal.objects import Club

def get_player_list_df(team, league_name=None, show_zeros=False):
    """
    Tworzy DataFrame z listą zawodników w drużynie.
    
    :param team: Obiekt drużyny, dla której generujemy dane.
    :param league_name: Nazwa ligi, dla której filtrujemy dane. Jeśli None, pokazuje wszystkich zawodników.
    :param show_zeros: Jeśli True, pokazuje również ligi, w których zawodnicy nie grali (minuty = 0).
    :return: DataFrame z kolumnami: 'player_id', 'player_name', 'league', 'minutes'.
    """
    import pandas as pd
    data = []

    if type(league_name) == str:
        league_name = [league_name]
    
    for player in team.players:

        # player_name = f"{player.firstname} {player.lastname}"
        player_name = f"{player.lastname} {player.firstname}"
        time_played_in_league = 0
        for app in player.appearances:
            if league_name is not None and app.league.name not in league_name:
                continue
            time_played_in_league += app.duration

        player_row = {
                "player_name": player_name,
                "time_played_in_league": time_played_in_league
            }
        data.append(player_row)

    df = pd.DataFrame(data)
    df.sort_values(by="player_name", ascending=True, inplace=True)
    df = df.query("time_played_in_league > 0" if not show_zeros else "time_played_in_league >= 0")
    return df

if __name__ == "__main__":
    # 1. Inicjalizacja klubu i załadowanie statystyk z plików JSON
    club = Club("Polonia Warszawa", "polonia")
    club.prep_stats()
    
    if club.teams:
        team = club.teams[4]
        print(f"Generowanie danych dla zespołu: {team.category_age}...")
        
        df_stats = get_player_list_df(team, league_name="CLJ U-17", show_zeros=False)

        csv_path = f"player_list_{team.category_age}.csv"
        df_stats.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")
        print(f"[OK] Zapisano do CSV: {csv_path}")
        
    else:
        print("Nie znaleziono żadnych zespołów w klubie.")
from mincal import Club

if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")
    print(club)
    # club.download_matches()
    club.download_players()
    # club.download_match_data()

    # club.prep_stats()
    # league = club.leagues[0]
    # league.show_players()
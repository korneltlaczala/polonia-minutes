from mincal import Club

if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")

    import sys
    print(sys.argv)
    if len(sys.argv) > 1:
        only_new_leagues = sys.argv[1] == "only_new_leagues"
    else:
        only_new_leagues = False
    print(only_new_leagues)

    club.download_matches(only_new_leagues=only_new_leagues)

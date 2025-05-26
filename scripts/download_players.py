from mincal import Club

if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")

    import sys
    if len(sys.argv) > 1:
        force = sys.argv[1] == "force"
    else:
        force = False

    club.download_players(force=force)

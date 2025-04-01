class Team:
    def __init__(self, name, folder, url):
        self.name = name
        self.folder = folder
        self.url = url

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Team({self.name}, {self.folder})"
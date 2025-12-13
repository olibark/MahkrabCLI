from mahkrab import constants as c

def terry():
    with open(c.TERRY_FILE, 'r', encoding="utf-8") as file:
        print(file.read())
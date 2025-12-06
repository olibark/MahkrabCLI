import constants as c

def terry():
    print("1: Thou shall not litter")
    print("2: No gore unless it looks fake.")
    print("3: No pedophilia or child porn.")
    print("4: Dont eat rare meat with blood.")
    print("5: No wife beating.")
    print("6: Do not swing from radio towers with one hand.")
    print("7: Do not disturb")
    with open(c.TERRY_FILE, 'r') as file:
        print(file.read())
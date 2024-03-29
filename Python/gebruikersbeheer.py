#!/usr/bin/python3

import sys
import csv
import os
import pwd
import grp
import subprocess
import argparse


# Functie voor het aanmaken van nieuwe gebruikers
def create_user(username, full_name, email, klasgroep, password, ssh_public_key):
    try:
        # Kijk na of de opgegeven username niet al bestaat op het systeem
        pwd.getpwnam(username)
        print(f"Gebruiker '{username}' bestaat al. Overslaan.")
        return
    # Voorkomt dat user niet opnieuw wordt toegevoegd
    except KeyError:
        pass

    # Maak een home directory voor de nieuwe user, hierbij wordt alles voor '@' in het email adres gebruikt als naam voor de directory.
    home_dir = '/home/' + email.split('@')[0]
    os.makedirs(home_dir, exist_ok=True)
    # Maak user aan
    cmd = ['useradd', '-d', home_dir]
    # Kijk na of er een wachtwoord is opgegeven en voeg dit toe aan het commando
    if password:
        cmd += ['-p', password]
    cmd += [username]
    # Voer het commando uit om de user toe te voegen
    subprocess.run(cmd)

    groups = ['students', klasgroep]
    # Doorloop de lijst met groepen en kijk of de groep bestaat
    for group in groups:
        try:
            grp.getgrnam(group)
        except KeyError:
            # Maak groep aan als deze niet bestaat
            subprocess.run(['groupadd', group])
        # Voeg gebruiker toe aan students en klasgroep
        subprocess.run(['usermod', '-aG', group, username])

    if ssh_public_key:
        # Maak pad naar .ssh dir in de home directory van de gebruiker
        ssh_dir = os.path.join(home_dir, '.ssh')
        # Maak directory .ssh aan als deze nog niet bestaat
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
        # Maak authorized_keys bestand in ssh_dir
        authorized_keys_file = os.path.join(ssh_dir, 'authorized_keys')
        # Schrijf de public ssh key die met de csv is meegegeven naar authorized_keys
        with open(authorized_keys_file, 'a') as f:
            f.write(ssh_public_key + '\n')

    print(f"Gebruiker '{username}' is succesvol aangemaakt.")


# Functie voor het gebruiken van het csv-bestand
def process_csv(csv_file):
    # Open het bestand in readmode
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        # Sla header van csv over en lees alleen de data uit
        header = next(reader)
        for row in reader:
            student_id = row[0]
            username = 's' + str(student_id)
            full_name = row[1]
            email = row[2]
            klasgroep = row[3]
            password = row[4]
            ssh_public_key = row[5]
            # Voer create_user functie uit met parameters
            create_user(username, full_name, email, klasgroep, password, ssh_public_key)


# Functie voor het aanmaken van een nieuwe groep en het toevoegen van gebruikers
def create_group(group_name, users):
    try:
        # Kijk na of de groep al bestaat
        grp.getgrnam(group_name)
        print(f"Groep '{group_name}' bestaat al.")
    except KeyError:
        # Maak groep aan als deze niet bestaat
        subprocess.run(['groupadd', group_name])
        print(f"Groep '{group_name}' is succesvol aangemaakt.")

    # Voeg gebruikers toe aan de groep
    for user in users:
        try:
            pwd.getpwnam(user)
            subprocess.run(['usermod', '-aG', group_name, user])
            print(f"Gebruiker '{user}' is toegevoegd aan groep '{group_name}'.")
        except KeyError:
            print(f"Gebruiker '{user}' bestaat niet. Toevoegen aan groep '{group_name}' mislukt.")


# Functie om users te verwijderen
def delete_users():
    users_to_delete = []
    # Alle users op het systeem ophalen
    for user in pwd.getpwall():
        # Voor elke user op het systeem wordt gekeken naar alle groepen om te zien waar de huidige user lid van is
        groups = [grp.gr_name for grp in grp.getgrall() if user.pw_name in grp.gr_mem]
        # Controleren of de gebruikersnaam begint met 's' en dat ze lid zijn van de groep 'students'
        if user.pw_name.startswith('s') and 'students' in groups:
            users_to_delete.append(user.pw_name)

    if len(users_to_delete) == 0:
        print("Geen users gevonden")
        return

    print("Gevonden users:")
    for user in users_to_delete:
        print(user)

    if args.interactive:
        choice = input("Wil je deze users verwijderen? (J) ja, kies gebruikers /(N) nee / (A) ja, alle gebruikers: ")
        if choice.upper() == 'A':
            for user in users_to_delete:
                subprocess.run(['userdel', user])
                print(f"User '{user}' verwijderd.")
        elif choice.upper() == 'J':
            for user in users_to_delete:
                confirm = input(f"Wil je user '{user}' verwijderen? (J) ja / (N) nee: ")
                if confirm.upper() == 'J':
                    subprocess.run(['userdel', user])
                    print(f"User '{user}' verwijderd.")
        else:
            print("Abort.")
    else:
        for user in users_to_delete:
            subprocess.run(['userdel', user])
            print(f"User '{user}' verwijderd.")


# Maak een argumentparser
parser = argparse.ArgumentParser(description='Script voor het beheren van gebruikers en groepen.')

# Voeg argumenten toe
parser.add_argument('-c', '--create', metavar='FILE', help='Maak gebruikers aan op basis van een CSV-bestand.')
parser.add_argument('-g', '--group', nargs='+', metavar=('GROUP_NAME', 'USERS'), help='Maak een nieuwe groep aan en voeg gebruikers toe.')
parser.add_argument('-f', '--file', metavar='FILE', help='Bestand met lijst van gebruikers (een per regel).')
parser.add_argument('-d', '--delete', action='store_true', help='Delete users die behoren tot groep studenten en wiens usernames beginnen met "s".')
parser.add_argument('-i', '--interactive', action='store_true', help='Vraag bevestiging voor users verwijderd worden')

# TE IMPLEMENTEREN
# parser.add_argument('-v', '--verbose', action='store_true', help='Meer output tonen')
# parser.add_argument('-q', '--quiet', action='store_true', help='Minder output tonen')
# parser.add_argument('-n', '--dry-run', action='store_true', help='Beschrijven wat er gedaan zou worden, maar het niet uitvoeren')



# Parse de command line argumenten
args = parser.parse_args()

# Kijk na welke actie moet worden uitgevoerd
if args.create:
    csv_file = args.create
    # Voer process_csv functie uit
    process_csv(csv_file)
elif args.group:
    group_name = args.group[0]
    users = args.group[1:]
    if args.file:
        # Kijk na of het bestand bestaat
        if os.path.isfile(args.file):
            # Open het bestand in readmode
            with open(args.file, 'r') as f:
                # Gebruik splitlines om elke gebruiker op een aparte regel te nemen en in de lijst users te steken
                users += f.read().splitlines()
        else:
            print(f"Bestand '{args.file}' bestaat niet.")
            # Maak de groep aan met elke gebruiker in de groep users
            create_group(group_name, users)
    else:
        users = sys.argv[3:]
        # Maak de groep aan met elke gebruiker in de groep users
        create_group(group_name, users)
elif args.delete:
    delete_users()
else:
    parser.print_help()
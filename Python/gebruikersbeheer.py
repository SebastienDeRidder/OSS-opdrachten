#!/usr/bin/env python3

import sys
import csv
import os
import pwd
import grp


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

    # Maak een home directory voor de nieuwe user, hierbij word alles voor '@' in het email adres gebruikt als naam voor de directory.
    home_dir = '/home/' + email.split('@')[0]
    os.makedirs(home_dir, exist_ok=True)
    # Maak user aan
    cmd = f"useradd -d {home_dir}"
    # Kijk na of er een wachtwoord is opgegeven en geef dit door aan het commando
    if password:
        cmd += f" -p '{password}'"
    cmd += f" '{username}'"
    # Voer het commando uit om de user toe te voegen
    os.system(cmd)

    groups = ['students', klasgroep]
    # Doorloop lijst groups en kijk of de groep bestaat
    for group in groups:
        try:
            grp.getgrnam(group)
        except KeyError:
            # Maak groep aan als hij niet bestaat
            os.system(f"groupadd {group}")
            # Voeg user toe aan students en klasgroep
        os.system(f"usermod -aG {group} {username}")

    if ssh_public_key:
        # Maak pad naar .ssh dir in de home directory van de user
        ssh_dir = os.path.join(home_dir, '.ssh')
        # Maak directory .ssh als hij nog niet bestaat
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
        # Maak authorized_keys bestand in ssh_dir
        authorized_keys_file = os.path.join(ssh_dir, 'authorized_keys')
        # Schrijf de public ssh key die met de csv wordt meegegeven naar authorized_keys
        with open(authorized_keys_file, 'a') as f:
            f.write(ssh_public_key + '\n')

    print(f"Gebruiker '{username}' is succesvol aangemaakt.")


# Functie voor het gebruiken van het csv-bestand
def process_csv(csv_file):
    # Open bestand in readmode
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        # Sla header van csv over en lees enkel de data uit
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
        # Maak groep aan als hij niet bestaat
        os.system(f"groupadd {group_name}")
        print(f"Groep '{group_name}' is succesvol aangemaakt.")

    # Voeg gebruikers toe aan de groep
    for user in users:
        try:
            pwd.getpwnam(user)
            os.system(f"usermod -aG {group_name} {user}")
            print(f"Gebruiker '{user}' is toegevoegd aan groep '{group_name}'.")
        except KeyError:
            print(f"Gebruiker '{user}' bestaat niet. Toevoegen aan groep '{group_name}' mislukt.")


# Kijk na of er 3 parameters zijn meegegeven
if len(sys.argv) >= 3:
    # Kijk na of de 2de parameter '-c' of '--create' is
    if sys.argv[1] == '-c' or sys.argv[1] == '--create':
        csv_file = sys.argv[2]
        # Voer process_csv functie uit
        process_csv(csv_file)
    else:
        print("Gebruik: gebruikersbeheer.py -c <CSV-bestand>")
# Kijk na of de 2de parameter '-g' of '--group' is
elif sys.argv[1] == '-g' or sys.argv[1] == '--group':
    # Kijk na of de 4de parameter '-f' is
    if sys.argv[3] == '-f':
        group_name = sys.argv[2]
        file_path = sys.argv[4]
        # Kijk na of het bestand bestaat
        if os.path.isfile(file_path):
            # Open het bestand in readmode
            with open(file_path, 'r') as f:
                # Gebruik splitlines om elke user op een aparte lijn te nemen en in de lijst users te steken
                users = f.read().splitlines()
            # Maak de groep aan met elke user in de groep users
            create_group(group_name, users)
        else:
            print(f"Bestand '{file_path}' bestaat niet.")
    else:
        group_name = sys.argv[2]
        users = sys.argv[3:]
        # Maak de groep aan met elke user in de groep users
        create_group(group_name, users)
else:
    print("Geef meer opties: minstens -c of -g")
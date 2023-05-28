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

# Kijk na of er genoeg parameters zijn meegegeven met het commando om het script uit te voeren. Als de 2de parameter '-c' of '--create' is wordt de process_csv functie uitgevoerd.
if len(sys.argv) == 3 and (sys.argv[1] == '-c' or sys.argv[1] == '--create'):
    csv_file = sys.argv[2]
    process_csv(csv_file)
else:
    print("Gebruik: gebruikersbeheer.py -c <CSV-bestand>")

Import-Module AzureAD
Import-Module ActiveDirectory

$ouParentName = "OS Scripting 23"  # Naam van de bovenliggende OU
$ouChildName = "s122861"  # Naam van de sub-OU
$ouGroupsName = "groups"
$ouUsersName = "users"
$maxGroupNameLength = 64

# Controleer of de bovenliggende OU bestaat
$ouParentExists = Get-ADOrganizationalUnit -Filter "Name -eq '$ouParentName'"

# Maak de OU's aan als deze niet bestaan
if (-not $ouParentExists) {
    New-ADOrganizationalUnit -Name $ouParentName -Path "DC=sebas-tien,DC=com" -ProtectedFromAccidentalDeletion $false
    Write-Host "OU '$ouParentName' succesvol aangemaakt."

    # Maak de sub-OU aan
    New-ADOrganizationalUnit -Name 's122861' -Path "OU=OS Scripting 23,DC=sebas-tien,DC=com" -ProtectedFromAccidentalDeletion $false
    Write-Host "OU '$ouChildName' succesvol aangemaakt binnen OU '$ouParentName'."

    # Maak de sub-OU's "groups" en "users" binnen de sub-OU aan
    New-ADOrganizationalUnit -Name $ouGroupsName -Path "OU=s122861,OU=OS Scripting 23,DC=sebas-tien,DC=com" -ProtectedFromAccidentalDeletion $false
    Write-Host "OU '$ouGroupsName' succesvol aangemaakt binnen OU '$ouChildName'."
    New-ADOrganizationalUnit -Name $ouUsersName -Path "OU=s122861,OU=OS Scripting 23,DC=sebas-tien,DC=com" -ProtectedFromAccidentalDeletion $false
    Write-Host "OU '$ouUsersName' succesvol aangemaakt binnen OU '$ouChildName'."
} else {
    Write-Host "OU '$ouParentName' bestaat al. Overslaan."
}

# Verbind met AzureAD
Connect-AzureAD

$username = "s122861@ap.be"
# Doorzoek AzureAD naar groepen waar $username lid van is
$user = Get-AzureADUser -Filter "userPrincipalName eq '$username'"
# Groepen waar $username lid van is ophalen
$groups = Get-AzureADUserMembership -ObjectId $user.ObjectId | Get-AzureADGroup

# Loop door alle groepen
$groups | ForEach-Object {
    # De DisplayName van elke groep bijhouden
    $groupDisplayName = $_.DisplayName
    $sanitizedDisplayName = $groupDisplayName -replace '^[\s]+', '' # verwijder spaties op het begin 
    $sanitizedDisplayName = $sanitizedDisplayName -replace '&', 'en'  # vervang & met en
    $sanitizedDisplayName = $sanitizedDisplayName -replace '[":]', ''   # verwijder " en :
    $sanitizedDisplayName = $sanitizedDisplayName.Substring(0, [Math]::Min($sanitizedDisplayName.Length, $maxGroupNameLength))
    $AzureGroups = "OU=$ouGroupsName,OU=$ouChildName,OU=$ouParentName,DC=sebas-tien,DC=com"
    $adGroup = Get-AzureADGroup -ObjectId $_.ObjectId

    # Per DisplayName nakijken of er al een groep bestaat met die naam
    if (-not (Get-ADGroup -Filter "Name -eq '$groupDisplayName'")) {
        # Nieuwe groep maken 
        New-ADGroup -Name $sanitizedDisplayName -Path $AzureGroups -GroupScope Global
        Write-Host "Groep '$sanitizedDisplayName' werd succesvol aangemaakt."
    } else {
        Write-Host "Groep '$groupDisplayName' bestaat al. Skipping."
    }

    # Leden van de groep ophalen
    $groupMembers = Get-AzureADGroupMember -ObjectId $adGroup.ObjectId

    # Loop doorheen alle users in de group
    $groupMembers | ForEach-Object {
        $memberUser = Get-AzureADUser -ObjectId $_.ObjectId

        # Check of naam "Admin Octopus is omdat deze naam errors veroorzaakt"
        if ($memberUser -notlike "Admin Octopus*"){
            # Maak de user aan in de users OU op de lokale AD
            $AzureUsers = "OU=$ouUsersName,OU=$ouChildName,OU=$ouParentName,DC=sebas-tien,DC=com"
            # Haal naam op van de user
            $uniqueName = $memberUser.UserPrincipalName
            
            # Check of de naam nog niet bestaat
            if (-not (Get-ADUser -Filter "Name -eq '$uniqueName'")) {
                # Maak gebruiker aan
                $password = ConvertTo-SecureString -String "Sup3rVeiligWachtwoord" -AsPlainText -Force
                $newUser = New-ADUser -Name $uniqueName -UserPrincipalName $memberUser.UserPrincipalName -GivenName $memberUser.GivenName -Surname $memberUser.Surname -Enabled $true -Path $AzureUsers -AccountPassword $password -PassThru

                # Check of waarde van $newUser niet leeg is
                # if ($newUser) {
                #     # Voeg de gebruiker toe aan de groep
                #     Add-ADGroupMember -Identity $sanitizedDisplayName -Members $newUser
                #     Write-Host "User '$($memberUser.DisplayName)' is gemaakt in de 'users' OU en toegevoegd aan de groep '$($sanitizedDisplayName)'."
                # } else {
                #     Write-Host "Fout bij het maken van gebruiker '$($memberUser.DisplayName)' in de 'users' OU."
                # }
            }
            else {
                Write-Host "User '$($memberUser.DisplayName)' bestaat al in de 'users' OU. Skipping."
            }
        }
    }
}

Import-Module AzureAD

$ouParentName = "OS Scripting 23"  # Naam van de bovenliggende OU
$ouChildName = "s122861"  # Naam van de sub-OU
$ouGroupsName = "groups"
$ouUsersName = "users"

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
$user = Get-AzureADUser -Filter "userPrincipalName eq '$username'"
# Groepen waar $username lid van is ophalen
$groups = Get-AzureADUserMembership -ObjectId $user.ObjectId | Get-AzureADGroup

$groups | ForEach-Object {
    # De DisplayName van elke groep bijhouden
    $groupDisplayName = $($_.DisplayName)
    $AzureGroups = "OU=$ouGroupsName,OU=$ouChildName,OU=$ouParentName,DC=sebas-tien,DC=com"
    # Per DisplayName nakijken of er al een groep bestaat met die naam
    if (-not (Get-ADGroup -Filter "Name -eq '$groupDisplayName'")) {
        # Nieuwe groep maken 
        New-ADGroup -Name $groupDisplayName -Path $AzureGroups -GroupScope Global
        Write-Host "Groep '$groupDisplayName' werd succesvol aangemaakt."
    } else {
        Write-Host "Groep '$groupDisplayName' bestaat al. Skipping."
    }

}
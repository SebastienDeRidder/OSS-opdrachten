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
# Configuratie
$adServer = "ADServerName"  # Naam van de Active Directory-server
$ouName = "OS Scripting 23"  # Naam van de OU die moet worden aangemaakt

# Controleer of de OU al bestaat
$ouExists = Get-ADOrganizationalUnit -Filter "Name -eq '$ouName'" -ErrorAction SilentlyContinue

# Maak de OU aan als deze niet bestaat
if (-not $ouExists) {
    New-ADOrganizationalUnit -Name $ouName

    Write-Host "OU '$ouName' succesvol aangemaakt."
} else {
    Write-Host "OU '$ouName' bestaat al. Overslaan."
}

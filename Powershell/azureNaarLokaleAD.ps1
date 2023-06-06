
$adServer = "192.168.0.111"
$ouName = "OS Scripting 23"

# Controleer of de OU al bestaat
$ouExists = Invoke-Command -ComputerName $adServer -ScriptBlock {
    param($ouName)
    Get-ADOrganizationalUnit -Filter "Name -eq '$ouName'"
} -ArgumentList $ouName

# Maak de OU aan als deze niet bestaat
if (-not $ouExists) {
    Invoke-Command -ComputerName $adServer -ScriptBlock {
        param($ouName)
        New-ADOrganizationalUnit -Name $ouName
    } -ArgumentList $ouName

    Write-Host "OU '$ouName' succesvol aangemaakt."
} else {
    Write-Host "OU '$ouName' bestaat al. Overslaan."
}

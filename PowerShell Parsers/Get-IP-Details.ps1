Function My-Geo {
param (
                [Parameter(Mandatory=$True,
                           HelpMessage='Please enter IP Address (e.g. 127.0.0.1)')]
                           [string]$ip
        )

$currentEAP = $ErrorActionPreference
$ErrorActionPreference = "silentlycontinue"

$domainresult = [System.Net.Dns]::gethostentry($ip)

If ($domainresult)
{
    
    if ($domain.ToLower() = "$env:computername.$env:userdnsdomain".ToLower())
    {
        $domain = "$ip - No HostNameFound"
    }
    Else
    {
        $domain = [string]$domainresult.HostName
    }
}
Else
{
    $domain = "$ip - No HostNameFound"
}


# Geo Information

$html = Invoke-WebRequest -Uri "http://freegeoip.net/xml/$ip" -UseBasicParsing 
$geo = [xml]$html.Content
$results = $geo.response



# ASN Information
$html = Invoke-WebRequest -Uri "https://www.ultratools.com/tools/asnInfoResult?domainName=$ip" #-UseBasicParsing 
$asninfo = ($html.ParsedHtml.getElementsByTagName(‘div’) | Where{ $_.className -eq ‘tool-results-container’ } ).innerText
$ErrorActionPreference = $currentEAP

$GeoObject = New-Object PSObject
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Domain Name" -value $domain
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "IP Address" -value $ip
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Country" -value $results.CountryName
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Country Code" -value $results.CountryCode
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Region Code" -value $results.RegionCode
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Region Name" -value $results.RegionName
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "City" -value $results.City
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Zip Code" -value $results.ZipCode
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Time Zone" -value $results.TimeZone
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Latitude" -value $results.Latitude
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Longitude" -value $results.Longitude
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "Metro Code" -value $results.MetroCode
Add-Member -inputObject $GeoObject -memberType NoteProperty -name "ASN" -value $asninfo
$GeoObject
} #end function My-Geo


$listofIPs = Get-Content IP_list.txt

$ResultList = @()

Write-host "Staring to process the IP Addresses found in IP_List.txt"
Write-host "This process takes 5-10 seconds per IP address in IP_List.txt"

# Lets resolve each of these addresses
foreach ($ip in $listofIPs)
{
    Write-Host "Working on IP Address: " $ip
    $ResultList+=  My-Geo($ip)
    Start-Sleep -s 1
     
}

Write-Host "Processing Complete"
$ResultList  | Export-Csv -Path report.csv -Encoding UTF8 -UseCulture -NoTypeInformation

Write-Host "Output written to: report.csv"
#Invoke-Item -Path report.csv

# US004: Bekijk en Download Beleidsdocumenten

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** gescande beleidsdocumenten te kunnen bekijken en downloaden
**Zodat** ik de volledige inhoud kan beoordelen en documenten kan opslaan voor offline analyse

## Beschrijving

Gebruikers moeten beleidsdocumenten direct in de applicatie kunnen bekijken en downloaden voor offline gebruik. Het systeem moet verschillende documentformaten (PDF, HTML, DOCX) ondersteunen en relevante metadata en context over elk document bieden.

## Acceptatiecriteria

### Scenario 1: Documentdetails bekijken

**Gegeven** ik een beleidsdocument heb gevonden in de zoekresultaten
**Wanneer** ik op de documenttitel klik
**Dan** moet ik een gedetailleerde weergave zien met:
- Volledige documenttitel
- Bron (DSO, Gemeenteblad, aangepaste bron)
- Publicatiedatum
- Gemeente (indien van toepassing)
- Documenttype
- Originele URL
- Samenvatting of beschrijving (indien beschikbaar)
**En** moet ik een voorbeeldweergave of "Document bekijken"-knop zien

### Scenario 2: PDF-documenten bekijken

**Gegeven** ik een PDF-beleidsdocument bekijk
**Wanneer** ik op "Voorbeeld" of "Document bekijken" klik
**Dan** moet de PDF worden geopend in een ingebouwde viewer binnen de applicatie
**En** moet ik door de pagina's kunnen navigeren
**En** moet ik kunnen in- en uitzoomen
**En** moet de originele opmaak behouden blijven

### Scenario 3: HTML-documenten bekijken

**Gegeven** ik een HTML-beleidsdocument bekijk
**Wanneer** ik op "Document bekijken" klik
**Dan** moet de HTML-inhoud worden weergegeven in een schoon, leesbaar formaat
**En** moeten links binnen het document functioneel zijn
**En** moeten afbeeldingen correct worden geladen
**En** moet de styling behouden maar gesaniteerd worden voor beveiliging

### Scenario 4: Documenten downloaden

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik op de knop "Downloaden" klik
**Dan** moet het document naar mijn lokale machine worden gedownload
**En** moet de bestandsnaam de documenttitel en bron bevatten
**En** moet het originele formaat behouden blijven (PDF, HTML, DOCX)

### Scenario 5: Meerdere documenten downloaden

**Gegeven** ik meerdere documenten heb geselecteerd uit de zoekresultaten
**Wanneer** ik op "Geselecteerde downloaden" klik
**Dan** moeten alle geselecteerde documenten worden gedownload
**En** moeten ze worden verpakt in een ZIP-bestand bij meer dan 5 documenten
**En** moet de ZIP een manifestbestand met metadata bevatten

### Scenario 6: Documentlink kopiëren

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik op "Link naar document kopiëren" klik
**Dan** moet de originele bron-URL naar mijn klembord worden gekopieerd
**En** moet ik een bevestigingsbericht zien
**En** moet de link het originele document openen wanneer deze in een browser wordt geplakt

### Scenario 7: Niet-beschikbare documenten afhandelen

**Gegeven** ik probeer een document te bekijken waarvan de bron niet langer beschikbaar is
**Wanneer** ik op "Document bekijken" klik
**Dan** moet ik een foutmelding zien die aangeeft dat het document niet beschikbaar is
**En** moet ik nog steeds de gecachte metadata zien
**En** moet ik de laatst bekende toegangsdatum zien

### Scenario 8: Documentweergaven bijhouden

**Gegeven** ik ben ingelogd als gebruiker
**Wanneer** ik een document bekijk of download
**Dan** moet het systeem deze actie registreren
**En** moet ik mijn recent bekeken documenten kunnen zien
**En** moet ik toegang hebben tot mijn downloadgeschiedenis

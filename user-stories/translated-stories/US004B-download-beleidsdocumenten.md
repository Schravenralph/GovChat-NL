# US004B: Download Beleidsdocumenten

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** beleidsdocumenten te kunnen downloaden voor offline gebruik
**Zodat** ik documenten kan analyseren zonder internetverbinding en ze kan opslaan voor toekomstig gebruik

## Beschrijving

Gebruikers moeten individuele of meerdere beleidsdocumenten naar hun lokale machine kunnen downloaden. Het systeem moet originele formaten behouden en handige batch-downloadmogelijkheden bieden voor meerdere documenten.

## Acceptatiecriteria

### Scenario 1: Enkel document downloaden

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik op de knop "Downloaden" klik
**Dan** moet het document naar mijn lokale machine worden gedownload
**En** moet de bestandsnaam de documenttitel en bron bevatten
**En** moet het originele formaat behouden blijven (PDF, HTML, DOCX)

### Scenario 2: Meerdere documenten downloaden

**Gegeven** ik meerdere documenten heb geselecteerd uit de zoekresultaten
**Wanneer** ik op "Geselecteerde downloaden" klik
**Dan** moeten alle geselecteerde documenten worden gedownload
**En** moeten ze worden verpakt in een ZIP-bestand bij meer dan 5 documenten
**En** moet de ZIP een manifestbestand met metadata bevatten

### Scenario 3: Documenten selecteren voor batch-download

**Gegeven** ik zoekresultaten bekijk
**Wanneer** ik selectievakjes gebruik om meerdere documenten te selecteren
**Dan** moet ik een teller zien die toont hoeveel documenten zijn geselecteerd
**En** moet ik een knop "Geselecteerde downloaden" zien
**En** moet ik alle documenten tegelijk kunnen selecteren/deselecteren

### Scenario 4: Grote documentverzamelingen downloaden

**Gegeven** ik meer dan 20 documenten download
**Wanneer** de download wordt geïnitieerd
**Dan** moet ik een voortgangsindicator zien
**En** moet ik de download indien nodig kunnen annuleren
**En** moeten voltooide documenten beschikbaar blijven, zelfs als ik halverwege annuleer

### Scenario 5: Downloadfouten afhandelen

**Gegeven** een document niet kan worden gedownload vanwege netwerkproblemen
**Wanneer** de downloadfout optreedt
**Dan** moet ik een duidelijke foutmelding zien
**En** moet ik de optie krijgen om de download opnieuw te proberen
**En** moeten succesvol gedownloade documenten nog steeds beschikbaar zijn

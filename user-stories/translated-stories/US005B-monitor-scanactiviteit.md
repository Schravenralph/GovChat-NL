# US005B: Monitor Actieve Scans en Geschiedenis

## User Story

**Als** systeembeheerder
**Heb ik nodig** actieve scans te kunnen monitoren en scangeschiedenis te kunnen bekijken
**Zodat** ik de voortgang van scans kan volgen en problemen kan oplossen wanneer ze optreden

## Beschrijving

Beheerders moeten de real-time status van actieve scans kunnen bekijken en toegang hebben tot historische scangegevens. Dit maakt proactieve monitoring mogelijk en helpt bij het identificeren van patronen of terugkerende problemen met specifieke bronnen.

## Acceptatiecriteria

### Scenario 1: Actieve scantaken bekijken

**Gegeven** ik op het scanbeheer-dashboard ben
**Wanneer** ik de lijst met actieve scans bekijk
**Dan** moet ik alle momenteel lopende scans zien met:
- Bronnaam
- Starttijd
- Voortgangspercentage (indien beschikbaar)
- Aantal verwerkte documenten
- Geschatte resterende tijd
**En** moet ik een lopende scan kunnen annuleren indien nodig

### Scenario 2: Scangeschiedenis bekijken

**Gegeven** ik eerdere scanactiviteiten wil bekijken
**Wanneer** ik de scangeschiedenispagina open
**Dan** moet ik een lijst met voltooide scans zien met:
- Bronnaam
- Start- en eindtijd
- Status (geslaagd, gedeeltelijk geslaagd, mislukt)
- Aantal gevonden documenten
- Aantal nieuwe documenten toegevoegd
- Aantal bijgewerkte documenten
- Eventuele fouten of waarschuwingen
**En** moet ik kunnen filteren op bron, datumbereik en status

### Scenario 3: Gedetailleerde scan-logs bekijken

**Gegeven** ik een specifieke scan wil onderzoeken
**Wanneer** ik op een scaninvoer in de geschiedenis klik
**Dan** moet ik gedetailleerde logs voor die scan zien
**En** moeten logs tijdstempels bevatten voor elke belangrijke actie
**En** moeten eventuele fouten worden gemarkeerd met details
**En** moet ik de logs kunnen exporteren

### Scenario 4: Scanprestatiestatistieken monitoren

**Gegeven** ik de scanefficiëntie wil begrijpen
**Wanneer** ik scanprestatiestatistieken bekijk
**Dan** moet ik zien:
- Gemiddelde scanduur per bron
- Documenten gescand per uur
- Succespercentage
- Meest voorkomende fouten
**En** moet ik statistieken voor een specifieke periode kunnen bekijken
**En** moet ik prestaties tussen verschillende bronnen kunnen vergelijken

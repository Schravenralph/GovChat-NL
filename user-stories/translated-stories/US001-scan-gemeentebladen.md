# US001: Scan Gemeentebladen voor Beleidsdocumenten

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** dat Gemeentebladen worden gescand op beleidsdocumenten
**Zodat** ik gemeentelijk beleid kan ontdekken en raadplegen dat niet beschikbaar is in het DSO-systeem

## Beschrijving

Het systeem moet in staat zijn om automatisch beleidsdocumenten uit Gemeentebladen van verschillende gemeenten te scannen en te indexeren. Hierdoor kunnen gebruikers beleidsdocumenten vinden die mogelijk niet gerelateerd zijn aan omgevings- of ruimtelijke planning, maar toch relevant zijn voor beleidsonderzoek.

## Acceptatiecriteria

### Scenario 1: Succesvol scannen van een Gemeenteblad-bron

**Gegeven** de beleidsscanner is geconfigureerd met een geldige Gemeenteblad-URL
**Wanneer** ik een scan van de Gemeenteblad-bron initieer
**Dan** moet het systeem alle beschikbare beleidsdocumenten ophalen
**En** moeten de documenten worden geïndexeerd met metadata (titel, publicatiedatum, gemeente, documenttype)
**En** moet ik een bevestigingsbericht zien met het aantal gevonden documenten

### Scenario 2: Meerdere gemeenten verwerken

**Gegeven** ik heb meerdere Gemeenteblad-bronnen van verschillende gemeenten geconfigureerd
**Wanneer** ik een batch-scan uitvoer over alle geconfigureerde bronnen
**Dan** moeten de documenten van elke gemeente afzonderlijk worden gescand
**En** moeten documenten worden gelabeld met de bijbehorende gemeentenaam
**En** moet ik een samenvattingsrapport ontvangen met resultaten per gemeente

### Scenario 3: Scanfouten netjes afhandelen

**Gegeven** een of meer Gemeenteblad-bronnen zijn tijdelijk niet beschikbaar
**Wanneer** het scanproces een fout tegenkomt
**Dan** moet het systeem de fout loggen met details
**En** doorgaan met scannen van andere beschikbare bronnen
**En** mij op de hoogte stellen van welke bronnen zijn mislukt en welke zijn geslaagd

### Scenario 4: Dubbele documenten voorkomen

**Gegeven** een document is eerder al gescand en geïndexeerd
**Wanneer** een herscan wordt uitgevoerd op dezelfde Gemeenteblad-bron
**Dan** moet het systeem dubbele documenten detecteren
**En** alleen het document bijwerken als wijzigingen worden gedetecteerd
**En** indexering overslaan als het document ongewijzigd is

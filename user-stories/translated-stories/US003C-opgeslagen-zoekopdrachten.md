# US003C: Opslaan en Beheren van Zoekopdrachten

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** mijn zoekopdrachten en filters te kunnen opslaan
**Zodat** ik frequente zoekopdrachten snel opnieuw kan uitvoeren en meldingen kan ontvangen over nieuwe overeenkomende documenten

## Beschrijving

Gebruikers moeten complexe zoekopdrachten met hun toegepaste filters kunnen opslaan voor later gebruik. Dit maakt het mogelijk om terugkerende zoekopdrachten snel uit te voeren en stelt gebruikers in staat om te worden geïnformeerd wanneer nieuwe documenten aan hun opgeslagen criteria voldoen.

## Acceptatiecriteria

### Scenario 1: Zoekopdracht opslaan

**Gegeven** ik een zoekopdracht heb uitgevoerd met meerdere filters toegepast
**Wanneer** ik op "Zoekopdracht opslaan" klik
**Dan** moet ik worden gevraagd om een naam voor de opgeslagen zoekopdracht in te voeren
**En** moet de zoekopdracht worden opgeslagen met alle huidige filters en zoekwoorden
**En** moet ik een bevestigingsbericht zien

### Scenario 2: Opgeslagen zoekopdrachten raadplegen

**Gegeven** ik een of meer zoekopdrachten heb opgeslagen
**Wanneer** ik naar het menu "Opgeslagen zoekopdrachten" navigeer
**Dan** moet ik een lijst zien van al mijn opgeslagen zoekopdrachten
**En** moet elke invoer de zoeknaam en aanmaakdatum tonen
**En** moet ik op een opgeslagen zoekopdracht kunnen klikken om deze uit te voeren

### Scenario 3: Opgeslagen zoekopdracht uitvoeren

**Gegeven** ik mijn opgeslagen zoekopdrachten bekijk
**Wanneer** ik op een opgeslagen zoeknaam klik
**Dan** moet de zoekopdracht worden uitgevoerd met de opgeslagen filters en zoekwoorden
**En** moeten de resultaten worden weergegeven alsof ik de criteria handmatig had ingevoerd
**En** moet ik de filters kunnen wijzigen voordat ik uitvoer

### Scenario 4: Meldingen inschakelen voor opgeslagen zoekopdracht

**Gegeven** ik een opgeslagen zoekopdracht heb
**Wanneer** ik meldingen voor die zoekopdracht inschakelen
**Dan** moet ik een melding ontvangen wanneer nieuwe documenten aan de criteria voldoen
**En** moet ik de meldingsfrequentie kunnen configureren (onmiddellijk, dagelijkse samenvatting, wekelijkse samenvatting)
**En** moeten meldingen het aantal nieuwe overeenkomende documenten bevatten

### Scenario 5: Opgeslagen zoekopdracht verwijderen

**Gegeven** ik een opgeslagen zoekopdracht heb die niet langer nodig is
**Wanneer** ik op "Verwijderen" klik bij de opgeslagen zoekopdracht
**Dan** moet ik worden gevraagd om de verwijdering te bevestigen
**En** moet na bevestiging de opgeslagen zoekopdracht worden verwijderd
**En** moeten alle bijbehorende meldingen worden uitgeschakeld

### Scenario 6: Opgeslagen zoekopdracht hernoemen

**Gegeven** ik de naam van een opgeslagen zoekopdracht wil bijwerken
**Wanneer** ik "Hernoemen" selecteer bij een opgeslagen zoekopdracht
**Dan** moet ik een nieuwe naam kunnen invoeren
**En** moet de zoekopdracht met de nieuwe naam worden opgeslagen
**En** moeten alle andere instellingen ongewijzigd blijven

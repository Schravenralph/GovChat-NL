# US007D: Maak Aangepaste Categorisatieregels

## User Story

**Als** systeembeheerder
**Heb ik nodig** aangepaste categorisatieregels te kunnen maken en beheren
**Zodat** documenten automatisch worden geclassificeerd volgens organisatiebehoeften

## Beschrijving

Beheerders moeten aangepaste regels kunnen definiëren die automatisch categorieën en tags toewijzen aan documenten op basis van specifieke criteria. Dit stelt organisaties in staat om het categorisatiesysteem aan te passen aan hun specifieke domein en vereisten.

## Acceptatiecriteria

### Scenario 1: Categorisatieregel maken

**Gegeven** ik een beheerder ben die het categorisatiesysteem configureert
**Wanneer** ik een aangepaste categorisatieregel maak
**Dan** moet ik kunnen definiëren:
- Regelnaam en beschrijving
- Zoekwoorden of patronen die de categorie activeren
- Prioriteitsniveau voor de regel
- Of de categorie automatisch moet worden toegepast of voorgesteld
- Welke categorie/tags moeten worden toegewezen bij activering
**En** moet de regel worden gevalideerd voordat deze wordt opgeslagen

### Scenario 2: Categorisatieregels testen

**Gegeven** ik een nieuwe categorisatieregel heb gemaakt
**Wanneer** ik de regel test
**Dan** moet het systeem me een voorbeeld tonen van documenten die zouden overeenkomen
**En** weergeven welke categorieën/tags zouden worden toegewezen
**En** me toestaan de regel te verfijnen op basis van resultaten
**En** de geschatte impact tonen (aantal beïnvloede documenten)

### Scenario 3: Regelprioriteit beheren

**Gegeven** meerdere regels op hetzelfde document kunnen worden toegepast
**Wanneer** ik regelprioriteiten configureer
**Dan** moeten regels met hogere prioriteit eerst worden geëvalueerd
**En** moet ik kunnen instellen of regels met lagere prioriteit extra tags kunnen toevoegen
**En** moet ik regels kunnen herordenen door te slepen en te plaatsen

### Scenario 4: Regels achteraf toepassen

**Gegeven** ik een nieuwe regel heb gemaakt voor bestaande documenten
**Wanneer** ik ervoor kies de regel achteraf toe te passen
**Dan** moet ik een voorbeeld zien van documenten die worden beïnvloed
**En** de bulktoepassing kunnen bevestigen of annuleren
**En** een samenvatting ontvangen van hoeveel documenten opnieuw zijn gecategoriseerd

### Scenario 5: Regelgebaseerde tag-blacklist

**Gegeven** bepaalde tags verkeerd worden toegepast door automatische systemen
**Wanneer** ik een blacklist-regel maak
**Dan** moet ik tags kunnen specificeren die nooit automatisch mogen worden toegepast
**En** voorwaarden kunnen specificeren voor wanneer de blacklist van toepassing is
**En** moeten bestaande onjuiste tags worden gemarkeerd voor beoordeling

### Scenario 6: Regeltoepassingsgeschiedenis bekijken

**Gegeven** ik wil begrijpen hoe regels presteren
**Wanneer** ik regelanalyses bekijk
**Dan** moet ik zien:
- Hoeveel documenten elke regel heeft gecategoriseerd
- Succespercentage (hoe vaak handmatige beoordeling de categorisatie bevestigt)
- Meest recent toegepaste regels
- Regels die vaak samen worden geactiveerd
**En** moet ik regelprestaties kunnen exporteren

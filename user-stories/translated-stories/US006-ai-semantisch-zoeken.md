# US006: AI-gedreven Semantisch Zoeken naar Beleid

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** AI-gedreven semantische zoekopdrachten uit te kunnen voeren over beleidsdocumenten
**Zodat** ik relevant beleid kan vinden op basis van betekenis en context, niet alleen zoekwoorden

## Beschrijving

Het systeem moet AI en natuurlijke taalverwerking gebruiken om de semantische betekenis van zoekopdrachten en beleidsdocumenten te begrijpen. Hierdoor kunnen gebruikers relevant beleid vinden, zelfs wanneer documenten geen exacte zoekwoord-matches bevatten, door de intentie en context van de zoekopdracht te begrijpen.

## Acceptatiecriteria

### Scenario 1: Natuurlijke taalquery uitvoeren

**Gegeven** ik beleid over een specifiek onderwerp wil vinden
**Wanneer** ik een vraag in natuurlijke taal invoer zoals "Wat zijn de regels over parkeren in woonwijken?"
**Dan** moet het systeem relevante beleidsdocumenten over parkeerregelgeving retourneren
**En** moeten de resultaten worden gerangschikt op semantische relevantie
**En** moet ik een uitleg zien waarom elk document relevant is

### Scenario 2: Vergelijkbaar beleid vinden

**Gegeven** ik een specifiek beleidsdocument bekijk
**Wanneer** ik op "Vergelijkbaar beleid vinden" klik
**Dan** moet het systeem AI gebruiken om semantisch vergelijkbare documenten te identificeren
**En** beleid met gerelateerde inhoud van verschillende bronnen tonen
**En** de overeenkomsten tussen documenten benadrukken
**En** me toestaan vergelijkbaar beleid naast elkaar te vergelijken

### Scenario 3: AI-gegenereerde samenvattingen krijgen

**Gegeven** ik zoekresultaten heb met meerdere lange beleidsdocumenten
**Wanneer** ik een AI-samenvatting voor een document aanvraag
**Dan** moet het systeem een beknopte samenvatting van het beleid genereren
**En** belangrijke punten en hoofdregelgeving benadrukken
**En** aangeven welke secties het meest relevant zijn voor mijn zoekopdracht
**En** de samenvatting leveren in mijn voorkeurstaal (Nederlands of Engels)

### Scenario 4: Vragen stellen over beleid

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik een specifieke vraag over het beleid stel met de AI-chatfunctie
**Dan** moet de AI de documentinhoud analyseren
**En** een nauwkeurig antwoord geven op basis van de beleidstekst
**En** de specifieke secties citeren die het antwoord ondersteunen
**En** me waarschuwen als het antwoord onzeker is of menselijke verificatie vereist

### Scenario 5: Beleid kruislings verwijzen

**Gegeven** ik onderzoek doe naar een onderwerp dat meerdere beleidsdomeinen omvat
**Wanneer** ik met semantisch zoeken naar een onderwerp zoek
**Dan** moet het systeem relevant beleid over verschillende bronnen identificeren
**En** verbanden tussen gerelateerd beleid tonen
**En** potentiële conflicten of tegenstrijdigheden benadrukken
**En** een geïntegreerd overzicht van alle relevante regelgeving bieden

### Scenario 6: Conceptgebaseerd filteren

**Gegeven** ik wil filteren op beleidsconcepten in plaats van zoekwoorden
**Wanneer** ik semantische concepten selecteer (bijv. "duurzaamheid", "openbare veiligheid", "economische ontwikkeling")
**Dan** moet het systeem documenten filteren op semantische betekenis
**En** documenten tonen die met het concept samenhangen, zelfs zonder exacte termen
**En** me toestaan meerdere concepten te combineren met AND/OR-logica

### Scenario 7: Beleidswijzigingen in de tijd detecteren

**Gegeven** ik wil begrijpen hoe een beleid is geëvolueerd
**Wanneer** ik de wijzigingsgeschiedenis voor een beleidsonderwerp bekijk
**Dan** moet de AI belangrijke wijzigingen identificeren en samenvatten
**En** een tijdlijn van beleidsupdates over verschillende versies tonen
**En** significante aanpassingen aan regelgeving benadrukken
**En** de impact van wijzigingen in eenvoudige taal uitleggen

### Scenario 8: Meertalig semantisch zoeken

**Gegeven** beleidsdocumenten bestaan in zowel Nederlands als Engels
**Wanneer** ik een zoekopdracht in het Nederlands uitvoer
**Dan** moet het systeem relevante resultaten in beide talen retourneren
**En** vertalingen leveren voor documenten in de andere taal
**En** semantische nauwkeurigheid over talen heen behouden
**En** me toestaan taalvoorkeuren voor resultaten te specificeren

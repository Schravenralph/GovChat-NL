# US006A: Natuurlijke Taal Beleidszoekopdracht

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** met natuurlijke taalvragen naar beleid te kunnen zoeken
**Zodat** ik relevante documenten kan vinden zonder exacte zoekwoorden te kennen

## Beschrijving

Het systeem moet AI gebruiken om natuurlijke taalquery's te begrijpen en semantisch relevante beleidsdocumenten te retourneren. Dit stelt gebruikers in staat om vragen in gewone taal te stellen en intelligente resultaten te ontvangen op basis van betekenis in plaats van alleen op zoekwoord-matching.

## Acceptatiecriteria

### Scenario 1: Natuurlijke taalquery uitvoeren

**Gegeven** ik beleid over een specifiek onderwerp wil vinden
**Wanneer** ik een vraag in natuurlijke taal invoer zoals "Wat zijn de regels over parkeren in woonwijken?"
**Dan** moet het systeem relevante beleidsdocumenten over parkeerregelgeving retourneren
**En** moeten de resultaten worden gerangschikt op semantische relevantie
**En** moet ik een uitleg zien waarom elk document relevant is

### Scenario 2: Complexe vragen afhandelen

**Gegeven** ik een vraag met meerdere onderdelen stel
**Wanneer** ik een query invoer zoals "Wat zijn de geluidsbeperkingen voor bouwwerkzaamheden bij scholen tijdens weekdagen?"
**Dan** moet het systeem alle belangrijke concepten identificeren (geluid, bouw, scholen, weekdagen)
**En** documenten retourneren die deze gecombineerde criteria behandelen
**En** markeren welke delen van mijn query elk document behandelt

### Scenario 3: Query-intentie begrijpen

**Gegeven** ik een vage of brede vraag invoer
**Wanneer** het systeem mijn query analyseert
**Dan** moet het verfijningen of gerelateerde onderwerpen voorstellen
**En** me de meest relevante resultaten tonen op basis van gangbare interpretaties
**En** me toestaan de query aan te passen op basis van suggesties

### Scenario 4: Meertalige query-ondersteuning

**Gegeven** beleidsdocumenten bestaan in zowel Nederlands als Engels
**Wanneer** ik een zoekopdracht in het Nederlands uitvoer
**Dan** moet het systeem relevante resultaten in beide talen retourneren
**En** semantische nauwkeurigheid over talen heen behouden
**En** vertalingen leveren voor resultaatfragmenten wanneer nodig

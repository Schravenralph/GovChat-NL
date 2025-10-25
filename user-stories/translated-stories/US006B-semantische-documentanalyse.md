# US006B: AI-gedreven Documentanalyse en Samenvattingen

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** dat AI beleidsdocumenten analyseert en samenvat
**Zodat** ik snel documentinhoud kan begrijpen zonder alles in detail te lezen

## Beschrijving

Het systeem moet AI gebruiken om beleidsdocumenten te analyseren en samenvattingen te genereren, vragen over specifieke documenten te beantwoorden en vergelijkbaar beleid te identificeren. Dit helpt gebruikers snel de relevantie van documenten te beoordelen en complexe beleidsinhoud te begrijpen.

## Acceptatiecriteria

### Scenario 1: AI-documentsamenvattingen genereren

**Gegeven** ik zoekresultaten heb met meerdere lange beleidsdocumenten
**Wanneer** ik een AI-samenvatting voor een document aanvraag
**Dan** moet het systeem een beknopte samenvatting van het beleid genereren
**En** belangrijke punten en hoofdregelgeving benadrukken
**En** aangeven welke secties het meest relevant zijn voor mijn zoekopdracht
**En** de samenvatting leveren in mijn voorkeurstaal (Nederlands of Engels)

### Scenario 2: Vragen stellen over specifiek beleid

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik een specifieke vraag over het beleid stel met de AI-chatfunctie
**Dan** moet de AI de documentinhoud analyseren
**En** een nauwkeurig antwoord geven op basis van de beleidstekst
**En** de specifieke secties citeren die het antwoord ondersteunen
**En** me waarschuwen als het antwoord onzeker is of menselijke verificatie vereist

### Scenario 3: Semantisch vergelijkbaar beleid vinden

**Gegeven** ik een specifiek beleidsdocument bekijk
**Wanneer** ik op "Vergelijkbaar beleid vinden" klik
**Dan** moet het systeem AI gebruiken om semantisch vergelijkbare documenten te identificeren
**En** beleid met gerelateerde inhoud van verschillende bronnen tonen
**En** de overeenkomsten tussen documenten benadrukken
**En** resultaten rangschikken op mate van gelijkenis

### Scenario 4: Beleid naast elkaar vergelijken

**Gegeven** ik vergelijkbaar beleid heb geïdentificeerd
**Wanneer** ik meerdere beleidsregels selecteer om te vergelijken
**Dan** moet het systeem ze naast elkaar weergeven
**En** belangrijke verschillen en overeenkomsten benadrukken
**En** me toestaan naar specifieke secties te navigeren
**En** een AI-gegenereerde vergelijkingssamenvatting bieden

# US003A: Basis Beleidszoekopdracht

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** basis zoekwoord-zoekopdrachten uit te kunnen voeren over gescand beleid
**Zodat** ik snel documenten kan vinden die specifieke termen bevatten

## Beschrijving

Gebruikers moeten door alle geïndexeerde beleidsdocumenten kunnen zoeken met zoekwoorden. De zoekfunctie moet werken over documenten van DSO, Gemeentebladen en aangepaste beleidsbronnen, en een uniforme zoekervaring bieden met gemarkeerde resultaten.

## Acceptatiecriteria

### Scenario 1: Basis zoekwoord zoeken uitvoeren

**Gegeven** het systeem heeft beleidsdocumenten van meerdere bronnen geïndexeerd
**Wanneer** ik een zoekterm in het zoekvak invoer
**En** ik op de zoekknop klik
**Dan** moet ik een lijst zien van documenten die dat zoekwoord bevatten
**En** moeten de resultaten documenttitel, bron, publicatiedatum en een fragment tonen
**En** moet de zoekterm worden gemarkeerd in de fragmenten

### Scenario 2: Geen resultaten afhandelen

**Gegeven** ik een zoekopdracht uitvoer
**Wanneer** geen documenten aan mijn zoekcriteria voldoen
**Dan** moet ik een "Geen resultaten gevonden"-bericht zien
**En** moet ik suggesties zien om mijn zoekopdracht te verbreden (andere zoekwoorden proberen)
**En** moet ik nog steeds mijn zoekopdracht kunnen wijzigen

### Scenario 3: Zoekresultaten sorteren

**Gegeven** ik zoekresultaten heb weergegeven
**Wanneer** ik een sorteeroptie selecteer (relevantie, datum nieuwste eerst, datum oudste eerst, alfabetisch)
**Dan** moeten de resultaten opnieuw worden geordend volgens de geselecteerde sorteermethode
**En** moet de sorteerselectie blijven bestaan bij navigatie

### Scenario 4: Aantal resultaten bekijken

**Gegeven** ik een zoekopdracht heb uitgevoerd
**Wanneer** de resultaten worden weergegeven
**Dan** moet ik het totale aantal overeenkomende documenten zien
**En** moet het aantal duidelijk zichtbaar zijn bovenaan de resultaten

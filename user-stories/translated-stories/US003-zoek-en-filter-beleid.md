# US003: Zoek en Filter Gescand Beleid

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** gescand beleid te kunnen zoeken en filteren op verschillende criteria
**Zodat** ik snel relevante beleidsdocumenten kan vinden uit meerdere bronnen

## Beschrijving

Gebruikers moeten door alle geïndexeerde beleidsdocumenten kunnen zoeken met zoekwoorden en filters kunnen toepassen om resultaten te verfijnen. De zoekfunctie moet werken over documenten van DSO, Gemeentebladen en aangepaste beleidsbronnen, en een uniforme zoekervaring bieden.

## Acceptatiecriteria

### Scenario 1: Basis zoekwoord zoeken uitvoeren

**Gegeven** het systeem heeft beleidsdocumenten van meerdere bronnen geïndexeerd
**Wanneer** ik een zoekterm in het zoekvak invoer
**En** ik op de zoekknop klik
**Dan** moet ik een lijst zien van documenten die dat zoekwoord bevatten
**En** moeten de resultaten documenttitel, bron, publicatiedatum en een fragment tonen
**En** moet de zoekterm worden gemarkeerd in de fragmenten

### Scenario 2: Filteren op beleidsbron

**Gegeven** ik een zoekopdracht heb uitgevoerd die documenten van meerdere bronnen retourneert
**Wanneer** ik een filter toepas om alleen documenten van "Gemeentebladen" te tonen
**Dan** moeten de resultaten worden bijgewerkt om alleen Gemeenteblad-documenten te tonen
**En** moet ik het aantal resultaten per beschikbare bron zien
**En** moet ik meerdere bronnen tegelijkertijd kunnen selecteren

### Scenario 3: Filteren op datumbereik

**Gegeven** ik zoekresultaten bekijk
**Wanneer** ik een datumbereikfilter instel (bijv. "Afgelopen 6 maanden" of aangepaste datums)
**Dan** moeten alleen documenten die binnen dat datumbereik zijn gepubliceerd worden weergegeven
**En** moet het aantal resultaten dienovereenkomstig worden bijgewerkt
**En** moet ik het datumfilter kunnen wissen om alle resultaten opnieuw te zien

### Scenario 4: Filteren op gemeente

**Gegeven** ik zoek naar beleidsdocumenten
**Wanneer** ik een gemeentefilter toepas (bijv. "Amsterdam", "Rotterdam")
**Dan** moeten alleen documenten van de geselecteerde gemeente worden getoond
**En** moet ik een lijst zien van alle beschikbare gemeenten met documentaantallen
**En** moet ik meerdere gemeenten kunnen selecteren

### Scenario 5: Filteren op documenttype

**Gegeven** ik zoekresultaten heb met verschillende documenttypen (PDF, HTML, DOCX)
**Wanneer** ik een documenttypefilter toepas
**Dan** moeten alleen documenten van het geselecteerde type worden weergegeven
**En** moet het filter het aantal documenten per type tonen
**En** moet ik dit kunnen combineren met andere filters

### Scenario 6: Zoekresultaten sorteren

**Gegeven** ik zoekresultaten heb weergegeven
**Wanneer** ik een sorteeroptie selecteer (relevantie, datum nieuwste eerst, datum oudste eerst, alfabetisch)
**Dan** moeten de resultaten opnieuw worden geordend volgens de geselecteerde sorteermethode
**En** moet de sorteerselectie blijven bestaan bij het toepassen van filters

### Scenario 7: Geen resultaten afhandelen

**Gegeven** ik een zoekopdracht uitvoer
**Wanneer** geen documenten aan mijn zoekcriteria voldoen
**Dan** moet ik een "Geen resultaten gevonden"-bericht zien
**En** moet ik suggesties zien om mijn zoekopdracht te verbreden (filters verwijderen, andere zoekwoorden proberen)
**En** moet ik nog steeds mijn zoekopdracht en filters kunnen wijzigen

### Scenario 8: Zoekfilters opslaan

**Gegeven** ik meerdere filters heb toegepast op mijn zoekopdracht
**Wanneer** ik op "Zoekopdracht opslaan" klik
**Dan** moet ik deze filtercombinatie een naam kunnen geven en opslaan
**En** deze later kunnen openen vanuit een menu "Opgeslagen zoekopdrachten"
**En** meldingen ontvangen wanneer nieuwe documenten overeenkomen met mijn opgeslagen zoekopdracht

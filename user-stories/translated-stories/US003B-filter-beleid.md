# US003B: Filter Beleidszoekopdracht Resultaten

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** zoekresultaten te kunnen filteren op verschillende criteria
**Zodat** ik resultaten kan verfijnen om de meest relevante beleidsdocumenten te vinden

## Beschrijving

Gebruikers moeten meerdere filters kunnen toepassen op zoekresultaten om hun zoekopdracht te verfijnen. Filters moeten bron, datumbereik, gemeente en documenttype omvatten, en moeten combineerbaar zijn om precieze zoekcriteria te creëren.

## Acceptatiecriteria

### Scenario 1: Filteren op beleidsbron

**Gegeven** ik een zoekopdracht heb uitgevoerd die documenten van meerdere bronnen retourneert
**Wanneer** ik een filter toepas om alleen documenten van "Gemeentebladen" te tonen
**Dan** moeten de resultaten worden bijgewerkt om alleen Gemeenteblad-documenten te tonen
**En** moet ik het aantal resultaten per beschikbare bron zien
**En** moet ik meerdere bronnen tegelijkertijd kunnen selecteren

### Scenario 2: Filteren op datumbereik

**Gegeven** ik zoekresultaten bekijk
**Wanneer** ik een datumbereikfilter instel (bijv. "Afgelopen 6 maanden" of aangepaste datums)
**Dan** moeten alleen documenten die binnen dat datumbereik zijn gepubliceerd worden weergegeven
**En** moet het aantal resultaten dienovereenkomstig worden bijgewerkt
**En** moet ik het datumfilter kunnen wissen om alle resultaten opnieuw te zien

### Scenario 3: Filteren op gemeente

**Gegeven** ik zoek naar beleidsdocumenten
**Wanneer** ik een gemeentefilter toepas (bijv. "Amsterdam", "Rotterdam")
**Dan** moeten alleen documenten van de geselecteerde gemeente worden getoond
**En** moet ik een lijst zien van alle beschikbare gemeenten met documentaantallen
**En** moet ik meerdere gemeenten kunnen selecteren

### Scenario 4: Filteren op documenttype

**Gegeven** ik zoekresultaten heb met verschillende documenttypen (PDF, HTML, DOCX)
**Wanneer** ik een documenttypefilter toepas
**Dan** moeten alleen documenten van het geselecteerde type worden weergegeven
**En** moet het filter het aantal documenten per type tonen
**En** moet ik dit kunnen combineren met andere filters

### Scenario 5: Meerdere filters combineren

**Gegeven** ik een bronfilter heb toegepast
**Wanneer** ik een datumbereikfilter en een gemeentefilter toevoeg
**Dan** moeten de resultaten alleen documenten tonen die aan ALLE filtercriteria voldoen
**En** moet ik het totale aantal actieve filters zien
**En** moet ik individuele filters kunnen verwijderen zonder alles te wissen

### Scenario 6: Alle filters wissen

**Gegeven** ik meerdere filters heb toegepast
**Wanneer** ik op "Alle filters wissen" klik
**Dan** moeten alle filters worden verwijderd
**En** moet de zoekopdracht alle resultaten opnieuw tonen
**En** moet ik een bevestiging zien dat filters zijn gewist

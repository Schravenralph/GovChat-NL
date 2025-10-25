# US007: Geautomatiseerde Beleidscategorisatie en Tagging

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** dat beleid automatisch wordt gecategoriseerd en getagd
**Zodat** ik snel kan navigeren en grote verzamelingen beleidsdocumenten kan organiseren

## Beschrijving

Het systeem moet gescande beleidsdocumenten automatisch analyseren en categoriseren met behulp van AI en vooraf gedefinieerde taxonomieën. Documenten moeten worden getagd met relevante categorieën, onderwerpen en metadata om betere organisatie, filtering en vindbaarheid mogelijk te maken.

## Acceptatiecriteria

### Scenario 1: Nieuwe documenten automatisch categoriseren

**Gegeven** een nieuw beleidsdocument is gescand en geïndexeerd
**Wanneer** het document wordt verwerkt
**Dan** moet het systeem automatisch primaire en secundaire categorieën toewijzen
**En** moeten categorieën gebaseerd zijn op een vooraf gedefinieerde taxonomie (bijv. "Financiën", "Gezondheidszorg", "Infrastructuur")
**En** moet het betrouwbaarheidsniveau voor elke categorie worden weergegeven
**En** moet ik automatische categorisaties kunnen beoordelen en overschrijven

### Scenario 2: Automatische tags genereren

**Gegeven** een beleidsdocument is gescand
**Wanneer** de AI de documentinhoud verwerkt
**Dan** moeten relevante tags automatisch worden gegenereerd (bijv. "parkeren", "bestemmingsplan", "vergunningen")
**En** moeten tags worden geëxtraheerd uit zowel de documenttitel als de inhoud
**En** moeten de meest relevante tags worden geprioriteerd
**En** moet ik maximaal 10 tags per document zien

### Scenario 3: Handmatig tagbeheer

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik tags wil toevoegen of wijzigen
**Dan** moet ik handmatig aangepaste tags kunnen toevoegen
**En** moet ik automatisch gegenereerde tags kunnen verwijderen
**En** moet het systeem tags voorstellen op basis van vergelijkbare documenten
**En** moeten tags worden opgeslagen en onmiddellijk doorzoekbaar zijn

### Scenario 4: Bladeren per categorie

**Gegeven** ik beleid per categorie wil verkennen
**Wanneer** ik naar de categoriebrowser navigeer
**Dan** moet ik een hiërarchische weergave van alle categorieën zien
**En** moet elke categorie het aantal documenten tonen dat deze bevat
**En** moet ik subcategorieën kunnen uitvouwen
**En** moet het klikken op een categorie de resultaten filteren om alleen die documenten te tonen

### Scenario 5: Aangepaste categorisatieregels maken

**Gegeven** ik een beheerder ben die het categorisatiesysteem configureert
**Wanneer** ik een aangepaste categorisatieregel maak
**Dan** moet ik kunnen definiëren:
- Regelnaam en beschrijving
- Zoekwoorden of patronen die de categorie activeren
- Prioriteitsniveau voor de regel
- Of de categorie automatisch moet worden toegepast of voorgesteld
**En** moet de regel worden toegepast op toekomstige documenten
**En** moet ik deze achteraf kunnen toepassen op bestaande documenten

### Scenario 6: Taggebaseerd filteren

**Gegeven** ik zoek naar beleidsdocumenten
**Wanneer** ik filter op specifieke tags
**Dan** moeten alleen documenten met die tags worden weergegeven
**En** moet ik meerdere tags kunnen combineren (AND/OR-logica)
**En** moet ik tagsuggesties zien op basis van huidige zoekresultaten
**En** moet het aantal resultaten worden bijgewerkt als ik tags toevoeg of verwijder

### Scenario 7: Categoriestatistieken bekijken

**Gegeven** ik de verzameling beleidsdocumenten wil begrijpen
**Wanneer** ik categoriestatistieken bekijk
**Dan** moet ik zien:
- Aantal documenten per categorie
- Meest voorkomende tags over alle documenten
- Categorieverdeling in de tijd
- Groeitrends voor specifieke categorieën
**En** moet ik statistieken kunnen exporteren als grafieken of rapporten

### Scenario 8: Multi-label classificatie

**Gegeven** een beleidsdocument meerdere onderwerpen omvat
**Wanneer** het systeem het document categoriseert
**Dan** moet het meerdere relevante categorieën toewijzen
**En** moet elke categorie een betrouwbaarheidsscore hebben
**En** moet de primaire categorie duidelijk worden aangegeven
**En** moet ik alle toegewezen categorieën in de documentmetadata kunnen zien

### Scenario 9: Categoriehiërarchie-navigatie

**Gegeven** categorieën zijn georganiseerd in een hiërarchie (ouder-kind-relaties)
**Wanneer** ik een oudercategorie selecteer
**Dan** moet ik opties zien om subcategorieën op te nemen of uit te sluiten
**En** moet broodkruimelnavigatie het huidige categoriepad tonen
**En** moet ik snel kunnen springen naar ouder- of zustercategorieën

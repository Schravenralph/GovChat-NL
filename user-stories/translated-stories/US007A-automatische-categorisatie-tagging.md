# US007A: Automatische Beleidscategorisatie en Tagging

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** dat beleid automatisch wordt gecategoriseerd en getagd door AI
**Zodat** documenten consistent worden georganiseerd zonder handmatige inspanning

## Beschrijving

Het systeem moet gescande beleidsdocumenten automatisch analyseren en passende categorieën en tags toewijzen met behulp van AI. Dit zorgt voor consistente organisatie over grote documentverzamelingen en vermindert de noodzaak voor handmatige classificatie.

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

### Scenario 3: Multi-label classificatie

**Gegeven** een beleidsdocument meerdere onderwerpen omvat
**Wanneer** het systeem het document categoriseert
**Dan** moet het meerdere relevante categorieën toewijzen
**En** moet elke categorie een betrouwbaarheidsscore hebben
**En** moet de primaire categorie duidelijk worden aangegeven
**En** moet ik alle toegewezen categorieën in de documentmetadata kunnen zien

### Scenario 4: Categorisatiebetrouwbaarheid bekijken

**Gegeven** ik automatisch gecategoriseerde documenten bekijk
**Wanneer** ik de categorietoewijzingen bekijk
**Dan** moet ik een betrouwbaarheidsscore zien voor elke categorie (0-100%)
**En** moeten toewijzingen met lage betrouwbaarheid worden gemarkeerd voor beoordeling
**En** moet ik documenten kunnen sorteren op betrouwbaarheidsniveau

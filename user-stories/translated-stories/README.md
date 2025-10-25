# Beleidsscanner User Stories

Deze map bevat user stories voor de Beleidsscanner-functie, die het scannen en indexeren van beleidsdocumenten mogelijk maakt van bronnen buiten het DSO, inclusief Gemeentebladen en aangepaste beleidswebsites.

## User Story Organisatie

### Kern Infrastructuur Stories

**US001: Scan Gemeentebladen voor Beleidsdocumenten**
- Gefocuste story over het scannen van gemeentelijke publicatiebladen (Gemeentebladen)
- 4 scenario's over succesvol scannen, meerdere gemeenten, foutafhandeling en duplicaatpreventie

**US002: Configureer Aangepaste Beleidsbronnen**
- Gefocuste story voor het instellen van aanvullende beleidsbronnen naast DSO en Gemeentebladen
- 5 scenario's over het toevoegen van bronnen, configuratie, testen, deactivering en validatie

### Zoek- en Ontdekkingsstories (Opgesplitst)

Originele US003 werd opgesplitst in 3 gefocuste stories:

**US003A: Basis Beleidszoekopdracht**
- Kernzoekfunctionaliteit met zoekwoord-zoekopdrachten
- 4 scenario's over basis zoeken, geen resultaten, sorteren en resultaataantallen

**US003B: Filter Beleidszoekopdracht Resultaten**
- Filtermogelijkheden voor het verfijnen van zoekresultaten
- 6 scenario's over filteren op bron, datum, gemeente, documenttype, filters combineren en filters wissen

**US003C: Opslaan en Beheren van Zoekopdrachten**
- Geavanceerd zoekbeheer en meldingen
- 6 scenario's over zoekopdrachten opslaan, toegang tot opgeslagen zoekopdrachten, uitvoeren, meldingen, verwijderen en hernoemen

### Document Toegangsstories (Opgesplitst)

Originele US004 werd opgesplitst in 3 gefocuste stories:

**US004A: Bekijk Beleidsdocument Details en Voorbeeld**
- Bekijken en voorvertonen van documenten in verschillende formaten
- 5 scenario's over documentdetails, PDF-voorvertoning, HTML-weergave, niet-beschikbare documenten en links kopiëren

**US004B: Download Beleidsdocumenten**
- Downloaden van enkele en meerdere documenten
- 5 scenario's over enkele downloads, bulkdownloads, selectie, grote verzamelingen en foutafhandeling

**US004C: Volg Document Toegangsgeschiedenis**
- Bekijk- en downloadgeschiedenis volgen
- 6 scenario's over automatische tracking, recent bekeken, downloads, geschiedenistoegang, geschiedenis wissen en bewaringsinstellingen

### Scanbeheer Stories (Opgesplitst)

Originele US005 werd opgesplitst in 3 gefocuste stories:

**US005A: Configureer en Voer Scan-schema's Uit**
- Het instellen van geautomatiseerde scanschema's
- 5 scenario's over schema-configuratie, handmatige triggers, pauzeren/hervatten, prioriteiten en schema's bewerken

**US005B: Monitor Actieve Scans en Geschiedenis**
- Scanvoortgang monitoren en historische gegevens bekijken
- 4 scenario's over actieve scans, scangeschiedenis, gedetailleerde logs en prestatiestatistieken

**US005C: Behandel Scanfouten en Verstuur Meldingen**
- Foutafhandeling en meldingssysteem
- 6 scenario's over automatische herhaling, aanhoudende fouten, meldingsvoorkeuren, succesvol-meldingen, samenvattingsmodus en fouttypeafhandeling

### AI-gedreven Functies (Opgesplitst)

Originele US006 werd opgesplitst in 3 gefocuste stories:

**US006A: Natuurlijke Taal Beleidszoekopdracht**
- Verwerking van natuurlijke taalquery's
- 4 scenario's over natuurlijke taalquery's, complexe vragen, query-intentie en meertalige ondersteuning

**US006B: AI-gedreven Documentanalyse en Samenvattingen**
- Documentanalyse en vraag-en-antwoord mogelijkheden
- 4 scenario's over AI-samenvattingen, vragen stellen, vergelijkbaar beleid vinden en naast-elkaar vergelijken

**US006C: Conceptgebaseerd Filteren en Beleidsevolutie**
- Geavanceerde semantische analysefuncties
- 5 scenario's over conceptfiltering, concepttaxonomie, beleidswijzigingsdetectie, kruisverwijzingen en gemeentevergelijkingen

### Categorisatiesysteem (Opgesplitst)

Originele US007 werd opgesplitst in 4 gefocuste stories:

**US007A: Automatische Beleidscategorisatie en Tagging**
- AI-gedreven automatische classificatie
- 4 scenario's over auto-categorisatie, tag-generatie, multi-label classificatie en betrouwbaarheidsscores

**US007B: Handmatig Categorie- en Tagbeheer**
- Handmatig beheer en correcties
- 5 scenario's over handmatige tags, categorieën bewerken, bulkbewerking, tagsuggesties en statistieken

**US007C: Bladeren en Filteren op Categorieën en Tags**
- Navigatie en filteren met taxonomie
- 6 scenario's over categoriehiërarchie, tagfiltering, navigatie, gerelateerde tags, tagcloud en statistieken

**US007D: Maak Aangepaste Categorisatieregels**
- Door beheerder gedefinieerde classificatieregels
- 6 scenario's over regelcreatie, testen, prioriteitsbeheer, achteraf toepassen, blacklists en analyses

## Implementatieprioriteit

### Fase 1: Fundament (Must Have)
- US001: Scan Gemeentebladen
- US002: Configureer Aangepaste Beleidsbronnen
- US003A: Basis Beleidszoekopdracht
- US004A: Bekijk Beleidsdocumenten
- US004B: Download Beleidsdocumenten
- US005A: Configureer Scan-schema's

### Fase 2: Verbeterde Bruikbaarheid (Should Have)
- US003B: Filter Beleidszoekopdracht Resultaten
- US005B: Monitor Scanactiviteit
- US005C: Scan Foutafhandeling en Meldingen
- US007A: Automatische Categorisatie en Tagging
- US007C: Bladeren en Filteren op Categorieën

### Fase 3: Geavanceerde Functies (Could Have)
- US003C: Opgeslagen Zoekopdrachten
- US004C: Document Toegangsgeschiedenis
- US006A: Natuurlijke Taal Zoeken
- US006B: AI Documentanalyse
- US007B: Handmatig Categoriebeheer
- US007D: Aangepaste Categorisatieregels

### Fase 4: AI-excellentie (Nice to Have)
- US006C: Conceptgebaseerd Filteren en Beleidsevolutie

## Opmerkingen

- Alle stories volgen het "Als... Heb ik nodig... Zodat..." formaat
- Acceptatiecriteria gebruiken Gherkin-syntaxis (Gegeven/Wanneer/Dan)
- Engelse versies zijn beschikbaar in de hoofd `user-stories/` map
- Stories gemarkeerd met letters (A, B, C, D) zijn opsplitsingen van grotere originele stories

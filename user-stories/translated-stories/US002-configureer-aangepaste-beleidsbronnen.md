# US002: Configureer Aangepaste Beleidsbronnen

## User Story

**Als** systeembeheerder
**Heb ik nodig** aangepaste websitebronnen te kunnen configureren voor het scannen van beleid
**Zodat** ik de scanner kan uitbreiden met aanvullende beleidsrepositories naast DSO en Gemeentebladen

## Beschrijving

Het systeem moet beheerders in staat stellen om aangepaste beleidsbronnen van verschillende websites toe te voegen, te configureren en te beheren. Dit maakt de beleidsscanner flexibel en uitbreidbaar, met ondersteuning voor verschillende soorten beleidsrepositories met variërende structuren en formaten.

## Acceptatiecriteria

### Scenario 1: Nieuwe aangepaste beleidsbron toevoegen

**Gegeven** ik ben ingelogd als beheerder
**Wanneer** ik naar de configuratiepagina voor beleidsbronnen navigeer
**En** ik een bronnaam, URL en brontype verstrek
**En** ik de nieuwe bronconfiguratie indien
**Dan** moet de nieuwe bron worden toegevoegd aan de lijst met actieve bronnen
**En** moet ik een bevestigingsbericht zien
**En** moet de bron beschikbaar zijn voor scannen

### Scenario 2: Bronspecifieke instellingen configureren

**Gegeven** ik een nieuwe aangepaste beleidsbron toevoeg
**Wanneer** ik de broninstellingen configureer
**Dan** moet ik kunnen specificeren:
- Documentselectorpatronen (CSS-selectors of XPath)
- Metadata-extractieregels (titel, datum, categorie)
- Scanfrequentie (dagelijks, wekelijks, maandelijks)
- Documenttypefilters (PDF, HTML, DOCX)
**En** moet het systeem de configuratie valideren voordat deze wordt opgeslagen

### Scenario 3: Beleidsbron-configuratie testen

**Gegeven** ik een nieuwe aangepaste beleidsbron heb geconfigureerd
**Wanneer** ik op de knop "Configuratie testen" klik
**Dan** moet het systeem proberen de bron te scannen
**En** een voorbeeld van gevonden documenten tonen (max 10)
**En** eventuele configuratiefouten of waarschuwingen weergeven
**En** de geëxtraheerde metadata tonen ter validatie

### Scenario 4: Beleidsbron deactiveren

**Gegeven** ik een actieve beleidsbron heb die niet langer relevant is
**Wanneer** ik de bron deactiveer vanaf de configuratiepagina
**Dan** moet de bron in het systeem blijven maar als inactief worden gemarkeerd
**En** moet deze worden uitgesloten van toekomstige scans
**En** moeten bestaande geïndexeerde documenten van die bron toegankelijk blijven

### Scenario 5: URL-toegankelijkheid valideren

**Gegeven** ik een nieuwe beleidsbron met een URL configureer
**Wanneer** ik de configuratie indien
**Dan** moet het systeem verifiëren dat de URL toegankelijk is
**En** een fout tonen als de URL 404 of een time-out retourneert
**En** me waarschuwen als de URL authenticatie vereist

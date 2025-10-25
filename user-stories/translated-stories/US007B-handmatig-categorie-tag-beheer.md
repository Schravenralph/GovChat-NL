# US007B: Handmatig Categorie- en Tagbeheer

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** handmatig categorieën en tags te kunnen toevoegen, bewerken en verwijderen
**Zodat** ik automatische toewijzingen kan corrigeren en domein-specifieke classificaties kan toevoegen

## Beschrijving

Gebruikers moeten categorieën en tags voor beleidsdocumenten handmatig kunnen beheren. Dit maakt correcties van automatische toewijzingen mogelijk en stelt gebruikers in staat om gespecialiseerde classificaties toe te voegen die mogelijk niet automatisch worden vastgelegd.

## Acceptatiecriteria

### Scenario 1: Handmatig tagbeheer

**Gegeven** ik een beleidsdocument bekijk
**Wanneer** ik tags wil toevoegen of wijzigen
**Dan** moet ik handmatig aangepaste tags kunnen toevoegen
**En** moet ik automatisch gegenereerde tags kunnen verwijderen
**En** moet het systeem tags voorstellen op basis van vergelijkbare documenten
**En** moeten tags worden opgeslagen en onmiddellijk doorzoekbaar zijn

### Scenario 2: Documentcategorieën bewerken

**Gegeven** ik de categorisatie van een document bekijk
**Wanneer** ik de toegewezen categorieën wil wijzigen
**Dan** moet ik categorieën kunnen toevoegen of verwijderen
**En** moet ik de primaire categorieaanduiding kunnen wijzigen
**En** moeten wijzigingen worden bijgehouden met tijdstempel en gebruikers-ID
**En** moet ik een bevestiging zien wanneer wijzigingen zijn opgeslagen

### Scenario 3: Categorieën en tags bulksgewijs bewerken

**Gegeven** ik meerdere documenten heb geselecteerd
**Wanneer** ik categorieën of tags op al deze wil toepassen
**Dan** moet ik categorieën/tags aan alle geselecteerde documenten kunnen toevoegen
**En** moet ik categorieën/tags van alle geselecteerde documenten kunnen verwijderen
**En** moet ik een samenvatting zien van hoeveel documenten worden beïnvloed
**En** moet ik de bulkbewerking kunnen bevestigen of annuleren

### Scenario 4: Tagsuggesties op basis van inhoud

**Gegeven** ik tags aan een document toevoeg
**Wanneer** ik begin met typen van een tag
**Dan** moet het systeem bestaande tags voorstellen die overeenkomen
**En** tonen hoeveel andere documenten elke voorgestelde tag gebruiken
**En** me toestaan een nieuwe tag te maken als er geen overeenkomt
**En** me waarschuwen als de nieuwe tag erg lijkt op een bestaande

### Scenario 5: Tag- en categoriegebruiksstatistieken bekijken

**Gegeven** ik wil begrijpen welke tags en categorieën het meest voorkomen
**Wanneer** ik de tag-/categoriestatistiekenpagina open
**Dan** moet ik een lijst zien van alle tags met gebruiksaantallen
**En** moet ik alle categorieën zien met documentaantallen
**En** moet ik vergelijkbare of dubbele tags kunnen samenvoegen
**En** moet ik ongebruikte tags kunnen verwijderen

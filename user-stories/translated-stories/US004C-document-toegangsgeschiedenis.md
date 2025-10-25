# US004C: Volg Document Toegangsgeschiedenis

## User Story

**Als** beleidsonderzoeker
**Heb ik nodig** mijn document bekijk- en downloadgeschiedenis te kunnen volgen
**Zodat** ik gemakkelijk kan terugkeren naar eerder geopende documenten en een overzicht kan houden van mijn onderzoek

## Beschrijving

Het systeem moet automatisch registreren wanneer gebruikers beleidsdocumenten bekijken of downloaden. Deze geschiedenis moet toegankelijk zijn voor gebruikers, zodat ze snel kunnen terugkeren naar documenten die ze eerder hebben geopend.

## Acceptatiecriteria

### Scenario 1: Automatisch documentweergaven bijhouden

**Gegeven** ik ben ingelogd als gebruiker
**Wanneer** ik een document bekijk
**Dan** moet het systeem deze actie registreren met een tijdstempel
**En** moet het document verschijnen in mijn lijst "Recent bekeken"
**En** moet dit gebeuren zonder handmatige actie van mij

### Scenario 2: Recent geopende documenten bekijken

**Gegeven** ik meerdere documenten heb bekeken
**Wanneer** ik naar "Recent bekeken documenten" navigeer
**Dan** moet ik een chronologische lijst zien van documenten die ik heb bekeken
**En** moet elke invoer de documenttitel, bron en bekijkdatum tonen
**En** moet ik op elke invoer kunnen klikken om het document opnieuw te bekijken

### Scenario 3: Documentdownloads bijhouden

**Gegeven** ik een document download
**Wanneer** de download succesvol is voltooid
**Dan** moet het systeem de download registreren met een tijdstempel
**En** moet het document verschijnen in mijn "Downloadgeschiedenis"
**En** moet ik de downloaddatum en bestandsnaam zien

### Scenario 4: Downloadgeschiedenis raadplegen

**Gegeven** ik eerder documenten heb gedownload
**Wanneer** ik naar mijn "Downloadgeschiedenis" navigeer
**Dan** moet ik alle documenten zien die ik heb gedownload
**En** moet ik elk document opnieuw kunnen downloaden vanuit de geschiedenis
**En** moet ik kunnen filteren op datumbereik of documenttype

### Scenario 5: Bekijkgeschiedenis wissen

**Gegeven** ik mijn bekijkgeschiedenis wil wissen
**Wanneer** ik "Geschiedenis wissen" selecteer en bevestig
**Dan** moet mijn lijst met recent bekeken documenten worden geleegd
**En** moet ik een bevestigingsbericht zien
**En** moet mijn downloadgeschiedenis intact blijven tenzij ook gewist

### Scenario 6: Voorkeuren voor geschiedenisbewaring instellen

**Gegeven** ik mijn accountinstellingen beheer
**Wanneer** ik instellingen voor geschiedenisbewaring configureer
**Dan** moet ik kunnen instellen hoe lang de geschiedenis wordt bewaard (1 week, 1 maand, 3 maanden, altijd)
**En** moet ik automatische geschiedenisregistratie kunnen in-/uitschakelen
**En** moet oude geschiedenis buiten de bewaartermijn automatisch worden verwijderd

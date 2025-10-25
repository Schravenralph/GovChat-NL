# US005: Beheer Beleidsscan-schema's

## User Story

**Als** systeembeheerder
**Heb ik nodig** geautomatiseerde beleidsscan-schema's te kunnen beheren en monitoren
**Zodat** het systeem up-to-date blijft met de nieuwste beleidsdocumenten zonder handmatige interventie

## Beschrijving

Het systeem moet geautomatiseerde, geplande scans van alle geconfigureerde beleidsbronnen ondersteunen. Beheerders moeten scanfrequenties kunnen configureren, scanstatus kunnen monitoren en scangeschiedenis kunnen bekijken om ervoor te zorgen dat de beleidsdatabase actueel blijft.

## Acceptatiecriteria

### Scenario 1: Scan-schema voor een bron configureren

**Gegeven** ik een beleidsbron beheer
**Wanneer** ik de scan-schema-instellingen configureer
**Dan** moet ik kunnen instellen:
- Scanfrequentie (per uur, dagelijks, wekelijks, maandelijks)
- Specifiek tijdstip van de dag voor scans
- Dagen van de week (voor wekelijkse scans)
- Datum van de maand (voor maandelijkse scans)
**En** moet het schema worden gevalideerd voordat het wordt opgeslagen
**En** moet ik het volgende geplande scantijdstip zien

### Scenario 2: Actieve scantaken bekijken

**Gegeven** ik op het scanbeheer-dashboard ben
**Wanneer** ik de lijst met actieve scans bekijk
**Dan** moet ik alle momenteel lopende scans zien met:
- Bronnaam
- Starttijd
- Voortgangspercentage (indien beschikbaar)
- Aantal verwerkte documenten
- Geschatte resterende tijd
**En** moet ik een lopende scan kunnen annuleren indien nodig

### Scenario 3: Scangeschiedenis bekijken

**Gegeven** ik eerdere scanactiviteiten wil bekijken
**Wanneer** ik de scangeschiedenispagina open
**Dan** moet ik een lijst met voltooide scans zien met:
- Bronnaam
- Start- en eindtijd
- Status (geslaagd, gedeeltelijk geslaagd, mislukt)
- Aantal gevonden documenten
- Aantal nieuwe documenten toegevoegd
- Aantal bijgewerkte documenten
- Eventuele fouten of waarschuwingen
**En** moet ik kunnen filteren op bron, datumbereik en status

### Scenario 4: Scanfouten afhandelen

**Gegeven** een geplande scan is mislukt
**Wanneer** ik de scanstatus controleer
**Dan** moet ik een duidelijke foutmelding zien die de mislukking verklaart
**En** moet het systeem automatisch mislukte scans opnieuw proberen (tot 3 pogingen)
**En** moet ik een melding ontvangen als alle herhalingspogingen mislukken
**En** moet ik handmatig een herscan kunnen activeren

### Scenario 5: Scannen pauzeren en hervatten

**Gegeven** ik systeemonderhoud moet uitvoeren
**Wanneer** ik alle scanactiviteiten pauzeer
**Dan** moeten alle actieve scans hun huidige document voltooien
**En** mogen er geen nieuwe scans starten
**En** moeten geplande scans in de wachtrij worden gezet voor later
**En** moet ik het scannen kunnen hervatten wanneer ik klaar ben

### Scenario 6: Scanprestaties monitoren

**Gegeven** ik de scanefficiëntie wil optimaliseren
**Wanneer** ik scanprestatiestatistieken bekijk
**Dan** moet ik zien:
- Gemiddelde scanduur per bron
- Documenten gescand per uur
- Succespercentage
- Meest voorkomende fouten
- Resourcegebruik (CPU, geheugen, netwerk)
**En** moet ik statistieken kunnen exporteren als CSV of JSON

### Scenario 7: Scanprioriteiten configureren

**Gegeven** ik meerdere beleidsbronnen heb geconfigureerd
**Wanneer** ik scanprioriteiten instel voor verschillende bronnen
**Dan** moeten bronnen met hoge prioriteit eerst worden gescand
**En** moet ik prioriteitsniveaus kunnen toewijzen (hoog, gemiddeld, laag)
**En** moet prioriteit de wachtrijvolgorde beïnvloeden wanneer meerdere scans zijn gepland

### Scenario 8: Scanmeldingen ontvangen

**Gegeven** ik meldingsvoorkeuren heb geconfigureerd
**Wanneer** een scan voltooid is of mislukt
**Dan** moet ik een melding ontvangen via:
- E-mail
- In-app melding
- Webhook (optioneel)
**En** moet ik kunnen configureren welke gebeurtenissen meldingen activeren
**En** moet ik ontvangers van meldingen kunnen aanpassen

# US005A: Configureer en Voer Scan-schema's Uit

## User Story

**Als** systeembeheerder
**Heb ik nodig** geautomatiseerde scan-schema's voor beleidsbronnen te kunnen configureren
**Zodat** beleidsdocumenten automatisch worden bijgewerkt zonder handmatige interventie

## Beschrijving

Het systeem moet beheerders in staat stellen om geautomatiseerde scanschema's in te stellen voor elke beleidsbron. Beheerders moeten kunnen definiëren wanneer en hoe vaak scans plaatsvinden, en handmatig scans kunnen activeren wanneer nodig.

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

### Scenario 2: Handmatig een scan activeren

**Gegeven** ik een beleidsbron onmiddellijk wil bijwerken
**Wanneer** ik op "Scan nu uitvoeren" klik voor een specifieke bron
**Dan** moet de scan onmiddellijk starten
**En** moet ik een bevestiging zien dat de scan is gestart
**En** mag de scan het reguliere schema niet verstoren

### Scenario 3: Scannen pauzeren en hervatten

**Gegeven** ik systeemonderhoud moet uitvoeren
**Wanneer** ik alle scanactiviteiten pauzeer
**Dan** moeten alle actieve scans hun huidige document voltooien
**En** mogen er geen nieuwe scans starten
**En** moeten geplande scans in de wachtrij worden gezet voor later
**En** moet ik het scannen kunnen hervatten wanneer ik klaar ben

### Scenario 4: Scanprioriteiten configureren

**Gegeven** ik meerdere beleidsbronnen heb geconfigureerd
**Wanneer** ik scanprioriteiten instel voor verschillende bronnen
**Dan** moeten bronnen met hoge prioriteit eerst worden gescand
**En** moet ik prioriteitsniveaus kunnen toewijzen (hoog, gemiddeld, laag)
**En** moet prioriteit de wachtrijvolgorde beïnvloeden wanneer meerdere scans zijn gepland

### Scenario 5: Bestaande scan-schema's bewerken

**Gegeven** ik een bestaand scan-schema heb
**Wanneer** ik de schema-instellingen wijzig
**Dan** moeten de wijzigingen onmiddellijk worden opgeslagen
**En** moet het volgende geplande scantijdstip opnieuw worden berekend
**En** moet ik een bevestiging zien van het bijgewerkte schema

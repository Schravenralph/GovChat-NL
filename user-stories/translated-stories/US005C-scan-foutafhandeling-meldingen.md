# US005C: Behandel Scanfouten en Verstuur Meldingen

## User Story

**Als** systeembeheerder
**Heb ik nodig** op de hoogte te worden gesteld van scanfouten en automatische herstelmechanismen te hebben
**Zodat** scanproblemen snel worden opgelost en ik word geïnformeerd over aanhoudende problemen

## Beschrijving

Het systeem moet automatisch scanfouten afhandelen met herhalingslogica en beheerders op de hoogte stellen wanneer problemen aandacht vereisen. Dit zorgt ervoor dat tijdelijke problemen niet leiden tot gemiste updates, terwijl aanhoudende problemen op de juiste manier worden geëscaleerd.

## Acceptatiecriteria

### Scenario 1: Automatisch opnieuw proberen bij scanfout

**Gegeven** een geplande scan is mislukt door een tijdelijke fout
**Wanneer** het systeem de fout detecteert
**Dan** moet het de scan automatisch opnieuw proberen (tot 3 pogingen)
**En** progressief langer wachten tussen pogingen (5 min, 15 min, 30 min)
**En** elke herhalingspoging loggen met tijdstempel en reden

### Scenario 2: Melden bij aanhoudende fouten

**Gegeven** een scan is mislukt na alle herhaalingspogingen
**Wanneer** alle herhaalingspogingen zijn uitgeput
**Dan** moet ik een melding ontvangen over de fout
**En** moet de melding de bronnaam en foutdetails bevatten
**En** moet de scan als "mislukt" worden gemarkeerd in de geschiedenis

### Scenario 3: Meldingsvoorkeuren configureren

**Gegeven** ik een beheerder ben die meldingen instelt
**Wanneer** ik meldingsinstellingen configureer
**Dan** moet ik meldingskanalen kunnen kiezen:
- E-mail
- In-app melding
- Webhook (optioneel)
**En** moet ik kunnen configureren welke gebeurtenissen meldingen activeren
**En** moet ik ontvangers van meldingen kunnen instellen per rol of gebruiker

### Scenario 4: Meldingen van succesvolle scans ontvangen

**Gegeven** ik succesvol-meldingen heb ingeschakeld
**Wanneer** een scan succesvol is voltooid
**Dan** moet ik een melding ontvangen
**En** moet de melding het volgende bevatten:
- Bronnaam
- Voltooiingstijd van scan
- Aantal nieuwe documenten gevonden
- Aantal bijgewerkte documenten

### Scenario 5: Meldingssamenvattingsmodus

**Gegeven** ik geen individuele meldingen voor elke scan wil ontvangen
**Wanneer** ik de samenvattingsmodus configureer
**Dan** moet ik een enkele samenvattingsmelding ontvangen op een gepland tijdstip
**En** moet de samenvatting alle scanactiviteit sinds de laatste samenvatting bevatten
**En** moet ik de samenvattingsfrequentie kunnen instellen (dagelijks, wekelijks)

### Scenario 6: Specifieke fouttypes afhandelen

**Gegeven** verschillende soorten scanfouten kunnen optreden
**Wanneer** een scan mislukt
**Dan** moet het systeem de fout categoriseren (netwerk, authenticatie, parsing, enz.)
**En** passende herhalingslogica toepassen op basis van het fouttype
**En** sommige fouten (bijv. authenticatie) onmiddellijk melden zonder nieuwe pogingen
**En** tijdelijke fouten (bijv. netwerk time-out) automatisch opnieuw proberen

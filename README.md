
## Installation

För att köra projektet, följ dessa steg:

1. Klona projektet från GitHub:
   ```bash
   git clone <repo-url>
   cd <projektmapp>
   ```
2. Skapa och aktivera en virtuell miljö:
   ```bash
   python -m venv venv
   source venv/bin/activate  # På Windows: venv\Scripts\activate
   ```
3. Installera beroenden:
   ```bash
   pip install -r requirements.txt
   ```
   **OBS!** Flask och vissa Flask-relaterade paket installeras ibland inte automatiskt trots att de ligger i requirements.txt. Om de saknas, installera dem manuellt:
   ```bash
   pip install flask flask-login flask-wtf flask-sqlalchemy
   ```
4. Starta applikationen:
   ```bash
   flask run
   ```

## Funktionalitet utöver det uppenbara

- **Swish-inspirerad transferfunktion** – Smidig pengaöverföring mellan konton.
- **Interaktiv transaktionshistorik** – Se tidigare transaktioner i en dynamisk tabell.
- **Management-table** – Live-sökning och sortering av användarkonton.
- **Statistik efter land** – Visualisering av transaktioner på dashboarden.
- **Pengatvättsvarning** – Systemet identifierar misstänkta transaktioner och varnar.
- **Kundhantering** – Gå direkt till kundsida från management-sektionen.

## Kända problem och förbättringsområden

- **Långsam dashboard** – Mycket data hämtas vid varje laddning. En lösning vore att lagra information i sessioner eller en cache.
- **"View more" i transfer-funktionen** – Funktionen kunde inte implementeras helt då det uppstod problem med form-splitning.
- **Freeze-funktion på konton** – Behöver förbättras för att stoppa misstänkta transaktioner.
- **Flash-meddelanden** – Vissa valideringsmeddelanden fungerar inte optimalt.
- **Inputvalidering** – Kan förbättras för att säkerställa robusthet.


## Utvecklingsprocess och reflektion

- Projektet började med en relativt enkel och icke-responsiv design. Sent i utvecklingsprocessen bestämde jag mig för att skapa en mer modern och responsiv layout, vilket tog upp en del tid från mitt planerade backend-arbete. Detta ledde till att vissa delar blev något forcerade och hade kunnat förbättras med bättre planering.

- Trots detta anser jag att jag har täckt in både G och VG-kraven i stor utsträckning och att projektet uppfyller de viktigaste målen på ett tillfredsställande sätt.

## Möjliga framtida förbättringar

- Implementera en adminprofil där misstänkta transaktioner samlas i en inkorg istället för att bara printas.
- Förbättrad "View more"-funktionalitet för transfer-historiken.
- Optimerad prestanda genom caching eller sessioner.

## Sammanfattning

Projektet erbjuder en modern och interaktiv upplevelse för hantering av transaktioner och kontoadministration. Även om vissa funktioner kan förbättras har det en stabil grund och flera användbara funktioner för vidare utveckling.


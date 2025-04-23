# RPC Photo Upload Application

Den här applikationen är en containerbaserad webbapplikation för att ladda upp foton, läsa EXIF-data, och lagra information i en MySQL-databas.

## Funktioner
- Ladda upp bilder via en webbgränssnitt.
- Läser EXIF-data för GPS-position och datum då bilden togs.
- Lagrar information om foton i en MySQL-databas.
- Visa och hantera bilder via en webbsida.

## Förutsättningar
- **Docker** och **Docker Compose** installerat på din maskin.
- Tillgång till port **5000** (för applikationen) och **3306** (för MySQL).

## Installation och körning

1. **Kloning av repository**
   ```sh
   git clone https://github.com/TG-proton/rpctid.git
   cd rpctid
   ```

2. **Skapa och starta Docker-containrar**
   ```sh
   docker-compose up --build
   ```

3. **Verifiera att applikationen körs**
   - Öppna din webbläsare och gå till: [http://localhost:5000](http://localhost:5000)

4. **Stoppa containrar**
   Om du vill stoppa containrarna:
   ```sh
   docker-compose down
   ```

## Felsökning
- **MySQL startar långsamt:**
  - Applikationen väntar tills MySQL-tjänsten är redo innan den startar. Detta hanteras via `depends_on` och `healthcheck` i `docker-compose.yml`.

- **Portkonflikter:**
  - Kontrollera att portarna 5000 och 3306 inte används av andra tjänster.

## Beroenden
- Flask==2.0.1
- Flask-Dropzone==1.6.0
- EXIFRead==2.3.2
- mysql-connector-python==8.0.25

## Licens
Detta projekt är licensierat under MIT-licensen. Se [LICENSE](LICENSE) för detaljer.

## Bidrag
Pull requests är välkomna. För större ändringar, vänligen öppna en issue först för att diskutera vad du vill ändra.

## Författare
- **TG-proton**

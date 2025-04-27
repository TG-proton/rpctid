# Dokumentation för rpctid-projektet

## Syfte
Detta projekt är till för att lösa ett CORS-problem mellan en Flask-applikation och en Nginx-proxy.

## Struktur
- `app/`: Flask-applikationens kod.
- `nginx/`: Nginx-konfigurationsfiler.
- `logs/`: Loggfiler för felsökning.
- `docs/`: Dokumentation, inklusive denna README.md.
- `tests/`: Tester för applikationen.

## Steg för att lösa problemet
1. Dokumentera problemet och samla in relevanta filer.
/var/www/rpctid/
├── app/                    # Flask-applikationens kod
├── nginx/                  # Nginx-konfigurationsfiler
├── logs/                   # Loggfiler för felsökning
├── docs/                   # Dokumentation och README.md
└── tests/                  # Tester för Flask-applikationen

cd /var/www/rpctid
sudo cp app.py /var/www/rpctid/app/
sudo cp requirements.txt /var/www/rpctid/app/

sudo cp /etc/nginx/sites-available/tid.endre.se /var/www/rpctid/nginx/
sudo cp /var/log/nginx/error.log /var/www/rpctid/logs/

### Flask-loggar
Flask-loggar visas korrekt i terminalen men sparas inte alltid till fil.
docker ps:
CONTAINER ID   IMAGE        COMMAND                  CREATED        STATUS        PORTS                                         NAMES
2aa35849915c   rpctid-web   "flask run --host=0.…"   18 hours ago   Up 4 hours    0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   rpctid-web-1
08233cee3025   mysql:8.0    "docker-entrypoint.s…"   18 hours ago   Up 18 hours   3306/tcp, 33060/tcp                           rpctid-db-1

#### Lösning
För att skapa ny loggfil:
sudo docker logs rpctid-web-1 > /var/www/rpctid/logs/flask-error.log 2>&1

2. Publicera filerna till GitHub-repot.
 # "initiera ett Git-repo:" Jag har redan ett repo som nedan:
 # cd /var/www/rpctid
 # sudo git init
 # sudo git remote add origin https://github.com/TG-proton/rpctid.git

cd /var/www/rpctid
sudo git add .
sudo git commit -m "Initial struktur och dokumentation för CORS-felsökning"
sudo git branch -M main
sudo git push -u origin main
eller
sudo git push -u origin main --force
sudo git pull origin main --rebase


3. Felsöka Flask och Nginx för CORS-problemet.
4. Implementera lösningar och dokumentera resultat.

## Testresultat
Här dokumenterar vi resultaten av varje test vi kör:

### Test 1: Direktförfrågan till API
**Kommando:**
```
curl -i https://tid.endre.se/api/photos
```

**Resultat:**
admindeb@exif:~$ curl -i https://tid.endre.se/api/photos
HTTP/1.1 404 NOT FOUND
Server: nginx/1.18.0 (Ubuntu)
Date: Sun, 27 Apr 2025 15:52:51 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 232
Connection: keep-alive

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
admindeb@exif:~$    

### Test 2: Frontend-anrop
Resultatet av frontend-anrop från klienten:
Access to fetch at 'https://tid.endre.se/api/photos' from origin 'https://rpctid.endre.se' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource. If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
admin.html:57          GET https://tid.endre.se/api/photos net::ERR_FAILED 404 (NOT FOUND)
(anonymous) @ admin.html:57
admin.html:74 Error fetching data: TypeError: Failed to fetch
    at admin.html:57:9
    at admin.html:57:9


### Test 3: Frontend-anrop
admindeb@exif:~$ curl -i http://tid.endre.se:5000/api/photos
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 81
Access-Control-Allow-Origin: https://rpctid.endre.se
Server: Werkzeug/2.0.3 Python/3.9.22
Date: Sun, 27 Apr 2025 18:04:32 GMT

[["testfil.jpg","57.74060997","14.00190897","Thu, 05 Sep 2024 17:20:55 GMT",""]]
admindeb@exif:~$ 


### Copilot said: Tack för den senaste uppdateringen! 

Den visaratt Flask-applikationen fungerar korrekt på port 5000 och returnerar ett giltigt svar för endpointen /api/photos. Dessutom skickar Flask rätt CORS-header: Access-Control-Allow-Origin: https://rpctid.endre.se.

Problemet verkar nu ligga i Nginx-konfigurationen, som inte vidarebefordrar förfrågningar korrekt från https://tid.endre.se/api/photos till Flask-applikationen på http://127.0.0.1:5000/api/photos.
Sammanfattning av situationen

    Flask fungerar som det ska:
        När du gör en direktförfrågan till Flask (http://tid.endre.se:5000/api/photos), returneras ett korrekt svar.
        Flask inkluderar korrekt CORS-header.

    Nginx vidarebefordrar inte korrekt:
        När du anropar via https://tid.endre.se/api/photos, returneras en 404 Not Found.
        Detta tyder på att Nginx inte skickar förfrågningarna vidare till Flask-applikationen.

### Problem med API-vidarebefordran via Nginx
#### Symptom:
- API-anrop till `https://tid.endre.se/api/photos` resulterade i en `404 Not Found`.
- Direkta anrop till Flask via `http://tid.endre.se:5000/api/photos` fungerade korrekt.

#### Orsak:
- Nginx-konfigurationen för `proxy_pass` innehöll ett avslutande `/`, vilket orsakade att vidarebefordran inte fungerade som förväntat.

#### Lösning:
- Ändrade `proxy_pass` i Nginx-konfigurationen:
  ```nginx
  proxy_pass http://127.0.0.1:5000;
  ```
- Laddade om Nginx-konfigurationen:
  ```bash
  sudo nginx -t
  sudo systemctl reload nginx
  ```

#### Resultat:
- API-anrop via Nginx fungerar korrekt och returnerar data med nödvändiga CORS-headers.

admindeb@exif:~$ curl -i https://tid.endre.se/api/photos
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Sun, 27 Apr 2025 18:12:05 GMT
Content-Type: application/json
Content-Length: 81
Connection: keep-alive
Access-Control-Allow-Origin: https://rpctid.endre.se
Access-Control-Allow-Origin: https://rpctid.endre.se
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type

[["testfil.jpg","57.74060997","14.00190897","Thu, 05 Sep 2024 17:20:55 GMT",""]]
admindeb@exif:~$ 

- API anrop till https://tid.endre.se/api/photos fungerar.

### Test 4: Det huvudsakliga problemet: Ej fungerande klient 

https://rpctid.endre.se/admin.html visar ej API data från server https://tid.endre.se(api/photos

Failed to load resource: net::ERR_SSL_PROTOCOL_ERROR
admin.html:74 Error fetching data: TypeError: Failed to fetch
    at admin.html:57:9
(anonymous) @ admin.html:74



### Åtgärdslista för CORS-problem mellan `tid.endre.se` och `rpctid.endre.se`

#### Problem
När vi försöker göra en `fetch`-begäran från `https://rpctid.endre.se` till API:et på `https://tid.endre.se/api/photos`, blockeras detta av webbläsarens CORS-policy. Detta beror på att servern på `tid.endre.se` returnerar felaktiga CORS-headerar, specifikt:

- Headern `Access-Control-Allow-Origin` innehåller flera värden (`https://rpctid.endre.se, https://rpctid.endre.se`), vilket bryter mot CORS-specifikationen.
- Detta leder till att webbläsaren inte tillåter begäran och ger följande felmeddelande i konsolen:

```
Access to fetch at 'https://tid.endre.se/api/photos' from origin 'https://rpctid.endre.se' has been blocked by CORS policy: The 'Access-Control-Allow-Origin' header contains multiple values 'https://rpctid.endre.se, https://rpctid.endre.se', but only one is allowed.
```

#### Åtgärder
1. **Uppdatera servern på `tid.endre.se`**:
   - Se till att servern returnerar en korrekt och enkel `Access-Control-Allow-Origin`-header. Exempel:
     ```
     Access-Control-Allow-Origin: https://rpctid.endre.se
     ```
   - Undvik att inkludera flera värden i headern.

2. **Testa och verifiera lösningen**:
   - Efter att servern har uppdaterats, testa om `fetch`-begäran från `https://rpctid.endre.se` fungerar utan fel.
   - Verifiera i webbläsarkonsolen att inga CORS-relaterade fel längre visas.

3. **Dokumentera serverkonfigurationen**:
   - Lägg till dokumentation om hur CORS är konfigurerat för API:et i denna README-fil eller i utvecklingsdokumentationen.
   - Detta förhindrar att liknande problem uppstår i framtiden.

4. **Alternativ tillfällig lösning** (ej rekommenderad för produktionsmiljöer):
   - Om problemet kvarstår och en omedelbar fix krävs, kan `mode: 'no-cors'` användas i `fetch`-begäran. Detta begränsar dock åtkomsten till svarsinnehållet och bör undvikas i produktionskod.

#### Status
- Problemet är identifierat och en lösning på servernivå krävs.
- Ingen aktiv fix på klientens sida rekommenderas för närvarande.

---

Denna lista kan uppdateras när nya insikter eller lösningar tillkommer.




### Lösning: Hantera CORS i Flask

#### Problembeskrivning
När vi försöker göra en `fetch`-begäran från `https://rpctid.endre.se` till API:et på `https://tid.endre.se/api/photos`, uppstår ett CORS-fel eftersom både Flask och Nginx försöker sätta `Access-Control-Allow-Origin`-headern. Detta resulterar i en konflikt där webbläsaren avvisar begäran.

#### Vald lösning
Vi har beslutat att hantera all CORS-hantering i Flask och ta bort CORS-relaterade headers från Nginx-konfigurationen.

#### Genomförande
1. **Uppdatera Nginx-konfiguration:**
   Öppna filen `nginx/tid.endre.se` och ta bort följande rader från `/api/`-sektionen:
   ```nginx
   add_header Access-Control-Allow-Origin "https://rpctid.endre.se";
   add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
   add_header Access-Control-Allow-Headers "Authorization, Content-Type";
   ```

2. **Ladda om Nginx:**
   Efter att ha sparat ändringarna, kör följande kommandon för att testa och ladda om Nginx-konfigurationen:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Verifiera Flask-konfiguration:**
   Flask är redan konfigurerad att hantera CORS via `flask_cors`. Följande rad i `app.py` säkerställer att endast förfrågningar från `https://rpctid.endre.se` tillåts:
   ```python
   CORS(app, resources={r"/api/*": {"origins": "https://rpctid.endre.se"}})
   ```

4. **Testa API:et:**
   Kör följande kommando för att testa att CORS fungerar korrekt:
   ```bash
   curl -i -X OPTIONS https://tid.endre.se/api/photos -H "Origin: https://rpctid.endre.se"
   ```
   Kontrollera att endast en `Access-Control-Allow-Origin`-header returneras.

5. **Testa frontend-klienten:**
   Ladda om sidan på `https://rpctid.endre.se/admin.html` och verifiera att inga CORS-fel visas i webbläsarkonsolen.

#### Förväntat resultat
API-förfrågningar från `https://rpctid.endre.se` till `https://tid.endre.se` bör fungera utan problem, och inga `Access-Control-Allow-Origin`-konflikter bör uppstå.

#### Dokumentation
Alla ändringar har dokumenterats i detta `README.md`-avsnitt för framtida referens.

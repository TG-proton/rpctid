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
### TEST
admindeb@exif:~$ curl -i -X OPTIONS https://tid.endre.se/api/photos -H "Origin: https://rpctid.endre.se"
HTTP/1.1 204 No Content
Server: nginx/1.18.0 (Ubuntu)
Date: Sun, 27 Apr 2025 20:43:39 GMT
Connection: keep-alive
Access-Control-Allow-Origin: https://rpctid.endre.se
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type

Opera:

Access to fetch at 'https://tid.endre.se/api/photos' from origin 'https://rpctid.endre.se' has been blocked by CORS policy: The 'Access-Control-Allow-Origin' header contains multiple values 'https://rpctid.endre.se, https://rpctid.endre.se', but only one is allowed. Have the server send the header with a valid value, or, if an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
admin.html:57          GET https://tid.endre.se/api/photos net::ERR_FAILED 200 (OK)
(anonymous) @ admin.html:57
admin.html:74 Error fetching data: TypeError: Failed to fetch
    at admin.html:57:9

## CORS Problem och Lösning

### Problem
När vi försökte göra API-anrop från frontend (`https://rpctid.endre.se`) till backend (`https://tid.endre.se/api/`), stötte vi på följande problem:

1. **CORS-fel**:
   - Webbläsaren blockerade API-anrop eftersom `Access-Control-Allow-Origin`-headern innehöll dubbla värden. Detta orsakades av att både Nginx och Flask hanterade CORS-relaterade headers.

2. **Begränsad funktionalitet**:
   - Efter att ha löst CORS-problemet märkte vi att API:et endast returnerade textdata från MySQL, vilket innebär:
     - Inga miniatyrbilder visas.
     - Kartan fungerar inte.
     - Det är inte möjligt att ladda upp filer från frontend.

---

### Lösning

#### 1. CORS-fel
För att lösa problemet med dubbla `Access-Control-Allow-Origin`-headers flyttade vi all hantering av CORS till Flask. Följande steg implementerades:

1. **Uppdatering av Nginx-konfiguration**:
   Vi tog bort alla `add_header`-instruktioner för CORS från Nginx och lät Flask hantera detta. Här är den slutliga konfigurationen för `tid.endre.se`:

   ```nginx name=nginx/tid.endre.se
   server {
       listen 80;
       server_name tid.endre.se;

       # Omdirigera alla HTTP-förfrågningar till HTTPS
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl;
       server_name tid.endre.se;

       # SSL-certifikat (Certbot eller annat verktyg)
       ssl_certificate /etc/letsencrypt/live/tid.endre.se/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/tid.endre.se/privkey.pem;

       # Proxy till Flask-backend
       location /api/ {
           proxy_pass http://127.0.0.1:5000;  # Flask kör på port 5000
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           # Hantera preflight OPTIONS utan att lägga till CORS-headers
           if ($request_method = OPTIONS) {
               return 204;
           }
       }

       # Standardinställningar för statiska filer (om nödvändigt)
       location / {
           root /var/www/html;  # Byt ut detta om nödvändigt
           index index.html;
       }
   }
   ```

2. **Flask-konfiguration för CORS**:
   Vi säkerställde att Flask hanterar alla CORS-relaterade headers med hjälp av biblioteket `flask_cors`. Följande kod lades till i `app.py`:

   ```python name=app.py
   from flask_cors import CORS
   CORS(app, resources={r"/api/*": {"origins": "https://rpctid.endre.se"}})
   ```

---

#### 2. Begränsad funktionalitet

**Problemen som kvarstår:**
- API:et returnerar endast textdata från MySQL och saknar stöd för:
  - Generering och visning av miniatyrbilder.
  - Kartvy (t.ex. med koordinater från databasen).
  - Filuppladdning via frontend.

---

### Nästa steg
För att lösa dessa problem krävs följande:

1. **Miniatyrbilder**:
   - Backend måste generera miniatyrbilder baserat på de uppladdade filerna.
   - Kontrollera att frontend kan hämta och visa dessa via API:et.

2. **Karta**:
   - Implementera en funktion i frontend som visualiserar koordinater (exempelvis med Google Maps eller Leaflet.js).
   - Backend bör returnera koordinatdata i ett format som frontend kan använda.

3. **Filuppladdning**:
   - Kontrollera att backend kan ta emot och spara filer som laddas upp via frontend.
   - Säkerställ att API:et returnerar korrekta svar vid filuppladdning (t.ex. statuskod och fil-URL).

---

### Testning
Testa följande scenarier för att säkerställa att allt fungerar:

1. **API-anrop för visning av data**:
   - Kontrollera att API:et returnerar fullständig data inklusive miniatyrbilder och koordinater.

2. **Karta**:
   - Verifiera att kartan visas korrekt med markerade positioner baserat på koordinater.

3. **Filuppladdning**:
   - Testa att ladda upp filer via frontend och kontrollera att de sparas korrekt i backend.

---

### Slutsats
Genom att lösa CORS-problemet har vi möjliggjort API-kommunikation mellan backend och frontend. Nästa steg är att implementera stöd för miniatyrbilder, karta och filuppladdning för att fullborda applikationens funktionalitet.





Nedanstående dokumentation är beskrivning samt metod för felsökning:


# RPC TID - Diagnostikverktyg och Felsökning

Current Date and Time (UTC): 2025-04-27 22:30:07
Current User's Login: TG-proton

## Beskrivning

Detta dokument beskriver processen för att samla in diagnostikfiler från en server för att underlätta felsökning av webblösningen. Dokumentationen är särskilt utformad för att hjälpa AI-assistenter att förstå systemkonfigurationen och identifiera problem utan att förlora kontext i chattkonversationer.

## Repots struktur

/var/www/rpctid/
├── app/        # Flask-applikationens kod
├── nginx/      # Nginx-konfigurationsfiler
├── logs/       # Loggfiler för felsökning
├── docs/       # Dokumentation och README.md
└── tests/      # Tester för Flask-applikationen

## Steg för att samla in diagnostikfiler

Följ dessa kommandon för att samla in alla nödvändiga filer för diagnostik och felsökning:

### 1. Säkerställ att du är i korrekt katalog
cd /var/www/rpctid/

### 2. Samla in Nginx-konfigurationer
sudo cp /etc/nginx/sites-available/tid.endre.se nginx/
sudo cp /etc/nginx/nginx.conf nginx/

### 3. Samla in systemloggar
sudo cp /var/log/nginx/error.log logs/nginx_error.log
sudo cp /var/log/nginx/access.log logs/nginx_access.log
sudo bash -c "tail -n 200 /var/log/syslog > logs/syslog_tail.log"

### 4. Samla in Flask-applikationens loggar
# Om loggarna finns i /var/www/rpctid/logs/, kan du hoppa över detta steg
sudo bash -c "journalctl -u rpctid.service --no-pager -n 200 > logs/rpctid_service.log"

### 5. Samla in systeminformation
sudo bash -c "uname -a > logs/system_info.txt"
sudo bash -c "systemctl status rpctid.service > logs/rpctid_status.txt 2>&1"
sudo bash -c "ps aux | grep -i flask > logs/flask_processes.txt"
sudo bash -c "netstat -tulpn | grep -i python > logs/flask_ports.txt"

### 6. Samla in Python-miljöinformation
sudo bash -c "which python3 > logs/python_path.txt"
sudo bash -c "python3 --version > logs/python_version.txt"
sudo bash -c "pip3 freeze > logs/pip_packages.txt"
sudo bash -c "env | grep -i python > logs/python_env.txt"

### 7. Samla in Docker-information (om tillämpligt)
sudo bash -c "docker ps > logs/docker_ps.txt"
sudo bash -c "docker images > logs/docker_images.txt"

### 8. Fixa behörigheter och pusha till GitHub
# Ändra ägare så du kan uppdatera repot
sudo chown -R admindeb:admindeb .

# Lägg till ändringarna i git
git add .
git commit -m "Lägg till systemkonfiguration och loggfiler för felsökning"
git push origin main

## Förklaring av filernas syfte

- nginx/tid.endre.se: Site-specifik Nginx-konfiguration som definierar hur webbservern hanterar din Flask-applikation
- nginx/nginx.conf: Huvudkonfigurationen för Nginx-servern
- logs/nginx_error.log: Felmeddelanden från Nginx
- logs/nginx_access.log: Förfrågningar till Nginx
- logs/flask-error.log: Felmeddelanden från Flask-applikationen
- logs/system_info.txt: Grundläggande systemdata
- logs/rpctid_status.txt: Status för Flask-applikationens systemtjänst
- logs/docker_ps.txt: Aktiva Docker-containrar
- logs/docker_images.txt: Installerade Docker-images

## Vanliga problem och lösningar

### Problem 1: Flask-applikationen startar inte
Kontrollera:
- logs/rpctid_status.txt för systemtjänstens status
- logs/flask-error.log för specifika Python-fel
- logs/pip_packages.txt för att verifiera att alla beroenden är installerade

### Problem 2: Nginx visar 502 Bad Gateway
Kontrollera:
- Att Flask-applikationen körs (logs/flask_processes.txt)
- Att socket/port-konfigurationen stämmer överens mellan Nginx och Flask
- logs/nginx_error.log för detaljer

### Problem 3: Statiska filer laddas inte
Kontrollera:
- Att sökvägar i Nginx-konfigurationen är korrekta
- Att filbehörigheter är rätt inställda
- Att statiska kataloger existerar och innehåller filerna

## Återställning av systemet

Om felsökning resulterar i ändringar som måste återställas:

# För att återställa Nginx-konfigurationerna:
sudo cp nginx/tid.endre.se /etc/nginx/sites-available/
sudo cp nginx/nginx.conf /etc/nginx/
sudo systemctl restart nginx

# För att återställa applikationen:
# (Specifika steg beror på implementationen)
sudo systemctl restart rpctid.service  # Om det är en systemd-tjänst
# ELLER
cd /var/www/rpctid && docker-compose up -d  # Om Docker används

---

Senast uppdaterad: 2025-04-27







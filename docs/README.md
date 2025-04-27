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
sudo cp /sökväg/till/din/flask/flask-error.log /var/www/rpctid/logs/

2. Publicera filerna till GitHub-repot.
 "initiera ett Git-repo:" Jag har redan ett repo som nedan:
 # cd /var/www/rpctid
 # sudo git init
 # sudo git remote add origin https://github.com/TG-proton/rpctid.git
 
sudo git add .
sudo git commit -m "Initial struktur och dokumentation för CORS-felsökning"
sudo git branch -M main
sudo git push -u origin main


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

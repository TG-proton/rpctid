# Dokumentation för rpctid-projektet

## Syfte
Nedanstående mappstruktur är skapad för att samla in konfig- och loggfiler från servern för att kunna delge dessa till Copilot
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
Dessa två DOCKER Container används på servern https://tid.endre.se
docker ps:
CONTAINER ID   IMAGE        COMMAND                  CREATED        STATUS        PORTS                                         NAMES
2aa35849915c   rpctid-web   "flask run --host=0.…"   18 hours ago   Up 4 hours    0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   rpctid-web-1
08233cee3025   mysql:8.0    "docker-entrypoint.s…"   18 hours ago   Up 18 hours   3306/tcp, 33060/tcp                           rpctid-db-1

#### Lösning
VIKTIGT! Behåll detta kommando: För att skapa ny loggfil:
sudo docker logs rpctid-web-1 > /var/www/rpctid/logs/flask-error.log 2>&1

2. På servern: Publicera filerna till GitHub-repot enligt nedan:

cd /var/www/rpctid
sudo git add .
sudo git commit -m "Initial struktur och dokumentation för CORS-felsökning"
sudo git branch -M main
sudo git push -u origin main
eller
sudo git push -u origin main --force
sudo git pull origin main --rebase


3. Exempeltext för felsökningsuppdrag skrivs här
4. Implementera lösningar och dokumentera resultat.

## Testresultat
Här nedan dokumenterar vi resultaten av varje test vi kör

### Test 1: <Syfte>
**Kommando:**

**Resultat:**

### Test 2: 

#### Resultat:

#### Åtgärder

#### Status

### Lösning: 

#### Problembeskrivning

#### Vald lösning


#### Genomförande

#### Förväntat resultat

#### Dokumentation

### TEST

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


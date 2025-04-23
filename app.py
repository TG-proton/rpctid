from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_dropzone import Dropzone
import os
import exifread
import mysql.connector

app = Flask(__name__)

# Konfiguration för uppladdningar
app.config['UPLOADED_PHOTOS_DEST'] = '/var/www/rpctid/uploads'
 # Mapp för att spara uppladdade foton
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_MAX_FILE_SIZE'] = 25600  # Max filstorlek i KB (25 MB)
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_UPLOAD_URL'] = '/upload'

dropzone = Dropzone(app)

# MySQL-konfiguration
import os

db_config = {
    'user': 'root',
    'password': os.getenv('MYSQL_PASSWORD'),  # Hämta lösenord från miljövariabel
    'host': 'db',
    'database': 'photo_uploads'
}

@app.route('/')
def index():
    print("Index page called")  # Lägg till logg här
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, latitude, longitude, date_taken, notes FROM photos")  # Lägg till anteckningar
    photos = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"Hämtade foton från databasen: {photos}")  # Debug-uttalande
    return render_template('index.html', photos=photos)

@app.route('/upload', methods=['POST'])
def upload_photos():
    uploaded_files = request.files.getlist('file')  # Hämta alla uppladdade filer
    positions = []
    dates = []

    if not uploaded_files:
        return jsonify({'error': 'Ingen fil uppladdad'}), 400

    for file in uploaded_files:
        if file.filename == '':
            return jsonify({'error': 'Ingen fil vald'}), 400

        # Spara filen i den angivna mappen
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file.filename)

        try:
            file.save(filepath)  # Spara filen direkt
            print(f"Sparad fil: {filepath}")  # Debug-uttalande
        except Exception as e:
            return jsonify({'error': 'Fel vid sparande av fil'}), 500

        # Läs EXIF-data för GPS-positioner
        try:
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f)
                print(f"EXIF-data för {file.filename}: {tags}")  # Debug-uttalande
                if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                    # Konvertera GPS-koordinater från DMS till decimal
                    lat_values = tags['GPS GPSLatitude'].values
                    lon_values = tags['GPS GPSLongitude'].values

                    lat = lat_values[0].num / lat_values[0].den + \
                          (lat_values[1].num / lat_values[1].den) / 60 + \
                          (lat_values[2].num / lat_values[2].den) / 3600

                    lon = lon_values[0].num / lon_values[0].den + \
                          (lon_values[1].num / lon_values[1].den) / 60 + \
                          (lon_values[2].num / lon_values[2].den) / 3600

                    # Kolla om latitud eller longitud är negativa (S eller W)
                    if 'GPS GPSLatitudeRef' in tags and tags['GPS GPSLatitudeRef'].values != 'N':
                        lat = -lat
                    if 'GPS GPSLongitudeRef' in tags and tags['GPS GPSLongitudeRef'].values != 'E':
                        lon = -lon

                    positions.append({'lat': lat, 'lon': lon})
                    print(f"GPS-positioner: {lat}, {lon}")  # Debug-uttalande

                    # Hämta datumet för när bilden togs
                    if 'EXIF DateTimeOriginal' in tags:
                        date_taken = str(tags['EXIF DateTimeOriginal'])
                        dates.append(date_taken)
                        print(f"Datum: {date_taken}")  # Debug-uttalande
                    else:
                        dates.append('Okänt datum')

                    # Spara i databasen
                    conn = mysql.connector.connect(**db_config)
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO photos (filename, latitude, longitude, date_taken, notes) VALUES (%s, %s, %s, %s, %s)",
                        (file.filename, lat, lon, date_taken, '')  # Tomma anteckningar vid uppladdning
                    )
                    conn.commit()
                    print(f"Sparad i databasen: {file.filename}, {lat}, {lon}, {date_taken}")  # Debug-uttalande
                    cursor.close()
                    conn.close()
                else:
                    return jsonify({'error': 'Inga GPS-data hittades i filen'}), 400
        except Exception as e:
            return jsonify({'error': 'Fel vid läsning av EXIF-data: ' + str(e)}), 500

    return jsonify({'success': True}), 200  # Returnera en framgångsrespons

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    # Ta bort filen från servern
    filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Raderad fil: {filepath}")  # Debug-uttalande

    # Ta bort posten från databasen
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM photos WHERE filename = %s", (filename,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Foto raderat'}), 200

@app.route('/update_notes/<filename>', methods=['POST'])
def update_notes(filename):
    notes = request.form.get('notes')  # Hämta anteckningar från formuläret

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE photos SET notes = %s WHERE filename = %s", (notes, filename))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Anteckningar uppdaterade'}), 200

if __name__ == '__main__':
    # Skapa mappen för uppladdningar om den inte finns
    if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
        os.makedirs(app.config['UPLOADED_PHOTOS_DEST'])
    
    app.run(host='0.0.0.0', port=5000, debug=True)  # Starta Flask-applikationen i debug-läge
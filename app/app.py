from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS  # Importera CORS
import os
import exifread
import mysql.connector

app = Flask(__name__)

# Lägg till CORS-konfiguration (anpassa om nödvändigt)
CORS(app, resources={r"/api/*": {"origins": "https://rpctid.endre.se"}})

# Konfiguration för uppladdningar
app.config['UPLOADED_PHOTOS_DEST'] = '/var/www/rpctid/uploads'  # Mapp för att spara uppladdade foton
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_MAX_FILE_SIZE'] = 25600  # Max filstorlek i KB (25 MB)
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_UPLOAD_URL'] = '/upload'

# MySQL-konfiguration
db_config = {
    'user': 'root',
    'password': os.getenv('MYSQL_PASSWORD'),  # Hämta lösenord från miljövariabel
    'host': 'db',
    'database': 'photo_uploads'
}

@app.route('/')
def index():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT filename, latitude, longitude, date_taken, notes FROM photos")
        photos = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return render_template('index.html', photos=photos)

@app.route('/upload', methods=['POST'])
def upload_photos():
    uploaded_files = request.files.getlist('file')
    if not uploaded_files:
        return jsonify({'error': 'Ingen fil uppladdad'}), 400

    for file in uploaded_files:
        if file.filename == '':
            return jsonify({'error': 'Ingen fil vald'}), 400

        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file.filename)
        file.save(filepath)

        # Defaultvärden för GPS och datum
        latitude, longitude = 0.0, 0.0
        date_taken = 'Okänt datum'

        try:
            # Försök läsa EXIF-data
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f)

                # Hämta GPS-data om det finns
                if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                    lat_values = tags['GPS GPSLatitude'].values
                    lon_values = tags['GPS GPSLongitude'].values
                    latitude = lat_values[0].num / lat_values[0].den + \
                               (lat_values[1].num / lat_values[1].den) / 60 + \
                               (lat_values[2].num / lat_values[2].den) / 3600
                    longitude = lon_values[0].num / lon_values[0].den + \
                                (lon_values[1].num / lon_values[1].den) / 60 + \
                                (lon_values[2].num / lon_values[2].den) / 3600

                    # Kontrollera referenser för negativa koordinater
                    if tags.get('GPS GPSLatitudeRef', 'N').values != 'N':
                        latitude = -latitude
                    if tags.get('GPS GPSLongitudeRef', 'E').values != 'E':
                        longitude = -longitude

                # Hämta datum om det finns
                if 'EXIF DateTimeOriginal' in tags:
                    date_taken = str(tags['EXIF DateTimeOriginal'])

        except Exception as e:
            print(f"Fel vid läsning av EXIF-data: {e}")  # Logga felet men fortsätt

        # Spara information i databasen
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO photos (filename, latitude, longitude, date_taken, notes) VALUES (%s, %s, %s, %s, %s)",
                (file.filename, latitude, longitude, date_taken, '')  # Tomma anteckningar vid uppladdning
            )
            conn.commit()
        except mysql.connector.Error as e:
            return jsonify({'error': f'Fel vid insättning i databasen: {e}'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'success': True}), 200

@app.route('/api/photos', methods=['GET'])
def get_photos():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT filename, latitude, longitude, date_taken, notes FROM photos")
        photos = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(photos)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM photos WHERE filename = %s", (filename,))
        conn.commit()
    except mysql.connector.Error as e:
        return jsonify({'error': f'Fel vid radering i databasen: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Foto raderat'}), 200

@app.route('/update_notes/<filename>', methods=['POST'])
def update_notes(filename):
    notes = request.form.get('notes')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE photos SET notes = %s WHERE filename = %s", (notes, filename))
        conn.commit()
    except mysql.connector.Error as e:
        return jsonify({'error': f'Fel vid uppdatering av anteckningar: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Anteckningar uppdaterade'}), 200

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Test API fungerar!"})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
        os.makedirs(app.config['UPLOADED_PHOTOS_DEST'])

    app.run(host='0.0.0.0', port=5000)
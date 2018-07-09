from flask import Flask
from flask import jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

connection = pymysql.connect("194.116.76.192", "bd7", "bd7", "final_project")
cursor = connection.cursor(pymysql.cursors.DictCursor)


@app.route('/')
def main():
    query = '''
    SELECT device_id, DATE_FORMAT(`timestamp`, '%Y-%m-%d %H:%i:00') AS event_date, latitude, longitude
    FROM prova
    WHERE
    latitude >= 45.066 AND
    longitude >= 7.462 AND
    latitude <= 45.068 AND
    longitude <= 7.482 AND
    DAY(`timestamp`) = 1
    ORDER BY device_id, DATE_FORMAT(`timestamp`, '%Y-%m-%d %H:%i:00')
    '''
    cursor.execute(query)
    rv = cursor.fetchall()

    query_distinct = '''
    SELECT device_id
    FROM prova
    WHERE
    latitude >= 45.066 AND
    longitude >= 7.462 AND
    latitude <= 45.068 AND
    longitude <= 7.482 AND
    DAY(`timestamp`) = 1
    GROUP BY device_id
    ORDER BY device_id
    '''
    cursor.execute(query_distinct)
    dist = cursor.fetchall()

    print(dist)


    results = []
    for car in dist:
        dati_riga = {
            'car_id': int(car['device_id']),
            'color': [253, 128, 93],
            'segments': []
            }
        indice = 1
        for row in rv:
            if row['device_id'] == car['device_id']:
                punti = [row['longitude'], row['latitude'], indice]
                indice += 1
                dati_riga['segments'].append(punti)


        results.append(dati_riga)
        indice = 1


    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

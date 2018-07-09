from flask import Flask
from flask import jsonify
from flask_cors import CORS
import pymysql
from random import randint

app = Flask(__name__)
CORS(app)

connection = pymysql.connect("194.116.76.192", "bd7", "bd7", "final_project")
cursor = connection.cursor(pymysql.cursors.DictCursor)


@app.route('/')
def main():
    query = '''
    SELECT device_id, event_date, latitude, longitude, TIME_TO_SEC(event_date)/60 AS tts
    FROM ridotto
    WHERE
    event_date >= '2017-06-15 15:44:00' AND
    event_date <= '2017-06-15 15:54:00'
    /*
    latitude >= 45.08 AND
    latitude <= 45.9 AND
    longitude >= 7.60 AND
    longitude <= 7.65
    */

    ORDER BY device_id, event_date
    '''
    cursor.execute(query)
    rv = cursor.fetchall()

    query_distinct = '''
    SELECT device_id, MIN(TIME_TO_SEC(event_date)/60) AS min_tts
    FROM ridotto
    WHERE
    event_date >= '2017-06-15 15:44:00' AND
    event_date <= '2017-06-15 15:54:00'
    /*
    latitude >= 45.08 AND
    latitude <= 45.9 AND
    longitude >= 7.60 AND
    longitude <= 7.65
    */
    GROUP BY device_id
    ORDER BY device_id
    '''
    cursor.execute(query_distinct)
    dist = cursor.fetchall()


    results = []
    for car in dist:
        dati_riga = {
            'car_id': int(car['device_id']),
            'color': [253, 128, 93],
            'segments': []
            }
        for row in rv:
            if row['device_id'] == car['device_id']:
                punti = [row['longitude'], row['latitude'], int(row['tts'])- int(car['min_tts'])]
                dati_riga['segments'].append(punti)

        results.append(dati_riga)



    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

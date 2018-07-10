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
    datetime_start = '2017-06-15 15:44:00'
    datetime_end = '2017-06-15 15:54:00'


    query = '''

	SELECT CONCAT('m-', CAST(device_id AS CHAR)) AS device_id, event_date, latitude, longitude, TIME_TO_SEC(event_date)/60 AS tts
    FROM ridotto
    WHERE
    event_date >= '{0}' AND
    event_date <= '{1}'

    ORDER BY device_id, event_date
    '''.format(datetime_start, datetime_end)
    
    cursor.execute(query)
    rv = cursor.fetchall()

    dist = set()
    min_tts = 1000000000
    for row in rv:
        dist.add(row['device_id'])
        if int(row['tts']) < min_tts:
            min_tts = int(row['tts'])

    results = []
    for car in dist:
        color = [159, 229, 90]
        if car[:1] == 's':
            color = [253, 128, 93]

        dati_riga = {
            'car_id': car,
            'color': color,
            'segments': []
            }
        for row in rv:
            if row['device_id'] == car:
                punti = [row['longitude'], row['latitude'], int(row['tts']) - min_tts]
                dati_riga['segments'].append(punti)

        results.append(dati_riga)



    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

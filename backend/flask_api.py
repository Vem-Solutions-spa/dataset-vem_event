from flask import Flask
from flask import jsonify
from flask_cors import CORS
import pymysql
from random import randint
from flask import request
import numpy as np
import pandas as pd
import random
from flask import send_file
import os
import json


app = Flask(__name__)
CORS(app)

# Setup Connessione al database
connection = pymysql.connect("194.116.76.192", "bd7", "bd7", "final_project")
cursor = connection.cursor(pymysql.cursors.DictCursor)

# Per DEMO: Servo il JSON già preparato
@app.route('/trips')
def trips():
    with open(os.path.join(os.path.dirname(app.instance_path), 'concerto.json')) as f:
        data = json.load(f)
    print('Invio JSON')
    return jsonify(data)


@app.route('/')
def main():

    date = '2017-06-15'
    min_time = '15:44'
    max_time = '15:54'
    min_lat = float(44.9941845)
    max_lat = float(45.1202965)
    min_long = float(7.5991039)
    max_long = float(7.7697372)

    if request.args.get("date"):
        date = request.args.get("date")
    if request.args.get("min_time"):
        min_time = request.args.get("min_time")
    if request.args.get("max_time"):
        max_time = request.args.get("max_time")
    if request.args.get("min_lat"):
        min_lat = float(request.args.get("min_lat"))
    if request.args.get("min_long"):
        min_long = float(request.args.get("min_long"))
    if request.args.get("max_lat"):
        max_lat = float(request.args.get("max_lat"))
    if request.args.get("max_long"):
        max_long = float(request.args.get("max_long"))

    print('''
    event_date >= '{0} {1}' AND
    event_date <= '{0} {2}' AND
    latitude >= {3} AND latitude <= {4} AND
    longitude >= {5} AND longitude <= {6}
    '''.format(date, min_time, max_time, min_lat, max_lat, min_long, max_long)
    )

    query = 'SELECT * FROM trips_parks_sera_concerto ORDER BY device_id,  event_date'

    query2 = '''
    SELECT * 
    FROM (
        
        SELECT device_id, event_date, latitude, longitude, TIME_TO_SEC(event_date)/60 AS tts, 'moving' AS status
        FROM ridotto_full_month
        WHERE
        event_date >= '{0} {1}' AND
        event_date <= '{0} {2}' AND
        latitude >= {3} AND latitude <= {4} AND
        longitude >= {5} AND longitude <= {6}
        
        /*
        UNION

        SELECT car_id AS device_id, event_date, latitude, longitude, tts, 'parked' AS status
        FROM parking_each_min
        WHERE
        event_date >= '{0} {1}' AND
        event_date <= '{0} {2}' AND
        latitude >= {3} AND latitude <= {4} AND
        longitude >= {5} AND longitude <= {6}
        */
    ) A
    ORDER BY device_id,  event_date
    '''.format(date, min_time, max_time, min_lat, max_lat, min_long, max_long)

    print('eseguo query')

    cursor.execute(query)
    rv = cursor.fetchall()

    print('query eseguita')

    # Calcolo set auto univoche e timestamp di inizio
    dist = set()
    min_tts = 1000000000
    for row in rv:
        dist.add(row['device_id'])
        if int(row['tts']) < min_tts:
            min_tts = int(row['tts'])

    print('set creato')

    # Creo il JSON nel formato richiesto da deck.gl
    results = []
    for car in dist:
        
        print('Elaboro auto ' + str(len(results)) + ' su ' + str(len(dist)))

        color = [159, 229, 90]

        dati_riga = {
            'car_id': car,
            'color': color,
            'segments': []
            }
        for row in rv:
            if row['device_id'] == car:

                lat = row['latitude']
                long = row['longitude']

                if row['status'] == 'parked':
                    lat = lat + random.uniform(-0.0001, 0.0001)
                    long = long + random.uniform(-0.0001, 0.0001)

                punti = [long, lat, int(row['tts']) - min_tts, row['status']]
                dati_riga['segments'].append(punti)

        results.append(dati_riga)

    print('lista creata')



    return jsonify(results)

@app.route('/heatmap')
def heatmap():
    # Per DEMO: Servo il JSON già preparato
    if request.args.get("snap"):
        if request.args.get("snap") == '1':
            with open(os.path.join(os.path.dirname(app.instance_path), '14-20.json')) as f:
                data = json.load(f)
            return jsonify(data)

        elif request.args.get("snap") == '2':
            with open(os.path.join(os.path.dirname(app.instance_path), '21-20.json')) as f:
                data = json.load(f)
            return jsonify(data)
            
        elif request.args.get("snap") == '3':
            with open(os.path.join(os.path.dirname(app.instance_path), '22-20.json')) as f:
                data = json.load(f)
            return jsonify(data)


    # Lettura parametri richiesta GET
    date = '2017-06-21'
    time = '20:00'
    min_lat = float(44.9941845)
    min_long = float(7.5991039)
    max_lat = float(45.1202965)
    max_long = float(7.7697372)

    if request.args.get("date"):
        date = request.args.get("date")
    if request.args.get("time"):
        time = request.args.get("time")
    if request.args.get("min_lat"):
        min_lat = float(request.args.get("min_lat"))
    if request.args.get("min_long"):
        min_long = float(request.args.get("min_long"))
    if request.args.get("max_lat"):
        max_lat = float(request.args.get("max_lat"))
    if request.args.get("max_long"):
        max_long = float(request.args.get("max_long"))

    # esempio: http://127.0.0.1:5000/heatmap?date=2017-06-22&time=20:00&min_lat=44.9941845&max_lat=45.1202965&min_long=7.5991039&max_long=7.7697372

    rv = detect_parks_grid('trips3',date + ' ' + time,[min_lat,max_lat],[min_long,max_long],10,20,num_cell_v=50,num_cell_h=50)

    lat_long = []
    for row in rv:
        lat_long.append([row[0], row[1]])

    return jsonify(lat_long)


# Funzione per calcolo densità parcheggi in una griglia
def detect_parks_grid(database_filename,date_hour,latitude_range,longitude_range,car_threshold,min_threshold,num_cell_v=100,num_cell_h=100):

    query_string = """SELECT car_id, X(start_pos) AS start_lon, Y(start_pos) AS start_lat, start_time, end_time,
    nr_min FROM %s WHERE  start_time < "%s" and end_time > "%s" """ % (database_filename,date_hour,date_hour)

    connection = pymysql.connect('194.116.76.192', 'bd7', 'bd7', 'final_project')

    df=pd.read_sql(query_string, connection)

    good_records = df.loc[(df['start_lat'] > latitude_range[0]) & (df['start_lat'] < latitude_range[1]) &
                      (df['start_lon'] > longitude_range[0]) & (df['start_lon'] < longitude_range[1]) &
                      (df['nr_min'] > min_threshold)]


    #good_records[['start_lon','start_lat']].to_csv(file_out,header=None,index=False)

    good_records_formatted = good_records[['start_lon','start_lat','nr_min']]

    grid_ticks_h = []
    grid_ticks_v = []

    delta_v = (latitude_range[1] - latitude_range[0])/float(num_cell_v)
    delta_h = (longitude_range[1] - longitude_range[0])/float(num_cell_h)

    grid_ticks_v.append(latitude_range[0])
    grid_ticks_h.append(longitude_range[0])

    parkings = np.zeros((num_cell_h, num_cell_v))

    diction = {}

    for i1 in range(0,num_cell_h):
        grid_ticks_h.append(grid_ticks_h[i1]+delta_h)
        diction[i1] = {}
        for i2 in range(0,num_cell_v):
            diction[i1][i2] = []

    for i1 in range(0,num_cell_v):
        grid_ticks_v.append(grid_ticks_v[i1]+delta_v)


    for i1 in range(0,good_records_formatted.shape[0]):
        h_coord = good_records_formatted.iloc[i1,0]
        v_coord = good_records_formatted.iloc[i1,1]

        for it in grid_ticks_h:
            if h_coord<it:
                h_add = grid_ticks_h.index(it)-1
                break

        for it in grid_ticks_v:
            if v_coord<it:
                v_add = grid_ticks_v.index(it)-1
                break

        parkings[h_add,v_add] += 1
        diction[h_add][v_add].append([h_coord,v_coord,good_records_formatted.iloc[i1,2]])

    big_list = []

    for i1 in range(0,num_cell_h):
        for i2 in range(0,num_cell_v):
            if parkings[i1,i2]>car_threshold:
                for tt in diction[i1][i2]:
                    big_list.append(tt)

    return big_list





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

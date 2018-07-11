import numpy as np
import pandas as pd
import pymysql
import csv


def detect_parks_grid(database_filename,file_out,date_hour,latitude_range,longitude_range,car_threshold,min_threshold,num_cell_v=100,num_cell_h=100): 
    
    query_string = """SELECT car_id, X(start_pos) AS start_lon, Y(start_pos) AS start_lat, start_time, end_time, 
    nr_min FROM %s WHERE  start_time < "%s" and end_time > "%s" """ % (database_filename,date_hour,date_hour)
    
    connection = pymysql.connect('194.116.76.192', 'bd7', 'bd7', 'final_project')
    
    df=pd.read_sql(query_string, connection)
    
    # si potrebbe fare nel sql
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
                
    with open(file_out, "wb") as f:
    writer = csv.writer(f)
    writer.writerows(big_list)
    
    
detect_parks_grid('trips3','June_22_grid_50_50_h20','2017-06-22 20:00',[44.9941845,45.1202965],[7.5991039,7.7697372],10,20,num_cell_v=50,num_cell_h=50) 
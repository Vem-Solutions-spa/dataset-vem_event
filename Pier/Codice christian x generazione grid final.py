def detect_parks_grid_in_time_correct(database_filename,overall_list,date_hour_list,latitude_range,longitude_range,min_threshold,num_cell_v=20,num_cell_h=20): 
    
    grid_ticks_v = []
    grid_ticks_h = []
    
    grid_ticks_v.append(latitude_range[0])
    grid_ticks_h.append(longitude_range[0])
    
    delta_v = (latitude_range[1] - latitude_range[0])/float(num_cell_v)
    delta_h = (longitude_range[1] - longitude_range[0])/float(num_cell_h)
    
    for i1 in range(0,num_cell_h):
        grid_ticks_h.append(grid_ticks_h[i1]+delta_h)
    
    for i1 in range(0,num_cell_v):
        grid_ticks_v.append(grid_ticks_v[i1]+delta_v)
        
    
    for date_hour in date_hour_list:
    
        in_hour = date_hour[0]
        fin_hour = date_hour[1]
    
        query_string = """SELECT car_id, X(start_pos) AS start_lon, Y(start_pos) AS start_lat, start_time, end_time, 
        nr_min FROM %s WHERE (start_time < "%s" and end_time > "%s") or (start_time < "%s" and end_time > "%s") or (start_time > "%s" and end_time < "%s") """ % (database_filename,in_hour,in_hour,fin_hour,fin_hour,in_hour,fin_hour)
    
        connection = pymysql.connect('194.116.76.192', 'bd7', 'bd7', 'final_project')
    
        df=pd.read_sql(query_string, connection)
        
        good_records = df.loc[(df['start_lat'] > latitude_range[0]) & (df['start_lat'] < latitude_range[1]) & 
                              (df['start_lon'] > longitude_range[0]) & (df['start_lon'] < longitude_range[1]) & 
                              (df['nr_min'] > min_threshold)]
        
        good_records['start_time'] = pd.to_datetime(good_records['start_time'])
        good_records['end_time'] = pd.to_datetime(good_records['end_time'])
        
        good_records['long_bin'] = pd.to_numeric(pd.cut(good_records['start_lon'], grid_ticks_h).apply(lambda x: (x.left+x.right)/2.0))
        good_records['lat_bin'] = pd.to_numeric(pd.cut(good_records['start_lat'], grid_ticks_v).apply(lambda x: (x.left+x.right)/2.0))
        
        time_list = []
        time_list.append(datetime.strptime(in_hour, "%Y-%m-%d %H:%M"))
        
        
        for i1 in range(1,25):
            time_list.append(time_list[0] + timedelta(hours=i1))
        
        for i1 in range(0,24):
            
            records_per_hour = good_records.loc[((good_records['start_time'] < time_list[i1]) & (good_records['end_time'] > time_list[i1]))
                                               | ((good_records['start_time'] < time_list[i1+1]) & (good_records['end_time'] > time_list[i1+1]))
                                               | ((good_records['start_time'] > time_list[i1]) & (good_records['end_time'] < time_list[i1+1]))]
        
            good_records_formatted = records_per_hour[['long_bin','lat_bin']]
        
            grouped_good_records = good_records_formatted.groupby(['long_bin','lat_bin'])
        
            for key, item in grouped_good_records:
                overall_list.append([key[0],key[1],grouped_good_records.get_group(key).shape[0],time_list[i1].strftime('%Y-%m-%d %H:%M'),int(time_list[i1].strftime('%d')),time_list[i1].weekday(),time_list[i1].hour])
                
        
    return overall_list
#!/usr/bin/env python3


import solaredge
import influx
import toml
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests import HTTPError
import time


parser = argparse.ArgumentParser()
parser.add_argument('-f', metavar='config file', required=True, type=str)


def send(solaredge_api, influxdb):
    end_time = datetime.now().replace(hour=23, minute=59, second=59)

    last_update = influxdb.get_last_update()
    start_time = None
    if(last_update is None) :
        print('DB empty, queuring one month.')
        start_time = end_time - relativedelta(months = 1)
    else :
        start_time = last_update

    data = solaredge_api.get_combined(start_time, end_time)

    result = {}

    for date in data :
        if date >= start_time.replace(tzinfo=None):
            result[date] = data[date]

    if len(result) > 0 :
        influxdb.write(result)
        
    print('Wrote', len(result), 'entries, Start time', start_time, ', End time', end_time)

def main():

    args = parser.parse_args()
    config = toml.load(args.f)

    solaredge_config = config['solaredge']
    site_id = solaredge_config['site_id']
    api_key = solaredge_config['api_key']

    sleep_time = config['deamon']['sleep']

    influx_config = config['influxdb']

    influxdb = influx.InfluxDb(
        influx_config['host'], 
        influx_config['port'], 
        influx_config['user'], 
        influx_config['password'], 
        influx_config['dbname'], 
        influx_config['measurement'],
        {'id': str(site_id)})

    
    solaredge_api = solaredge.Api(api_key, site_id)

    while True:
        try :
            send(solaredge_api, influxdb)
        except HTTPError as ex:
            print('API request failed:', ex)

        time.sleep(sleep_time * 60)


if __name__ == "__main__":
    main()

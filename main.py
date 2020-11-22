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
    end_time = datetime.now()

    last_update = influxdb.get_last_update()
    if(last_update is None) :
        print('DB empty, queuring one month.')
        start_time = end_time - relativedelta(months = 1)
    else :
        start_time = last_update

    powerdata = solaredge_api.get_power(start_time, end_time)
    influxdb.write_power(powerdata)

    print('Wrote', len(powerdata), 'entries, Start time', start_time, ', End time', datetime.now())

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
        {id: str(site_id)})

    
    solaredge_api = solaredge.Api(api_key, site_id)


    while True:
        try :
            send(solaredge_api, influxdb)
        except HTTPError as ex:
            print('API request failed:', ex)

        time.sleep(sleep_time * 60)


if __name__ == "__main__":
    main()
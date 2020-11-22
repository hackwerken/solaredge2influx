#!/usr/bin/env python3

import requests
import  dateutil.parser
from datetime import datetime

class Api:

    def __init__(self, api_key, site_id) :
        self.api_key = api_key
        self.site_id = site_id

    def get_power(self, start_time, end_time) :

        dateformat = '%Y-%m-%d %H:%M:%S'

        params = {'api_key': self.api_key,
            'startTime': start_time.strftime(dateformat),
            'endTime': end_time.strftime(dateformat)
        }

        r = requests.get('https://monitoringapi.solaredge.com/sites/{}/power'.format(self.site_id), params=params)
        r.raise_for_status()
        
        values =  r.json()['powerDateValuesList']['siteEnergyList'][0]['powerDataValueSeries']['values']


        result = []

        for value in values :
            if value['value'] != None:
                date = dateutil.parser.isoparse(value['date'])
                result.append({'date': date, 'value': value['value']})

        return result

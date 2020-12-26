#!/usr/bin/env python3

import requests
import dateutil.parser
import dateutil.tz
from datetime import datetime

datetime_format = '%Y-%m-%d %H:%M:%S'
date_format = '%Y-%m-%d'

class Api:

    def __init__(self, api_key, site_id) :
        self.api_key = api_key
        self.site_id = site_id

    def _get(self, name, params) :

        params.update({'api_key': self.api_key})

        r = requests.get('https://monitoringapi.solaredge.com/sites/{}/{}'.format(self.site_id, name), params=params)
        r.raise_for_status()
        return r

    def _parse_date(self, input) :
        date = dateutil.parser.isoparse(input)
        return date.replace(tzinfo = dateutil.tz.tzlocal())

    def _format_datetime(self, dt, format) :
        return dt.astimezone(dateutil.tz.tzlocal()).strftime(format)

    def get_power(self, start_time, end_time) :
        params = {
            'startTime': self._format_datetime(start_time, datetime_format),
            'endTime': self._format_datetime(end_time, datetime_format)
        }

        r = self._get('power', params)
        values =  r.json()['powerDateValuesList']['siteEnergyList'][0]['powerDataValueSeries']['values']


        result = {}

        for value in values :
            if value['value'] != None:
                date = self._parse_date(value['date'])
                result[date] = value['value']

        return result

    def get_energy(self, start_time, end_time) :
        params = {
            'startDate': self._format_datetime(start_time, date_format),
            'endDate': self._format_datetime(end_time, date_format),
            'timeUnit': 'QUARTER_OF_AN_HOUR'
        }

        r = self._get('energy', params)

        values = r.json()['sitesEnergy']['siteEnergyList'][0]['energyValues']['values']


        result = {}

        for value in values :
            if value['value'] != None:
                date = self._parse_date(value['date'])
                result[date] = value['value']

        return result

    def _merge(self, source, destination, name) :
        
        for key in source :
            value = source[key]

            if key in destination :
                destination[key][name] = value
            else :
                destination[key] = {name : value}

    def get_combined(self, start_time, end_time) :
        power = self.get_power(start_time, end_time)
        energy = self.get_energy(start_time, end_time)
       

        combined = {}
        self._merge(energy, combined, 'energy')
        self._merge(power, combined, 'power')

        return combined



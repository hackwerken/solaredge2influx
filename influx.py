
#!/usr/bin/env python3

import  dateutil.parser
from influxdb import InfluxDBClient

class InfluxDb:

    def __init__(self, host, port, user, password, dbname, measurement, tags) :
        self.measurement = measurement
        self.tags = tags
        self._influxdb = InfluxDBClient(host, port, user, password, dbname)

    def get_last_update(self) :
        select = self._influxdb.query('SELECT LAST(power) FROM "pv"')
        if len(select) < 1 :
            return None

        last_update = select.raw['series'][0]['values'][0][0]
        return dateutil.parser.isoparse(last_update)
       
    def write_power(self, points) :
        out = []

        for power in points :
            point = {
                "measurement": self.measurement,
                "tags": self.tags,
                "time": power['date'],
                "fields": {
                    "power": float(power['value'])
                }
            }
            out.append(point)

        self._influxdb.write_points(out)
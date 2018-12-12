# -*- coding: utf-8 -*-
# (c) 2018 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging
from influxdb import InfluxDBClient

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

log = logging.getLogger(__name__)


class InfluxDBStorage:

    capabilities = ['readings']

    def __init__(self, dsn, measurement='ldi_readings', empty_tables=False, dry_run=False):

        self.dry_run = dry_run
        self.measurement = measurement

        dsn_parts = urlparse(dsn)
        if dsn_parts.scheme.startswith('udp+'):
            self.db = InfluxDBClient.from_dsn(dsn, udp_port=dsn_parts.port, timeout=5)
        else:
            self.db = InfluxDBClient.from_dsn(dsn, timeout=5)
            self.db.create_database(self.db._database)


    def emit(self, reading):
        """
        Will store these kind of records to InfluxDB:
        {
            "measurement": "ldi_readings",
            "tags": {
                "station_id": 28,
                "sensor_id": 658
            },
            "time": "2018-12-12T02:21:08Z",
            "fields": {
                "P1": 13.35,
                "P2": 8.05
            }
        }
        """

        # Copy measurement values and delete "time" field.
        data = dict(reading.data)
        del data['time']

        # Build InfluxDB record.
        record = {
            "measurement": self.measurement,
            "tags": {
                "station_id": reading.station.station_id,
                "sensor_id": reading.station.sensor_id,
            },
            "time": reading.data.time,
            "fields": data
        }

        # Store into database.
        self.db.write_points([record])

    def flush(self):
        pass

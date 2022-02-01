from shutil import copyfile
import psycopg2
import Helper
import os, errno
import csv
import glob
from numpy import *

class DBSaver():
    """Class to handle Database communication."""
    
    def __init__(self):
        self.session_id = None
        self.con = None

    def connect(self, user, password):
        """
        Establish connection and store reference to it.
        
        Return:
        bool: True (connection successful), False (connection failed)
        """

        msg = "dbname=tacdb user=%s password=%s host=localhost port=5432" % (user, password)
        try:
            self.con = psycopg2.connect(msg)
            return True
        except:
            return False

    def add_sensors(self, sensors):
        """Add specified sensor names to database if not exist."""

        cur = self.con.cursor()
        for sensor in sensors:
            s_exist = "SELECT EXISTS(SELECT 1 FROM sensor WHERE name='%s')" % sensor
            cur.execute(s_exist)
            if not cur.fetchone()[0]:
                cur.execute("INSERT INTO sensor(name) VALUES(%s)", [sensor])
        cur.close()
        self.con.commit()

    def new_session(self):
        """Add new session entry to database after latest session entry."""

        cur = self.con.cursor()
        cur.execute("SELECT 1 FROM session LIMIT 1")
        if cur.fetchone():
            cur.execute("SELECT id FROM session ORDER BY timestamp DESC LIMIT 1")
            self.session_id = cur.fetchone()[0]
            self.session_id += 1
        else:
            self.session_id = 1

        cur.execute("INSERT INTO session(timestamp) VALUES(%s)", [Helper.get_timestamp()])
        cur.close()
        self.con.commit()
            
    def get_sensor_id(self, sensor_name):
        """
        Get Sensor ID from database for specified sensor_name.
        
        Return:
        string: sensor_id    
        """

        cur = self.con.cursor()
        s_exist = "SELECT EXISTS(SELECT 1 FROM sensor WHERE name='%s')" % sensor_name
        ret = None
        cur.execute(s_exist)
        if cur.fetchone()[0]:
            cur.execute("SELECT id FROM sensor WHERE name=%s", [sensor_name])
            ret = cur.fetchone()[0]
        cur.close()
        return ret

    def save_measurement(self, session_data):
        """Save measurement to database."""

        cur = self.con.cursor()
        for sensor_data in session_data:
            # convert np array to python array
            if isinstance(sensor_data["data"], ndarray):
                sensor_data["data"] = sensor_data["data"].tolist()
            sensor_data_array = list(sensor_data.values())
            # replace sensor_name with sensor_id
            sensor_name = sensor_data_array[0]
            sensor_id = self.get_sensor_id(sensor_name)
            sensor_data_array[0] = sensor_id
            sensor_data_array.append(self.session_id)

            cur.execute("INSERT INTO measurement(sensor_id, timestamp, header, data, units, session_id) VALUES(%s,%s,%s,%s,%s,%s)", sensor_data_array)
        cur.close()
        self.con.commit()

    def save_calibration(self, calibration_data):
        """Save Calibration to database."""

        cur = self.con.cursor()
        calibration_data["data"] = calibration_data["data"].tolist()
        calib_data_array = list(calibration_data.values())
        # replace sensor_name with sensor_id
        sensor_name = calib_data_array[0]
        sensor_id = self.get_sensor_id(sensor_name)
        calib_data_array[0] = sensor_id

        cur.execute("INSERT INTO calibration(sensor_id, timestamp, header, data, units) VALUES(%s,%s,%s,%s,%s)", calib_data_array)
        cur.close()
        # save changes to DB
        self.con.commit()

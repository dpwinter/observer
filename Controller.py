from Widgets import *
import psycopg2
import time
import Saver
import Helper
from numpy import *

class Controller():
    """
    MVC-Controller class to direct communication between widget manager and sensor manager.

    The Controller is responsible for:
    1. Control Timing
    2. Initiate Measurement process
    3. Control Saving to database
    4. Forward errors to View
    5. Calibration

    """

    def __init__(self):
        """Setup control parameters for timing, saving and calibration."""

        self.model = None
        self.view = None
        self.update_timer = QTimer()
        self.interval_timer = CountTimer()
        self.update_time_ms = 100
        self.calibration_time_ms = 5000
        self.calibration_cycles = 3
        self.interval_time = QTime(0,0)
        self.saver = None
    
    def register_view(self, view):
        """
        Set reference to View.

        Setup to update View every update_time_ms miliseconds.
        Pass some control parameters relevant for updating Widgets to View.
        """

        self.view = view
        self.update_timer.timeout.connect(lambda: self.view.update(self.interval_timer.remainingTime(), self.interval_timer.cnt))

    def register_model(self, model):
        """
        Set reference to Model.
        
        Setup to initiate measurement (query Model) every interval_time.
        Note: The use of QTime object as interval for interval_timer.
        (This simplifies setting the Timer interval by QTimeEdit Widget)
        """

        self.model = model
        self.interval_timer.timeout.connect(self.measure_all)

    def register_saver(self, user, pw):
        """Set reference to Saver. Establish connection to PSQL database."""

        self.saver = Saver.DBSaver()
        if self.saver.connect(user, pw):
            self.saver.add_sensors(self.model.sensor_ids)
            self.view.set_db_con_state(1)
        else:
            self.view.message_box("Connection failed")
            self.saver = None
            self.view.set_db_con_state(0)
            return

    def start(self, time=None):
        """
        Start new measurement session.
        
        Note: Called from View by passing user set interval_time.
        """

        if time:
            self.interval_time = time
        else:
            time = self.interval_time
        if self.saver == None:
            self.view.message_box("Database not connected.")
            self.view.reset()
            return

        self.saver.new_session()

        self.interval_timer.setInterval(time.msecsSinceStartOfDay())
        self.update_timer.start(self.update_time_ms)
        self.interval_timer.start()

    def stop(self):
        """Stop timers."""

        self.update_timer.stop()
        self.interval_timer.stop()

    def pause(self):
        """Deactivate interval_timer during measurement."""

        self.update_timer.stop()
        self.interval_timer.pause()

    def restart(self):
        """Restart timers."""

        self.update_timer.start(self.update_time_ms)
        self.interval_timer.start()

    def measure_all(self):
        """
        Measure all sensors.
        
        Deactivate interval_timer during measurements.
        (By that measurement time has no effect on interval_timer time.)
        Restart timers after measurements complete.
        """

        self.pause()
        self.view.set_highlight_lbl("Measurement in progress, do not stop.")
        session_data = self.model.measure_all()
        self.saver.save_measurement(session_data)
        self.restart()

    def measure_single(self, index):
        """
        Measure single sensor. (For Calibration purpose)
        
        Return value:
        np_array[points][3] with columns [frequency, C-Value, D-Value]
        """

        self.view.set_highlight_lbl("Calibration in progress, do not stop.")
        data = self.model.measure_single(index)
        return data

    def mean(self, sensor_index):
        """
        Calculate mean values of C-Values per frequency.

        Return value:
        np_array[points][3] with columns [frequency, C-Value, D-Value]
        Note: Only the mean vales of C-Values are calculated.
        """

        mean = None
        for cycle in range(self.calibration_cycles):
            # First cycle: Set mean to measurement
            if mean is None:
                mean = self.measure_single(sensor_index)
            # Further cycles: Add C-Values of new measurement
            else:
                mean["data"].T[1] += self.measure_single(sensor_index)["data"].T[1]

        # Divide C-Values by number of cycles
        mean["data"].T[1] /= self.calibration_cycles
        return mean

    def calibrate(self, index):
        """
        Calibrate Keysight E4990A.

        1. n measurements when capacitive sensor is filled with air.
        2. Calculate mean of these measurements (air_mean).
        3. n measurements when capacitive sensor is filled with cyclohexan.
        4. Calculate mean of these measurements (cyclo_mean).
        5. Apply Calibration algorithm:
                m = (cyclo_mean C-value - air_mean C-value) / deta_lit
                k = air_mean C-value - (m * c_air_lit)
        """

        if self.saver == None:
            self.view.message_box("Database not connected")
            self.view.reset()
            return

        msg = QMessageBox()
        msg.setText("Calibrate sensor %s?" % self.model.sensor_ids[index])
        msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msg.setDefaultButton(QMessageBox.Yes)
        ret = msg.exec()
        if ret == 0x4000:   # Yes pressed
            # Get mean on air
            self.view.message_box("Connect to air.")
            air_mean = self.mean(index)
            # Get mean on cyclohexan
            self.view.message_box("Connect to cyclohexan.")
            cyclohexan_mean = self.mean(index)

            # apply formula on mean arrays
            c_air_lit = 1
            c_cyclohexan_lit_20 = 2.016
            delta_lit = c_cyclohexan_lit_20 - c_air_lit
            res = cyclohexan_mean.copy()
            for i in range(len(res["data"].T[0])):
                # data format: res["data"][row][col]
                res["data"][i][1] = (cyclohexan_mean["data"][i][1] - air_mean["data"][i][1]) / delta_lit
                res["data"][i][2] = air_mean["data"][i][1] - (res["data"][i][1] * c_air_lit)

            res["header"]  = ["Frequency", "m", "k"]
            res["units"]   = ["Hz", "", ""]
            self.saver.save_calibration(res)
        self.view.reset()

    def evaluate(self, raw_data, calibration_data):
        """Apply evaluation algorithm. Currently not used."""

        raw_data["data"].T[1] = (raw_data["data"].T[1] - calibration_data.T[2]) / calibration_data.T[1]
        raw_data["data"].T[2] = raw_data["data"].T[1] * sensor_event["data"].T[2]
        return raw_data

from Widgets import *
from Sensors import *
import sys
import os

class WidgetManager:
    """MVC-View Class: Layout and Management of Widgets on Screen."""

    def __init__(self):
        self.widgets = {}
        self.controller = None

    def register_controller(self, ctrl):
        """Set reference to Controller."""

        self.controller = ctrl

    def create_widgets(self, sensor_names, calibratables):
        """
        Create Widgets in Layout.

        Note: Change content of this function to alter GUI Layout.
        """

        layout_top = QHBoxLayout()
        db_group = QGroupBox("Database connection")
        user_lbl = QLabel("Username:")
        user = QLineEdit("postgres")
        user.setFixedHeight(50)
        pw_lbl = QLabel("Password:")
        pw = QLineEdit("postgres")
        pw.setFixedHeight(50)
        pw.setEchoMode(QLineEdit.Password)
        bbtn = Button("Connect", self)
        bbtn.setFixedHeight(50)
        icon = QLabel("Not connected.")
        layout_top.addWidget(user_lbl)
        layout_top.addWidget(user)
        layout_top.addWidget(pw_lbl)
        layout_top.addWidget(pw)
        layout_top.addWidget(bbtn)
        layout_top.addWidget(icon)
        db_group.setLayout(layout_top)

        time_edit_group = QGroupBox("Measurement interval")
        te = TimeDisplay()
        font = te.font()
        font.setPointSize(25)
        te.setFont(font)
        layout_mid_r_top = QHBoxLayout()
        layout_mid_r_top.addStretch()
        layout_mid_r_top.addWidget(te)
        layout_mid_r_top.addStretch()
        pbtn = RepeatButton("+", self)
        mbtn = RepeatButton("-", self)
        pbtn.setFont(font)
        mbtn.setFont(font)
        btns = QHBoxLayout()
        btns.addWidget(mbtn)
        btns.addWidget(pbtn)
        sbtn = ToggleButton(["Start", "Stop"], self)
        sbtn.setFixedHeight(100)
        layout_mid_r = QVBoxLayout()
        layout_mid_r.addLayout(layout_mid_r_top)
        layout_mid_r.addLayout(btns)
        layout_mid_r.addWidget(sbtn)
        time_edit_group.setLayout(layout_mid_r)

        list_group = QGroupBox("Connected sensors")
        tab = Table()
        tab.setColumnCount(2)
        tab.setRowCount(len(sensor_names))
        cbtns = []
        for i in range(len(calibratables)):
            tab.setItem(i, 0, QTableWidgetItem(sensor_names[i]))
            if calibratables[i]:
                cbtn = Button("Calibrate", self)
                tab.setCellWidget(i, 1, cbtn)
                cbtns.append(cbtn)
            
        layout_table = QHBoxLayout()
        layout_table.addWidget(tab)
        list_group.setLayout(layout_table)

        layout_mid = QHBoxLayout()
        layout_mid.addWidget(list_group)
        layout_mid.addWidget(time_edit_group)

        lbl = Label("Ready for Measurement")
        layout_bottom = QHBoxLayout()
        layout_bottom.addStretch()
        layout_bottom.addWidget(lbl)
        layout_bottom.addStretch()

        layout_all = QVBoxLayout()
        layout_all.addWidget(db_group)
        layout_all.addLayout(layout_mid)
        layout_all.addLayout(layout_bottom)
 
        widget = QWidget()
        widget.setLayout(layout_all)

        self.widgets = {
                "user" : user,      # user (line edit)
                "pw"   : pw,        # password (line edit)
                "bbtn" : bbtn,      # connect button
                "icon" : icon,      # connect status icon
                "pbtn" : pbtn,      # plus button
                "mbtn" : mbtn,      # minus button
                "sbtn" : sbtn,      # start/stop button
                "cbtns": cbtns,     # array of calibration buttons
                "te"   : te,        # time display (time edit)
                "tab"  : tab,       # table (contain sensor names and cbtns)
                "lbl"  : lbl        # label (status indicator)
                }

        self.widgets["pbtn"].pressed.connect(te.stepUp)
        self.widgets["mbtn"].pressed.connect(te.stepDown)

        return widget
    
    def button_pressed(self, button):
        """Handle button presses by ID of pressed button."""

        # "Browse" Button pressed
        if button == self.widgets["bbtn"]:
            user = self.widgets["user"].text()
            pw = self.widgets["pw"].text()
            self.controller.register_saver(user, pw)

        # "Start" / "Stop" Button pressed
        elif button == self.widgets["sbtn"]:
            if button.isChecked():
                time = self.widgets["te"].interval
                if time != QTime(0,0):
                    self.activate_widgets(False)
                    self.controller.start(time)
                else:
                    self.message_box("No measurement interval set.")
                    self.reset()
                    return
            else:
                self.controller.stop()
                self.reset()

        # "+" / "-" Button pressed
        elif button == self.widgets["pbtn"] or button == self.widgets["mbtn"]:
            return

        # "Calibrate" Button pressed
        else:
            index = self.widgets["cbtns"].index(button)
            self.activate_widgets(False)
            self.widgets["sbtn"].set()
            self.controller.calibrate(index)

    def update(self, time, cnt):
        """Update TimeEdit and Measurement Counter Label."""

        self.widgets["lbl"].set_count(cnt)
        qtime = QTime(0, 0).addMSecs(time)
        self.widgets["te"].setTime(qtime)

    def set_highlight_lbl(self, text):
        """Display highlighted text in Measurement Counter Label."""

        self.widgets["lbl"].setText("<font color='red'>" + text + "</font>")
        QApplication.processEvents()
    
    def message_box(self, txt):
        """Display simple MessageBox with content text."""

        msg = QMessageBox()
        msg.setText(txt)
        msg.exec()

    def set_db_con_state(self, state):
        """Update connection state of PSQL database."""

        if state:
            self.widgets["icon"].setText("connected.")
        else:
            self.widgets["icon"].setText("disconnected.")

    def reset(self):
        """Reset altered Widgets to initial values."""

        self.activate_widgets(True)
        self.widgets["sbtn"].reset()
        self.widgets["te"].reset()
        self.widgets["lbl"].reset()

    def activate_widgets(self, state):
        """Activate/Deactivate Widgets except Start/Stop-Button (must be always active)."""

        for widget in self.widgets.values():
            if type(widget) != list:
                if widget is not self.widgets["sbtn"]:
                    widget.setEnabled(state)

class SensorManager():
    """MVC-Model class: Handles communication to implemented sensors."""

    def __init__(self):
        self.sensors = {}

    @property
    def sensor_ids(self):
        """Return IDs of all sensor instances."""

        s_names = []
        for sensor in self.sensors.values():
            s_names.append(sensor.property["id"])
        return s_names
    
    def create_sensors(self):
        """
        Function to instantiate desired sensors.
        
        Note: Change this function to alter the sensor setup. 
        Only implemented sensor classes should be instantiated.

        Return:
        [string]: list of keys of self.sensors
        [int]: list of int (0 or 1) to show if sensor is calibratable
        """

        ia = KeysightE4990A([2391, 6153])
        rtd1 = PT100("D5")
        rtd2 = PT100("D6")
        self.sensors = {
                            "Keysight": ia,
                            "PT100_1": rtd1,
                            "PT100_2": rtd2
                       }
        calibratable = [sensor.property["calibratable"] for sensor in self.sensors.values()]
        return [*self.sensors], calibratable
    
    def measure_single(self, index):
        """Return measurement data of single sensor."""

        sensor = list(self.sensors.values())[index]
        return sensor.read()
        
    def measure_all(self):
        """Return measurement data of all sensors in self.sensors."""

        data = []
        for sensor in self.sensors.values():
            data.append(sensor.read())
        return data

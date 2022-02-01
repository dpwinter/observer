import Helper
import time
import numpy as np
import usbtmc
import board, busio, digitalio, adafruit_max31865

class Sensor(object):
    """
    Sensor Base Class. Should be used as parent class for new sensors.

    Provides unified interface to Sensors for SensorManager:
    1. sensorX._info
    2. sensorX.read()
    """

    def __init__(self):
        """Define _info array which should be filled by each sensor individually."""

        self._info = {
                        'name' : None,
                        'id': None,
                        'interface': None,
                        'link': None,
                        'type': None,
                        'calibratable': None,
                    }

    @property
    def property(self):
        """Information about Sensor."""

        return self._info.copy()

    def read(self):
        """
        Function to read a Sensor.

        Return:
        dict: information about sensor

        Note: _get() function of every sensor must return header, data, units in this exact order.
        """

        header, data, units = self._get()
        event = {
                    'id': self._info["id"],
                    'timestamp': Helper.get_timestamp(),
                    'header': header,
                    'data': data,
                    'units': units
                }

        return event

class KeysightE4990A(Sensor):
    """Class for Keysight E4990A connected via USB."""

    def __init__(self, addr):
        super().__init__()
        self._info["calibratable"] = 1
        self._info["link"] = usbtmc.Instrument(addr[0], addr[1])
        self._info["interface"] = "USB/SCPI"
        self._info["type"] = "Impedancer"
        self._info["id"] = self.__ask("*IDN?")
        # set usb timeout to 2 mins
        self._info["link"].timeout = 120 * 1000
        self.__setup()

    def __send(self, msg):
        """Send msg to Keysight E4990A."""

        self._info["link"].write(msg)
        return 1
    
    def __ask(self, msg):
        """
        Send msg to Keysight E4990A, return answer as string.
        
        Return:
        string: return message of device
        """

        ans = self._info["link"].ask(msg)
        return ans

    def __as_array(self, cmd):
        """Send cmd to Keysight E4990A, return answer as np.array."""

        return np.array([self.__ask(cmd).split(",")]).astype(np.float64)
    
    def __setup(self):  
        """Set Parameters on Keysight E4990A."""

        # initiate registers for polling
        self.__send("*RST")
        self.__send(":TRIGGER:SOURCE BUS")
        self.__send(":SYST:BEEP:COMP:STAT OFF")
        self.__send(":SYST:BEEP:WARN:STAT OFF")
        self.__send(":ABORT")
        self.__send(":INIT:CONT ON")

        # initiate operation registers
        self.__send(":STAT:OPER:PTR 0")
        self.__send(":STAT:OPER:NTR 16")
        self.__send(":STAT:OPER:ENAB 16")
        self.__send("*SRE 128")
        
        # setup measurement environment
        self.__send(":CALC1:PAR1:DEF CP")
        self.__send(":CALC1:PAR2:DEF D")
        self.__send(":SENS1:APER 2")    # set precision

        # setup display on Keysight 4990A
        self.__send(":SENS1:SWE:TYPE LOG")
        self.__send(":SENS1:FREQ:START 20")
        self.__send(":SENS1:FREQ:STOP 120E6")
        self.__send(":SENS1:CORR2:CKIT:LOAD:R 100")
        self.__send(":DISP:WINDOW1:Y:SCALE:DIV 10")
        self.__send(":DISP:WINDOW1:TRACE1:Y:SCALE:RPOS 5")
        self.__send(":DISP:WINDOW1:TRACE1:Y:SCALE:PDIV 100E-3")
        self.__send(":DISP:WINDOW1:TRACE1:Y:SCALE:RLEVEL -100E-3")
        self.__send(":DISP:WINDOW1:TRACE2:Y:SCALE:RPOS 5")
        self.__send(":DISP:WINDOW1:TRACE2:Y:SCALE:PDIV 200")
        self.__send(":DISP:WINDOW1:TRACE2:Y:SCALE:RLEVEL 400")

    """Alternative polling method. (Might be useful)"""
    # def __poll(self):
    #     # self.__send("*OPC?")
    #     self.__send(":TRIGGER:SINGLE")
    #     while(True):
    #         time.sleep(0.2)
    #         # operation register event changes after measurement is complete
    #         if self.__ask(":STAT:OPER:EVENT?") == "+16":
    #             self.__send(":ABOR")
    #             return

    def __poll(self):
        """
        Function to initiate measurement and waiting for its completion.
        
        Note: *OPC? call blocks program flow, this is no optimal solution.
        """

        self.__send(":TRIG:SING")
        self.__ask("*OPC?")

    def _get(self):
        """
        Sensor query function.
        
        Return values:
        header[3], data[points][3], units[3]
        """

        self.__poll()
        freq = self.__as_array(":SENS1:FREQ:DATA?")
        data = {}
        for i in range(1,3):
            self.__send(":CALC1:PAR%d:SEL"%i)
            data["PAR{0}".format(i)] = self.__as_array(":CALC1:DATA:FDAT?")
        # Omit imaginary part (by ::2)
        data = np.column_stack((freq[0], data["PAR1"][0][::2], data["PAR2"][0][::2]))
        header = ["Frequenz", "C-Wert", "D-Wert"]
        units = ["Hz", "F", "-"]
        self.__send("*CLS")
        return header, data, units

class PT100(Sensor):
    """Class for PT100 Temperature Sensors connected via SPI."""

    def __init__(self, cs_pin):
        super().__init__()

        self._info["calibratable"] = 0
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        cs = digitalio.DigitalInOut(getattr(board,cs_pin))

        self._info["link"] = adafruit_max31865.MAX31865(spi, cs, wires=4)
        self._info["interface"] = "SPI"
        self._info["type"] = "RTD"
        self._info["id"] = "PT100_%s" % cs_pin

    def _get(self):
        """
        Method for polling data via adafruit_max31865 library.
        
        Return:
        [string],[float],[string]
        """

        data = [self._info["link"].temperature]
        header = ["Temperature"]
        unit = ["*C"]
        return header, data,  unit

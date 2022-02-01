from Managers import *
from Controller import *

class MainWindow(QMainWindow):
    """Container for Widgets to be rendered on screen."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interval Measurement")
        self.showMaximized()

        wman = WidgetManager()
        sman = SensorManager()
        ctrl = Controller()

        wman.register_controller(ctrl)
        try:
            # get sensor configuration from sensor manager
            snames, calibratables = sman.create_sensors()
        except Exception as e:
            wman.message_box("One or more sensors not connected.\nCheck connection and restart.")
            QApplication.quit()

        # get widget configuration from widget manager
        main_widget = wman.create_widgets(snames, calibratables)
        self.setCentralWidget(main_widget)

        # setup model-view-controller
        ctrl.register_view(wman)
        ctrl.register_model(sman)

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()

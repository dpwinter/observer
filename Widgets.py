from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

"""Polymorphised Widgets that are used by the View."""

class CountTimer(QTimer):
    """A Timer that increments a counter with every timeout."""

    def __init__(self):
        super().__init__()
        self.cnt = 0

    def timerEvent(self, event):
        super().timerEvent(event)
        self.cnt += 1

    def stop(self):
        super().stop()
        self.cnt = 0

    def pause(self):
        super().stop()

class Button(QPushButton):
    """Send reference to pressed Button to Window Manager."""

    def __init__(self, txt, wm):
        super().__init__(txt)
        self.wm = wm

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.wm.button_pressed(self)

class ToggleButton(Button):
    """A Toggle Button that allows for changes of button's text."""

    def __init__(self, txts, wm):
        super().__init__(txts[0], wm)
        self.txts = txts
        self.setCheckable(1)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.isChecked():
            self.setText(self.txts[1])
        else:
            self.setText(self.txts[0])

    def set(self):
        self.setText(self.txts[1])
        self.setChecked(1)

    def reset(self):
        self.setText(self.txts[0])
        self.setChecked(0)

class RepeatButton(Button):
    """A recursive self-pushing button on mouse down."""

    def __init__(self, txt, wm):
        super().__init__(txt, wm)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAutoRepeat(1)
        self.setAutoRepeatDelay(250)
        self.setAutoRepeatInterval(1)

class Label(QLabel):
    """A Label that can be reinitialised to a preset init_text."""

    def __init__(self, txt):
        super().__init__(txt)
        self.init_txt = txt
        self.cnt = 0

    def set_count(self, cnt):
        self.cnt = cnt
        self.setText("Measurement %d" % self.cnt)

    def reset(self):
        self.setText(self.init_txt)
        self.cnt = 0

class Table(QTableWidget):
    """Custom table layout."""

    def __init__(self):
        """Set general QT5 appearance parameter."""

        QTableWidget.__init__(self)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(40)
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setColumnWidth(0, 200)
        self.setShowGrid(False)

class TimeDisplay(QTimeEdit):
    """A TimeEdit that allows for wrapping of sec to mins to hrs for more natural time selection."""

    def __init__(self):
        """Set general QT5 appearance parameter."""

        super().__init__()
        self.setAccelerated(1)
        self.setDisplayFormat("HH:mm:ss")
        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.setSelectedSection(QDateTimeEdit.SecondSection)
        self.interval = QTime(0,0)

    def reset(self):
        """Reset display to stored value."""

        self.setTime(self.interval)

    def stepBy(self, step):
        """Wrap time in sections."""

        if step < 0 and self.time() < QTime(0,0,1):
            return
        if self.currentSection() == QDateTimeEdit.HourSection:
            if step < 0 and self.time() < QTime(1,0,0):
                return
            elif step > 0 and self.time() > QTime(22,0,0):
                return
            else:
                self.setTime(self.time().addSecs(step * 3600))
        elif self.currentSection() == QDateTimeEdit.MinuteSection:
            if step < 0 and self.time() < QTime(0,1,0):
                return
            elif step > 0 and self.time() > QTime(23,58,0):
                return
            else:
                self.setTime(self.time().addSecs(step * 60))
        elif self.currentSection() == QDateTimeEdit.SecondSection:
            if step > 0 and self.time() > QTime(23, 59, 58):
                return
            else:
                self.setTime(self.time().addSecs(step))

        # Store reference to user set time
        self.interval = self.time()

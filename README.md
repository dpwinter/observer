# Observer
> A small object oriented interval GUI measurement program developed for Raspberry Pi and touch screens.

## Install

Download the repository, install requirements, if desired freeze package using for example pyInstaller.

## Overview

The App allows to simply start, stop and save interval measurements using different connected sensors. The interface is designed to be very simple and easily operable on a touch screen device.
![png](docs/images/App3.png)

Once started, the interface elements become inactive until the measurement is stopped. Usual measurements up to several weeks, thus the application needed to be developed with robostness in mind. Error messages are displayed at the bottom of the display in red.
![png](docs/images/App4.png)

Furthermore, a relational database scheme has been developed to store and access measurements remotely. This is particularly critical, as the device is usually carried around and connected to some setup for which a constant power supply is not always guaranteed.
![png](docs/images/RC_db_scheme.png)

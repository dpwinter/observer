# Observer
> A small object oriented interval GUI measurement program developed for Raspberry Pi and touch screens.

## Install

Download the repository, install requirements, if desired freeze package using for example pyInstaller.

## Overview

The App allows to simply start, stop and save interval measurements using different connected sensors. The interface is designed to be very simple and easily operable on a touch screen device. 

## Starting a measurement

Before starting a measurement, a user has to select the desired sensors from a list which is dynamically updated once new sensors are connected. Afterwards, he/she enters his/her database credentials for remote storage. A remote database is a critical feature for all use cases. Lastly, the measurement interval time is set either by entering a number directly via keyboard or, as it is more often the case, by setting the time via the touch screen using the *+* and *-* buttons. A final press on start proceeds to take data from the specified sensors after the interval time has passed and saves it to the cloud.

![png](docs/images/App3.png)

## Stopping a measurement

Once started, the interface elements become inactive until the measurement is stopped. Typical measurements last from days up to several weeks. For these relatively long periods the application had to be developed with robostness and self-correcting behavior in mind. Once an irreparable error occurs, the user is notified by a pop-up and via email.

![png](docs/images/App4.png)

## Database scheme

Furthermore, a relational database scheme has been developed to store and access measurements remotely. This is particularly critical, as the device is usually carried around and connected to some setup for which a constant power supply is not always guaranteed.

![png](docs/images/RC_db_scheme.png)

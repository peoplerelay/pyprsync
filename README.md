# pyprsync.py
*PeopleRelay external synchronizer*
***
## Description
**pyprsync.py** is service for [systemd](https://freedesktop.org/wiki/Software/systemd/) (Linux) that calls synchronization procedure from PeopleRelay database. There is not build-in scheduler in [Firebird 2.5](https://www.firebirdsql.org/en/firebird-2-5-8/), therefore external tool is required for timed synchronizations. **pyprsync.py** is made for robustness and simplicity. Run-time errors are suppressed in hope that system will recover.


## Prerequisites
* Python 3
* [FDB](https://www.firebirdsql.org/en/devel-python-driver/) Python library


## Installation and Configuration
Depending on operating system, [Firebird](https://www.firebirdsql.org/en/firebird-2-5-8/) and PeopleRelay setup, it can be required to edit script and configurations files. In typical case it should be enough to perform next steps:

* change connection parameters and synchronization interval in ***pyprsync.config***
* copy ***pyprsync.py*** to ***/usr/bin/***
* copy ***pyprsync.config*** to ***/etc/***
* copy ***pyprsync.service*** to *(systemd directory)**/system***
* enable ***pyprsync*** systemd service


## License
Apache License 2.0

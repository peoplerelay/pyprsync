  install -m 755 -o root ./pyprsync.py /usr/bin/pyprsync.py
  install -m 644 -o root ./pyprsync.config /etc/pyprsync.config
  install -m 644 -o root ./pyprsync.service /usr/lib/systemd/system/pyprsync.service

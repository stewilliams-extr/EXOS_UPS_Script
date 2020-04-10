# EXOS_UPS_Script
This script runs on an EXOS switch, and will poll a Synology NAS via SNMP to check if the UPS connected to it is on battery.  If it's on battery the script will check 3 times 30 seconds apart before disabling incline power.  Once the battery is charging the script will wait until the UPS is charged before enabling the ports.


* [EXOS UPS Script](exos_ups.py)


Switch UPM script and timer config.  It will run every 5 minutes.
```
create upm profile powerscript
load script exos_ups.py

.
configure upm profile powerscript maximum execution-time 120
create upm timer pwtime
configure upm timer pwtime profile powerscript
configure upm timer pwtime after 30 every 300```
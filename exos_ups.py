from pysnmp.entity.rfc3413.oneliner import cmdgen
from time import sleep
from exsh import clicmd


nopower = 0

#Settings for your Synology and ports to enable/disable
ip = '192.168.1.22'
oid = '1.3.6.1.4.1.6574.4.2.1.0'
snmp_ro = 'public'
disport = 'disable inline-power ports 1,2,3'
enport = 'enable inline-power ports 1,2,3'

#Function used to check SNMP for power status. returns SNMP reply
def powercheck():
    cmdGen = cmdgen.CommandGenerator()

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData(snmp_ro),
        cmdgen.UdpTransportTarget((ip, 161)), oid)

    # Check for errors and print out results
    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex)-1] or '?'
                )
            )
        else:
            for name, val in varBinds:
                output = val
    return output

output = powercheck()

#Catches when UPS is charged, and enables inline power only if it's disabled
if output == "OL":
    #clicmd('create log message "On Grid power and Charged"', True)
    if 'disabled' in clicmd('show inline-power stats ports 11', True):
        clicmd('create log message "On Grid and charged, going to full power captain!"', True)
        clicmd(enport, True)
    
#If power is out we check power 3 times to see if power is really out!  
if output == "OB" or output == "OB DISCHRG":
    clicmd('create log message "On Battery!"', True)
    for x in range(3):
        #Check to see if POE is already disabled
        if 'disabled' in clicmd('show inline-power stats ports 11', True):
            break
        sleep(30)
        new_ouput = powercheck() # capture new power status
        #Checking new UPS value to see if it's still charging.
        if new_ouput == "OB" or new_ouput == "OB DISCHRG":
            nopower += 1
            clicmd('create log message "Battery check {0}!"'.format(nopower), True)
        #If power has been checked 3 times disable ports using command in disport
        if nopower >= 3:
            clicmd('create log message "Powering down POE ports!"', True)
            clicmd(disport, True)
            break
#I don't want to enable my ports until my UPS is back to full power. So I wait and log.
if output == "OL CHRG":
    clicmd('create log message "Battery Charging please wait."', True)
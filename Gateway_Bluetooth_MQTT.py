import RPi.GPIO as GPIO
import time
import datetime
import bluetooth
from logentries import LogentriesHandler
import logging

#!/usr/bin/env python3

import paho.mqtt.client as mqtt

import os 

# Return CPU temperature as a character string                                      
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list                                        
# Index 0: total RAM                                                                
# Index 1: used RAM                                                                 
# Index 2: free RAM                                                                 
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string                                
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

# Return information about disk space as a list (unit included)                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                          
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                  
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])


log = logging.getLogger('logentries')
log.setLevel(logging.INFO)

log.addHandler(LogentriesHandler('84f0a7cc-6b39-41e9-a7a9-e8da2db0ad66'))

def bin2dec(string_num):
    return str(int(string_num, 2))

def read():        
    data = []
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(4,GPIO.OUT)
    GPIO.output(4,GPIO.HIGH)
    time.sleep(0.025)
    GPIO.output(4,GPIO.LOW)
    time.sleep(0.02)

    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for i in range(0,3500):
        data.append(GPIO.input(4))

    bit_count = 0
    tmp = 0
    count = 0
    HumidityBit = ""
    TemperatureBit = ""
    HumidityBitDec = ""
    TemperatureBitDec = ""
    crc = ""
    flag = 0

    try:
            while data[count] == 1:
                    tmp = 1
                    count = count + 1

            for i in range(0, 32):
                    bit_count = 0

                    while data[count] == 0:
                            tmp = 1
                            count = count + 1

                    while data[count] == 1:
                            bit_count = bit_count + 1
                            count = count + 1

                    if bit_count > 16:
                            if i>=0 and i<8:
                                    HumidityBit = HumidityBit + "1"
                            if i>=8 and i<16:
                                    HumidityBitDec = HumidityBitDec + "1"
                            if i>=16 and i<24:
                                    TemperatureBit = TemperatureBit + "1"
                            if i>=24 and i<32:
                                    TemperatureBitDec = TemperatureBitDec + "1"
                    else:
                            if i>=0 and i<8:
                                    HumidityBit = HumidityBit + "0"
                            if i>=8 and i<16:
                                    HumidityBitDec = HumidityBitDec + "0"
                            if i>=16 and i<24:
                                    TemperatureBit = TemperatureBit + "0"
                            if i>=24 and i<32:
                                    TemperatureBitDec = TemperatureBitDec + "0"

    except:
            flag = 1

    try:
            for i in range(0, 8):
                    bit_count = 0

                    while data[count] == 0:
                            tmp = 1
                            count = count + 1

                    while data[count] == 1:
                            bit_count = bit_count + 1
                            count = count + 1

                    if bit_count > 16:
                            crc = crc + "1"
                    else:
                            crc = crc + "0"
    except:
            flag = 1

    if HumidityBit != '' and TemperatureBit != '' and HumidityBitDec != '' and TemperatureBitDec != '':
        Humidity = bin2dec(HumidityBit)
        Temperature = bin2dec(TemperatureBit)
        HumidityDec = bin2dec(HumidityBitDec)
        TemperatureDec = bin2dec(TemperatureBitDec)
           
        h=int(Humidity)+float(HumidityDec)
        t=int(Temperature)+float(TemperatureDec)

       
        if(flag != 1):
            if h + t - int(bin2dec(crc)) == 0:
                CPU_Temp = str(getCPUtemperature())
                CPU_Usage = str(getCPUuse())
                
                RAM_stats = getRAMinfo()
                RAM_Used = str(round(int(RAM_stats[1]) / 1000,1))
                RAM_Free = str(round(int(RAM_stats[2]) / 1000,1))

                DISK_stats = getDiskSpace()
                DISK_Free = str(DISK_stats[1])
                DISK_Perc = str(DISK_stats[3])
                #print "%s        SensorId=Jignesh, Temperature=%s.%s, Humidity=%s.%s %%" %(datetime.datetime.now(), Temperature ,TemperatureDec,Humidity ,HumidityDec,)
                #print "CPU_temp = "+str(getCPUtemperature())+"CPU_usage = "+str(getCPUuse())+"RAM_total = "+str(round(int(RAM_stats[0]) / 1000,1))+"RAM_used = "+str(round(int(RAM_stats[1]) / 1000,1))+"RAM_free = "+str(round(int(RAM_stats[2]) / 1000,1))+"DISK_free = "+str(DISK_stats[1])+"DISK_perc = "+str(DISK_stats[3])
                #log.info("%s        SensorId=Jignesh, Temperature=%s.%s, Humidity=%s.%s %%" %(datetime.datetime.now(), Temperature ,TemperatureDec,Humidity ,HumidityDec,))
                log.info( "%s        SensorId=%s,  Temperature=%s.%s, Humidity=%s.%s %% , CPU_Temp=%s , RAM_Used=%s , RAM_Free=%s , DISK_Free=%s, DISK_Used=%s  "  % (datetime.datetime.now(), "Jignesh", Temperature, TemperatureDec, Humidity, HumidityDec,CPU_Temp, RAM_Used, RAM_Free,DISK_Free, DISK_Perc,))
                print "%s        SensorId=%s,  Temperature=%s.%s, Humidity=%s.%s %% , CPU_Temp=%s , RAM_Used=%s , RAM_Free=%s , DISK_Free=%s, DISK_Used=%s  "  % (datetime.datetime.now(), "Jignesh", Temperature, TemperatureDec, Humidity, HumidityDec,CPU_Temp, RAM_Used, RAM_Free,DISK_Free, DISK_Perc,)

        
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("topic/test")

def on_message(client, userdata, msg):
    print msg.payload.decode()
    log.info(msg.payload.decode())
    
    

    
#BluetoothServer    
server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
port = 2
server_sock.bind(("",port))
server_sock.listen(1)
client_sock,address = server_sock.accept()
print "Accepted connection from ",address
#MQTT Subscriber
client = mqtt.Client()
client.connect("192.168.0.33",1883,60)



i=0
while True:
    mod = i%24
    if mod < 12:
        data = client_sock.recv(1024)
        print data
        log.info(data)
    else:
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_start()
        if mod == 23:
            client.loop_stop()
    i = i+1
    #print mod
    read()
    time.sleep(5)




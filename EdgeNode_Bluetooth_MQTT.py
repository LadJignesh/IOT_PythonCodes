import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import datetime
import bluetooth
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



def bin2dec(string_num):
    return str(int(string_num, 2))
def read(i):
    data = []
    flag = 0;

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(4,GPIO.OUT)
    GPIO.output(4,GPIO.HIGH)
    time.sleep(0.025)
    GPIO.output(4,GPIO.LOW)
    time.sleep(0.02)

    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for i in range(0,3600):
        data.append(GPIO.input(4))

    bit_count = 0
    tmp = 0
    count = 0
    HumidityBit = ""
    TemperatureBit = ""
    HumidityBitDecimal = ""
    TemperatureBitDecimal = ""
    crc = ""

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
                    HumidityBitDecimal = HumidityBitDecimal + "1"
                if i>=16 and i<24:
                    TemperatureBit = TemperatureBit + "1"
                if i>=24 and i<32:
                    TemperatureBitDecimal = TemperatureBitDecimal + "1"
            else:
                if i>=0 and i<8:
                    HumidityBit = HumidityBit + "0"
                if i>=8 and i<16:
                    HumidityBitDecimal = HumidityBitDecimal + "0"
                if i>=16 and i<24:
                    TemperatureBit = TemperatureBit + "0"
                if i>=24 and i<32:
                    TemperatureBitDecimal = TemperatureBitDecimal + "0"

    except:
        flag = 1;
    if flag == 0:
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
        if flag == 0:
            Humidity = bin2dec(HumidityBit)
            HumidityDecimal = bin2dec(HumidityBitDecimal)
            Temperature = bin2dec(TemperatureBit)
            TemperatureDecimal = bin2dec(TemperatureBitDecimal)

            actualTemp = float(str(Temperature) + "." + str(TemperatureDecimal))
            actualHumidity = float(str(Humidity)+"."+str(HumidityDecimal))
            checksum = int(Humidity) + int(Temperature) + int(HumidityDecimal) + int(TemperatureDecimal) - int(bin2dec(crc))
            if checksum == 0:
                CPU_Temp = str(getCPUtemperature())
                #CPU_Usage = str(getCPUuse())
                
                RAM_stats = getRAMinfo()
                RAM_Used = str(round(int(RAM_stats[1]) / 1000,1))
                RAM_Free = str(round(int(RAM_stats[2]) / 1000,1))

                DISK_stats = getDiskSpace()
                DISK_Free = str(DISK_stats[1])
                DISK_Perc = str(DISK_stats[3])
                if mod < 12:
                    return "%s        Protocol=%s, SensorId=%s,  Temperature=%s.%s, Humidity=%s.%s %% , CPU_Temp=%s , RAM_Used=%s , RAM_Free=%s , DISK_Free=%s, DISK_Used=%s  "  % (datetime.datetime.now(),"Bluetooth", "Chirag", Temperature, TemperatureDecimal, Humidity, HumidityDecimal,CPU_Temp, RAM_Used, RAM_Free,DISK_Free, DISK_Perc,)
                else:
                    return "%s        Protocol=%s, SensorId=%s,  Temperature=%s.%s, Humidity=%s.%s %% , CPU_Temp=%s , RAM_Used=%s , RAM_Free=%s , DISK_Free=%s, DISK_Used=%s  "  % (datetime.datetime.now(),"MQTT", "Chirag", Temperature, TemperatureDecimal, Humidity, HumidityDecimal,CPU_Temp,RAM_Used, RAM_Free,DISK_Free, DISK_Perc,)
                    

bd_addr = "B8:27:EB:51:D9:E7"   #server bluetooth address
port = 2
sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))

client = mqtt.Client()
client.connect("localhost",1883,60)



i=0

while(True):
    mod = i%24
    val = read(mod)
    if val != None:
        print val
        if mod < 12 :
            sock.send(val)
        else:    
            client.publish("topic/test", val);
        i = i + 1
        time.sleep(5)

    

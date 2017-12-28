import RPi.GPIO as GPIO
import time



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

    Humidity = bin2dec(HumidityBit)
    Temperature = bin2dec(TemperatureBit)
    HumidityDec = bin2dec(HumidityBitDec)
    TemperatureDec = bin2dec(TemperatureBitDec)
    h=int(Humidity)+float(HumidityDec)
    t=int(Temperature)+float(TemperatureDec)
    
    if(flag != 1):
        if h + t - int(bin2dec(crc)) == 0:
            print time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->Humidity:"+ Humidity + "."+HumidityDec+"% ,  Temperature:"+ Temperature +"."+TemperatureDec+"C"
            with open("text.txt", "a") as myfile:
                myfile.write(time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->Humidity:"+ Humidity + "."+HumidityDec+"% ,  Temperature:"+ Temperature +"."+TemperatureDec+"C\n")
                if(int(Temperature) < 22):
                    myfile.write(time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->It's cold\n")
                    print time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->It's cold"
                elif(int(Temperature) > 27):
                    myfile.write(time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->It's very hot\n")
                    print time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->It's very hot"

                if(int(Humidity) <80):
                    myfile.write("Humidity is normal\n")
                    print "Humidity is normal"
                elif(int(Humidity) > 80 and int(Humidity) < 90):
                    myfile.write(time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"--> Humidity is high\n")
                    print time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"--> Humidity is high"
                elif(int(Humidity) >90):
                    myfile.write(time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->Humidity is very high\n")
                    print time.strftime("%d/%m/%Y")+"  "+time.strftime("%I:%M:%S")+"-->Humidity is very high"
                

while True:
    read()
    time.sleep(5)

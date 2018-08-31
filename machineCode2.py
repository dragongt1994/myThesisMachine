import numpy as np
import serial
import time
import RPi.GPIO as GPIO
import threading
import datetime
import time
d_0=33
d_1=474
class machine2:
    def __init__(self):
        self.ser=serial.Serial("/dev/ttyS0")
        self.ser.baudrate=9600

                
        GPIO.setmode(GPIO.BCM)
        self.DIR1=22
        self.RST1=27
        self.SR=17
        self.PWM1=18
        GPIO.setup(self.DIR1,GPIO.OUT)
        GPIO.setup(self.RST1,GPIO.OUT)
        GPIO.setup(self.SR,GPIO.OUT)
        GPIO.setup(self.PWM1,GPIO.OUT)
        GPIO.output(self.RST1,GPIO.HIGH)
        GPIO.output(self.DIR1,GPIO.HIGH)
        GPIO.output(self.SR,GPIO.HIGH)
        self.curr_dist=0
        self.Updt=True
        self.P = GPIO.PWM(self.PWM1,1000)
        self.lck=threading.RLock()
        self.P.start(100)
        self.upd_thr=threading.Thread(target=self.updateDist)
        self.disp_thr=threading.Thread(target=self.dispDist)
        
        self.recloop=True
    def Reset(self,i):
        if i==1:
            GPIO.output(self.RST1,GPIO.HIGH)
        elif i==0:
            GPIO.output(self.RST1,GPIO.LOW)
    def updateDist(self):
        while self.Updt:
   #         self.lck.acquire()
            self.curr_dist=self.getDist()
    #        self.lck.release()
            time.sleep(0.00005)
    #        print(self.curr_dist)
    def startRecordDistanceLoop(self,s):
        rec_thr=threading.Thread(target=self.recordDistance,args=(s,))
        rec_thr.start()
    def stopDistanceRecord(self):
        self.recloop=False
    def recordDistance(self,s):
        dist_rec=open(s,'w')
        print("start")
        print(str(self.curr_dist))
        self.recloop=True
        t1=time.time()
        
        while self.recloop:
       #     self.lck.acquire()
            temp=self.curr_dist
     #       print(temp)
        #    self.lck.release()
            t2=time.time()
            td=t2-t1
            tcurr=td
           # print("tcurr= "+str(tcurr))
            dist_rec.write(str(temp)+','+str(tcurr)+'\n')
            #time.sleep(0.1)
        print("done")
        dist_rec.close()

    def startUpdateLoop(self):
        self.upd_thr.start()
    def dispDist(self):
        print('dispDist')
        while True:
            print(self.curr_dist)
    def startDispDistLoop(self):
        self.disp_thr.start()
        
    def getDist(self):
        
        self.ser.write([0x55])
        temp=self.ser.read()
        temp2=self.ser.read()
        #time.sleep(0.01)
        tempb=int(temp[0])
        temp2b=int(temp2[0])
        temp3=((tempb*256)+temp2b)
        return temp3
    def setDutyCycle(self,d):
        self.P.ChangeDutyCycle(d)
        
        
    def checkSpeed(self,t):
##        print('here')
        self.Reset(0) 
        d0=self.curr_dist
        self.direct(0)
        self.Reset(1)
        time.sleep(t)
        self.Reset(0)
        d1=self.curr_dist
         
        sp=(d1-d0)/t
   ##     print(d1)
 ##       print(d0)
        self.sp=sp
    #    print(sp)
        return sp
    def direct(self,d):
        if d==0:
            GPIO.output(self.DIR1,GPIO.LOW)
        elif d==1:
            GPIO.output(self.DIR1,GPIO.HIGH)

    def setPosition(self,p):
        
        curr=self.getDist()
        #print('here')
        if curr>p:
            self.direct(1)
            self.Reset(1)
            temp=self.getDist()
            #print('a1')
            while temp>p:
                temp=self.getDist()
                print(temp)
                None
            self.Reset(0)
            return self.getDist()
        else:
            
            self.direct(0)
            self.Reset(1)
            temp=self.getDist()
         #   print('a2')
            while temp<=p:
                print(temp)
                temp=self.getDist()
                
                None
            self.Reset(0)
            return self.getDist()
    def setPosition2(self,p):
        tot=0

        res=0
        self.Reset(1)
        Kp=6
        Ki=0.5
      #  p=(p-38)/200
        while True:
            curr1=self.getDist()
            curr=((curr1-d_0)/(d_1-d_0))*100
            #print(curr)
            #print(curr)
            e=p-curr#
            #print(e)
            tot=tot+e
            

            ead=Kp*e+Ki*tot
           # print(ead)
            if ead>0:
                self.direct(0)
            else:
                self.direct(1)
            res=abs(ead)
            if res<1:
                self.Reset(0)
                break
            #print(res)
            if res<0:
                res=0
            elif res>100:
                res=100
            self.setDutyCycle(int(res))
    def setPosition3Thread(self,p):

#        print(s)
        temp=threading.Thread(target=self.setPosition3,args=(p,))
        temp.start()
    def setPosition3(self,p):
        tot=0

        res=0
        self.Reset(1)
        Kp=6
        Ki=0.6
      #  p=(p-38)/200
        while True:
            self.lck.acquire()
   #         print(self.curr_dist)
            
            curr1=self.curr_dist+1
            curr1=curr1-1
            t1=datetime.datetime.now()
            time.sleep(0.01)
            t2=datetime.datetime.now()
            #print(t2-t1)
            #449
            curr=((curr1-32)/449)*100
            #print(curr)
            self.lck.release()
     #       print(curr)
            #print(curr)
            #print(curr)
            e=p-curr#
            
            tot=tot+e
            

            ead=Kp*e+Ki*tot
           # print(ead)
            if ead>0:
                self.direct(0)
            else:
                self.direct(1)
            res=abs(ead)
            
            res=res*res
            #print(res)
            #print(res)
            if res<0.05:
                print(res)
                self.Reset(0)
                break
            if res<0:
                res=0
            elif res>100:
                res=100
            self.setDutyCycle(int(res))
    def shake(self,c,t,d):
        self.Reset(1)
        o=0
        self.setDutyCycle(d)
        for i in range(0,c):
            self.direct(0)
            time.sleep(t)
            self.direct(1)
            time.sleep(t)
        self.Reset(0)

    

    def process(self,S):
        self.file1=open('distpac/speed'+S+'.txt','w')
        for c in range(10,99):
            i=c
            self.setPosition3(30)
            
            self.setDutyCycle(i)
            self.startRecordDistanceLoop('distpac/dist '+str(c)+'.txt')
            p=self.checkSpeed(1)
            self.stopDistanceRecord()

            a=str(i)+','+str(p)+'\n'
            print(a)
            self.file1.write(a)
        self.file1.close()

    def push(self,duty,t):
        self.setDutyCycle(duty)

        self.Reset(1)
        self.direct(0)
        time.sleep(t)
        self.Reset(0)

    def PIDController(self,SP,PV,getDist):
        Kp=1
        Ki=0.3
        SPa=np.array(SP)
        PVa=np.array(PV)
        Tset=0


        while True:
            PV=getDist()
            e=SP-PV
            self.errI=self.errI+e
            ead=Kp*SPa+Ki*self.errI
            Tset=Tset-ead

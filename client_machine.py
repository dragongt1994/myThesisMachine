import struct
import hashlib
import math
from enum import Enum
import socket
import socketserver

#from enum import enum
def md5(bt):
    hash_md5 = hashlib.md5()
    hash_md5.update(bt)
    return hash_md5.hexdigest()

class messageType(Enum):
    CONN_REQT=2
    CONN_CONF=3
    SEND_FILE=4
    SEND_REQT=5
    SEND_CONF=6
    SEND_SUCC=7

def message(msg_type,size=None, snum=None, username=None, fname=None, mname=None, lname=None, machine=None ):
    if msg_type==messageType.CONN_REQT:
       # msgtype=struct.unpack('i', val[1])
        dat=struct.pack('i', msg_type.value)+str.encode(username)+ str.encode(fname)+ str.encode(mname)+str.encode(lname)
    elif msg_type==messageType.CONN_CONF:
        dat=struct.pack('i', msg_type.value)+struct.pack('I', machine)
    elif msg_type==messageType.SEND_REQT:
        dat=struct.pack('I', msg_type.value)+struct.pack('I', size)+struct.pack('I', snum)
    elif msg_type==messageType.SEND_FILE:
        dat=struct.pack('I', msg_type.value)+struct.pack('I', size)+struct.pack('I', snum)
    elif msg_type==messageType.SEND_CONF:
        dat=struct.pack('I', msg_type.value)+ str.encode(machine)
    return dat

def parseMessage(dat):
    msgtype=struct.unpack('i', dat[0:4])
    username=str.decode(dat[4:14])
    fname=str.decode(dat[14:24])
    mname=str.decode(dat[24:34])
    lname=str.decode(dat[34:44])

class earthquakeData:
    def __init__(self,npts=0,delta=0,maxv=0,minv=0,val=None, f=None):
        if f!=None:
            self.fname=f
            temp=f.read()
            self.npts=struct.unpack('I',temp[0:4])
            self.delta=struct.unpack('f',temp[4:8])
            self.maxv=struct.unpack('f',temp[8:12])
            self.minv=struct.unpack('f',temp[12:16])
            print (self.npts)
            print(self.delta)
            print(maxv)
            print(minv)
            fnum=len(temp[16:])
            #print(len(temp[16:]))
            tp=self.npts[0]
            print(tp)
            self.val=struct.unpack('f'*tp,temp[16:])
        else:
            self.npts=npts
            self.delta=delta
            self.maxv=maxv
            self.minv=minv
            self.val=val
            print (self.npts)
            print(self.delta)
            print(maxv)
            print(minv)
    def saveToFile(self,fname):
        f=open(fname,"wb")
        f.write(self.packData())
        f.close()
    def packData(self):
        temp= struct.pack('i', self.npts)
        temp=temp+struct.pack('f', self.delta)
        temp=temp+struct.pack('f', self.maxv)
        temp=temp+struct.pack('f', self.minv)
        temp=temp+struct.pack('%sf'%self.npts, *self.val)
        return temp
    #4096
class Packet:
    def __init__(self, dat=None, p=None):
        if p==None:
            l=len(dat)
            self.__dat=dat
            res=[]
            self.dat_size=l
            nmb=math.ceil(l/4056)
            print("nmb"+ str(nmb))
            for ctr in range(0, nmb):
                pck_temp=self.dat[ctr*4056:(ctr+1)*4056]
                tdat=pck_temp
                l=len(tdat)
                print("4060-l="+str(4056-l))
                temp=bytes([0]*(4056-l))
                temp2=struct.pack('i',ctr)+struct.pack('i',l)+tdat+temp
                s=md5(temp2)
                s2=str.encode(s)
                temp2=temp2+s2
                print(len(temp2))
                res=res+[temp2]
            
            self.__pck=res
        else:
            self.dat_size=0
            self.__dat=[]
            print('')
            for tmp in p:
                l=int(struct.unpack('i', tmp[4:8] )[0])
                print("l="+str(l))
                self.__dat=self.__dat+[tmp[8 :(8+l)]]
                self.dat_size=self.dat_size+l
                
            self.__pck=p
    @property
    def dat(self):
        return self.__dat
      #  print(fin)

    @property
    def pck(self):
        return self.__pck
    
    def isOkay(self):
        
        temp=self.__dat
        s=md5(temp)
        s2=str.encode(s)
        
    

class clientMachine:
    def __init__(self, username,fname,mname, lname, currData=None):
        self.username=username
        self.fname=fname
        self.mname=mname
        self.lname=lname
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.__currData=currData
    @property
    def currData(self):
        return self.__currData
    
    @currData.setter
    def currData(self, currData):
        self.__currData=currData
    
        
    def saveToFile(self,fname):
        f=open(fname,"b")
        f.write(self.__currData.packData())

    def sendData(self):
        max_length=4
        
    def askConnection(self, host, port):
        self.sck.connect((host, port))
        #username,fname,mname,lname 30 for whole

        dat=message(messageType.CONN_REQT, username=self.username, fname=self. fname, mname= self.mname,lname= self.lname)
        msg=Packet(dat)
        print(dat)
        strm=bytearray(msg.pck[0])
        #print(strm)
        self.sck.send(strm)
        r=self.sck.recv(4096)
        tp=Packet(p=[r]).dat
        t= Packet(p=[r]).dat
        t=t[0]
        temp=struct.unpack('I',t[0:4])
        print("before confirmation")
        print(temp)
        if temp[0]==messageType.CONN_CONF.value:
            print("confirmed")
            dat=self.__currData
            tot_dat=Packet(dat).pck
            dat=message(messageType.SEND_REQT,size=4096,snum=len(tot_dat))
            msg=Packet(dat)
            strm=bytearray(msg.pck[0])
        #print(strm)
            self.sck.send(strm)

            print("initiate Recieve")
            r=self.sck.recv(4096)
            print(r)
            print("received")
            t=Packet(p=[r]).dat
            print("packed")
            t=t[0]
            print(t)
            temp=struct.unpack('I',t[0:4])
            print("temp="+str(temp))
            print("Confirming Available")
            if temp[0]==messageType.SEND_CONF.value:
                ctr=0
                print("send confirmed")
                for tdat in tot_dat:
                    #strm=pickle.dumps(msg.pck)
                    #self.sck.send(strm)
                    self.sck.send(tdat)
#                    ftemp=open("pack_dat/pack_"+str(ctr)+".dat", "wb")
#                    ftemp.write(tdat)
#                    ftemp.close()
                    print(ctr)
                    ctr=ctr+1
            
            
        
        #ftemp=open("pack_"+str(ctr)+".dat", "wb")
        #ftemp.write(tdat)
        #ft    emp.close()
    #            self.sck.send(tdat.packData)
    

    
class serverMachine(socketserver.BaseRequestHandler):
        
    def handle(self):
        # self.request is the TCP socket connected to the clien
        print("Connected")
        data = self.request.recv(4096)
        tdat=Packet(p=[data]).dat
        dat=tdat[0]
        print(dat[:])
        msgtype=struct.unpack('i', dat[0:4])[0]
        print(msgtype)
        print(dat[4:14])
        self.username=dat[4:14].decode('utf-8')
        self.fname=dat[14:24].decode('utf-8')
        self.mname=dat[24:34].decode('utf-8')
        self.lname=dat[34:44].decode('utf-8')
        if msgtype== messageType.CONN_REQT.value:
            print("reqested")
            tmp=message(messageType.CONN_CONF, machine="machine")
            msg=Packet(dat=tmp)
            tp=bytearray(msg.pck[0])
            print("sending")
            self.request.send(tp)
            print("finally sent")
            data = self.request.recv(4096)
            print("received something")
            print(data)
            tdat=Packet(p=[data]).dat[0]
            print(tdat)
            msgtype=struct.unpack('i', tdat[0:4])[0]
            print(msgtype)
            if msgtype==messageType.SEND_REQT.value:
                print("requested send")
                size=struct.unpack("i", tdat[4:8])[0]
                snum=struct.unpack("i", tdat[8:12])[0]
                tmp=message(messageType.SEND_CONF, machine="mach1")
                msg=Packet(dat=tmp)
                tp=bytearray(msg.pck[0])
                self.request.send(tp)
                print("size="+str(size)+" snum="+str(size))
                temp=[]
                for ctr in range(0, snum):
                    dat=self.request.recv(4096)
                    temp=temp+[dat]
                final_file=Packet(p=temp)
                cont=final_file.dat
                ctr=0
                for files in cont:
                    ftemp=open("pack_"+str(ctr)+".dat", "wb")
                    ftemp.write(files)
                    ftemp.close()
                    ctr=ctr+1
                tmp=message
                
        
        
        
        
        


#eq.saveToFile("earth.dat")
#eq

#if __name__ == "__main__":
  #  main()


import struct

COMM=1
CONFI=2
    
    
REQT_WEIGHT=1
REQT_ACCELE=2
REQT_M_ACCELE=3
SET_TIME=4
CONN_REQT=5
    
START_ACCELE_REC=6
STOP_ACCELE_REC=7
START_WEIGHT_REC=8
TRANS=9
TRANS_ACCEL=10

FIN_WEIGHT_INIT=11
class Message:
    def __init__(self,msg=None, com=None,val=None, buf=None):
        print("new")
        if buf!=None:
            self.mssg_type=struct.unpack('i', buf[0:4])[0]
            self.comm_type=struct.unpack('i', buf[4:8])[0]
            self.value=struct.unpack('f', buf[8:12])[0]
            self.CRC=struct.unpack('I', buf[12:16])[0]
            self.buff=buf[0:16]
        elif msg!=None and com!=None and val!=None:
            self.mssg_type=msg
            self.comm_type=com
            self.value=val
            temp=struct.pack("i", msg)+struct.pack("i", com)+struct.pack("f", val)
            self.CRC=getCRC32(temp) & 0xFFFFFFFF
            temp2=struct.pack("I", self.CRC)

            self.buff=temp+temp2
    def isOkay(self):
        temp=getCRC32(self.buff[0:12])
        if temp==self.CRC:
            return True
        else:
            return False
            
class Message2:
    def __init__(self, mssg_type=None, comm_type=None, value=None, buff=None):
        if buff==None:
            if type(mssg_type)==str and type(comm_type)==str and type(value)==str:
                self.mssg_type=mssg_type
                self.comm_type=comm_type
                self.value=value
            else:
                self.mssg_type=mssg_type
                self.comm_type=comm_type
                self.value=str(value)
            self.buff=self.mssg_type+" "+self.comm_type+" "+self.value
        else:
            self.buff=buff
            res=self.buff.split(' ')
            self.mssg_type=res[0]
            self.comm_type=res[1]
            self.value=res[2]
        
        

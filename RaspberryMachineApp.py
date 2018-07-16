from PyQt4.QtGui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import sys
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from PyQt4 import QtGui
from math import pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
import _thread
import datetime

from client_machine import *
from machineCode2 import machine2
class Window(QtGui.QDialog):
    def __init__(self,tx, ty, trig, parent=None):
        super(Window, self).__init__(parent)
        
        # a figure instance to plot on
        self.tx=tx
        self.ty=ty
        self.trig=trig
        self.figure=Figure()
        self.canvas = FigureCanvas(self.figure)
        
        plt.ylim(-1, 1)
        plt.xlim(0, 100)
        print("Please click")
        res = plt.ginput(0)
        plt.close()
        x=[]
        y=[]
        for i in res:
            x=x+[i[0]]
            y=y+[i[1]]
    
        x=np.array(x)
        sort_index =np.argsort(x)
        x=x[sort_index]
        y=np.array(y)
        y=y[sort_index]
        f = interp1d(x, y)
        xnew = np.linspace(x[0], x[len(x)-1], num=100, endpoint=True)
        ax = self.figure.add_subplot(111)

        #coord=self.figure2.ginput(0)

    
        self.figure = Figure()
        
        
        self.xnew=xnew
        self.ynew=f(xnew)
        # refresh canvas
        print("here")
        b, a = signal.butter(2, 1)
        
        res = signal.filtfilt(b, a, self.ynew)
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        ax = self.figure.add_subplot(111)
        ax.set_xlim(0, 100)
        ax.set_ylim(-1, 1)
        ax.plot(self.xnew, res, '--') 
        
        
        self.tx[0]=self.xnew.copy()
        self.ty[0]=self.ynew.copy()
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.frSB=QDoubleSpinBox()
        self.frSB.setMinimum(0.01)
        self.frSB.setSingleStep(0.01)
        self.frSB.setMaximum(1)
        self.frSB.setValue(1)
        self.frSB.valueChanged.connect(self.plot)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.frSB)
        self.setLayout(layout)
        
        
        
        self.canvas.draw()
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        
        # Just some button connected to `plot` method

    
    def closeEvent(self, event):
        tempx=self.tx[0]
        self.trig(name="drawnGraph", d=datetime.datetime.now(), dur=(tempx[len(tempx)-1]-tempx[0]))
        #self.trig(name="drawnGraph", d=datetime.datetime.now())
    def plot(self):
        ''' plot some random stuff '''
        # random data

        b, a = signal.butter(2,self.frSB.value())
        
        res = signal.filtfilt(b, a, self.ynew)
        ax = self.figure.add_subplot(111)
        
        
        self.tx[0]=self.xnew.copy()
        self.ty[0]=res.copy()
        # discards the old graph
        ax.clear()

        # plot data
        ax.set_xlim(0, 100)
        ax.set_ylim(-1, 1)
        ax.plot(self.xnew, res, '--')
        
        # refresh canvas
        self.canvas.draw()
        
    
class PeriodGraph(QtGui.QDialog):
    def __init__(self,tx, ty, trig, parent=None):
        super(PeriodGraph, self).__init__(parent)
        # a figure instance to plot on
        self.tx=tx
        self.ty=ty
        self.trig=trig
        self.figure=Figure()
        self.canvas = FigureCanvas(self.figure)

        self.ax=self.figure.add_subplot(111)

        self.frSB=QDoubleSpinBox()
        self.frSB.setMinimum(0.1)
        self.frSB.setMaximum(15)
        self.frSB.setSingleStep(.1)
        self.frSB.valueChanged.connect(self.graphPlot)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.canvas)
        
        self.hbox1=QHBoxLayout()
        
        self.label1=QLabel("Freqency")
        self.hbox1.addWidget(self.label1)
        self.hbox1.addWidget(self.frSB)
        
        self.label1=QLabel("Shape of Signal")
        self.shapeTypeCB=QComboBox()
        self.shapeTypeCB.addItem("Sine")
        self.shapeTypeCB.addItem("Saw")
        self.shapeTypeCB.addItem("Square")
        self.shapeTypeCB.currentIndexChanged.connect(self.graphPlot)
#        self.graphButton=QPushButton("Draw")
#        
#        self.graphButton.clicked.connect(self.graphPlot)
#        
        self.hbox2=QHBoxLayout()
        self.hbox2.addWidget(self.label1)
        self.hbox2.addWidget(self.shapeTypeCB)
        
        self.label2=QLabel("Time")
        self.timeSB=QSpinBox()
        self.timeSB.setMinimum(5)
        self.timeSB.setMaximum(100)
        self.timeSB.valueChanged.connect(self.graphPlot)
        
        self.hbox3=QHBoxLayout()
        self.hbox3.addWidget(self.label2)
        self.hbox3.addWidget(self.timeSB)
        
        self.magnitude=QDoubleSpinBox()
        self.label3=QLabel("Magnitude")
        self.magnitude.setMinimum(0.01)
        self.magnitude.setMaximum(1)
        self.magnitude.setSingleStep(0.01)
        self.magnitude.valueChanged.connect(self.graphPlot)
    
        self.hbox4=QHBoxLayout()
        self.hbox4.addWidget(self.label3)
        self.hbox4.addWidget(self.magnitude)
        
        
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.vbox.addLayout(self.hbox4)
#        self.vbox.addWidget(self.graphButton)
        
        self.setLayout(self.vbox)
        self.graphPlot()
    def graphPlot(self):
        xnew = np.linspace(0, self.timeSB.value(), num=(self.timeSB.value()*100), endpoint=True)
        ynew =np.sin(xnew*self.frSB.value())
        print(ynew)
        print("here")
        if self.shapeTypeCB.currentIndex()==0:
        #    xnew = np.linspace(0, self.timeSB.value(), num=(self.timeSB.value()*100), endpoint=True)
            ynew =np.sin(xnew*self.frSB.value())
            
        elif self.shapeTypeCB.currentIndex()==2:
        #   xnew = np.linspace(0, self.timeSB.value(), num=(self.timeSB.value()*100), endpoint=True)
            ynew=self.squareWave(self.frSB.value(), xnew)
        elif self.shapeTypeCB.currentIndex()==1:
            ynew=signal.sawtooth(2 * np.pi * self.frSB.value() * xnew, width=0.5)
        
        ynew=ynew*self.magnitude.value()
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-1,1)
        self.ax.plot(xnew, ynew, '--')
        self.canvas.draw()
        
        self.tx[0]=xnew.copy()
        self.ty[0]=ynew.copy()
    def squareWave(self, f, t):
        return signal.square(2 * np.pi * f * t)
        #return (4/pi)*(np.sin(2*pi*f*t)+(1/3)*np.sin(6*pi*f*t)+(1/5)*np.sin(10*pi*f*t))
    def closeEvent(self, event):
        tempx=self.tx[0]
        self.trig(name="PeriodGraph", d=datetime.datetime.now(), dur=(tempx[len(tempx)-1]-tempx[0]))
class Screen(QWidget):
    def __init__(self):
        self.x=[[None]]
        self.y=[[None]]
        self.item=machine2()
        super(Screen, self).__init__()
        
        self.initUI()
    @pyqtSlot()    
    def graphInput(self):
        try:
            self.w1=Window(self.x, self.y, self.procGraph)
            self.w1.show()
        except Exception as e:
            print(e)
#            t = np.arange(10)
#            plt.plot(t, np.sin(t))
#            print("Please click")
#            coord = plt.ginput(0)
#            print(coord[(0):])
#            #print("clicked", x)
#            
#            plt.close()
    def periodGraphInput(self):
        self.w2=PeriodGraph(self.x, self.y, self.procGraph)
        self.w2.show()
    
    def procGraph(self, name="",d=None, dur=None ):
        print("checkd")
        if self.x[0]!=None:
            print(self.x[0])
            print(self.y[0])
            print("dur= "+str(dur/len(self.x[0])))
            eq=earthquakeData(len(self.y[0]), dur/len(self.x[0]), 1, -1, self.y[0])
            s=name+"-"+str(d.day)+"-"+str(d.month)+"-"+str(d.year)+"-"+str(d.second)+"-"+str(d.minute)+"-"+str(d.hour)+".dat"
            print(s)
            print("proc")
            eq.saveToFile(os.getcwd()+"/pack_dat"+"/"+s)
            print("here10")
            self.ax.clear()
            self.ax.set_xlim(0, 100)
            self.ax.set_ylim(-1,1)
            self.ax.plot(self.x[0], self.y[0], '--')
            self.refreshList()
            self.canvas.draw()
    def clickedItem(self, v):
        print("click")
        print(v.text())
        path=os.getcwd()+"/pack_dat"+"/"
        
        a=open(path+v.text(), "rb")
        re=earthquakeData(f=a)
        val=re.val
        print(re.npts)
        t=np.array(range(0, re.npts[0]))*re.delta[0]
        self.x[0]=t.tolist().copy()
        self.y[0]=val
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-1,1)
        self.ax.plot(self.x[0], self.y[0], '--')
        #self.refreshList()
        self.canvas.draw()
#        print(val)
    def setPosition(self):
        
        #self.item.setPosition3(int(self.posSB.value()))
        print("start")
        _thread.start_new_thread(self.item.setPosition3,(int(self.posSB.value()),))
        print("end")
    def initUI(self):
        
        self.item.startUpdateLoop()
        self.listWidget = QListWidget()
        self.listWidget.itemClicked.connect(self.clickedItem)
        tmp=[]
        for i in range(1, 10):
            tmp=tmp+[str(i)]
        #self.sp = QLineEdit()
        #self.sp.setInputMask("99")
        self.figure=Figure()
        #ax = self.figure.add_subplot(111)
        
        
        self.canvas = FigureCanvas(self.figure)
        self.ax=self.figure.add_subplot(111)
        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([-1, 1])
        
       
        
        self.execButton=QPushButton("Execute")
        self.execButton.clicked.connect(self.procGraph)
        self.addDrawGraph=QPushButton("Add Graph")
        self.addDrawGraph.clicked.connect(self.graphInput)
        
        self.addPeriodGraph=QPushButton("Add Period Graph")
        self.addPeriodGraph.clicked.connect(self.periodGraphInput)
        
        vbox = QVBoxLayout()

        vbox.addStretch(1)
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.listWidget)
        
        
        
        self.hbox = QHBoxLayout()
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.execButton)
        self.hbox.addWidget(self.addDrawGraph)
        self.hbox.addWidget(self.addPeriodGraph)
        
        self.label4=QLabel("Position")
        self.posSB=QSpinBox()
        self.posSB.setMinimum(0)
        self.posSB.setMaximum(100)
        
        self.posButton=QPushButton("Set Position")
        
        self.hbox2=QHBoxLayout()
        self.hbox2.addWidget(self.label4)
        self.hbox2.addWidget(self.posSB)
        self.hbox2.addWidget(self.posButton)

        self.posButton.clicked.connect(self.setPosition)
        
        
#        self.frSB=QSpinBox()
#        self.frSB.setMinimum(0)
#        self.frSB.setMaximum(100)
        
#        self.label1=QLabel("Frequency")
#        
#        self.hbox2 = QHBoxLayout()
#        #self.hbox2.addStretch(1)
#        self.hbox2.addWidget(self.label1)
#        self.hbox2.addWidget(self.frSB)
#        
#        self.frSB2=QDoubleSpinBox()
#        self.frSB2.setMinimum(0)
#        self.frSB2.setMaximum(100)
#        self.frSB2.setSingleStep(0.01)
#        self.label2=QLabel("Magnitude")
        
#        self.hbox3 = QHBoxLayout()
        #self.hbox2.addStretch(1)
#        self.hbox3.addWidget(self.label2)
#        self.hbox3.addWidget(self.frSB2)
#        
        
        vbox.addLayout(self.hbox)
        vbox.addLayout(self.hbox2)
#        vbox.addLayout(self.hbox2)
#        vbox.addLayout(self.hbox3)
        
        #Resize width and height
        self.listWidget.resize(300,120)
        dirpath = os.getcwd()+"/pack_dat/"
        print("current directory is : " + dirpath)
        foldername = os.path.basename(dirpath)
        print("Directory name is : " + foldername)
        mypath=dirpath
        #temp=[]
        #for f in listdir(mypath):
        #   temp=temp+[dirpath+f]
        files = filter(os.path.isfile, os.listdir(dirpath))
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
       # print(onlyfiles)
        #print("here4")
        #files=os.listdir(mypath)
        #print(files)
        files.sort(reverse=True, key=lambda f:os.path.getmtime(os.path.join(dirpath, f)))
        print("here5")
        for f in files:
           self.listWidget.addItem(f)
        self.setLayout(vbox)
        print("here3")
        self.show()
    
    def refreshList(self):
        self.listWidget.clear()
        mypath=os.getcwd()+"/pack_dat"
        #name_list=os.listdir(path)
        name = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        #name_list = os.listdir(path)
        #full_list = [os.path.join(path,i) for i in name_list]
        name.sort(reverse=True, key=lambda f:os.path.getmtime(os.path.join(mypath, f)))

        #print(files)
        for f in name:
           self.listWidget.addItem(f)
        self.listWidget.update()
    
    def keyPressEvent(self, event):
        key = event.key()
        print(key)

    
class myListWidget(QListWidget):

   def Clicked(self,item):
      QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())
    
def main():
    app = QApplication(sys.argv)
    temp=Screen()
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()

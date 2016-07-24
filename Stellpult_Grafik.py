#!/usr/bin/env python3

# Programm zur Ansteuerung von 10 Maerklin 5625 Weichenantrieben
#
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import Toplevel
import time
import os
import sys, getopt
import copy
import RPi.GPIO as GPIO


version = "1.5.1" # 1.0 Function Keys, Hilfetext mit Strg+h, getestet mit Schaltung
                # 1.1 Shutdowen Funktion
                # 1.2 Konfiguration aus Datei einlesen
                # 1.3 Stromschalter fuer Abstellgleise
                # 1.4 Lok Liste
                # 1.5 Buttons üeber Gleis positioniert
                # 2.0 Resized fuer 7zoll Display
on = 0
off = 1
fahrweg = 8
delay=0.2
canvas_width = 800
canvas_height = 480
weichen = []
abstellgleis = []
window = []
root = []
led = []
bttn = []
button_color="white smoke"
wcolor="white"
debug_level = 0
debug_level_text= ""
out=sys.stderr
cmd="."
helpfile="./Stellpult_Grafik_help.txt"
config_file="./Stellpult_Grafik.cfg"

########################################################################
#
# Einlesen einer Konfiguration aus Datei
#
########################################################################
class Skin:
    def __init__ (self, file):
        self.logo = "./images/Zug-48.gif"
        self.button_color = "white smoke"
        self.window_bg = "white"
        self.width = canvas_width
        self.height = canvas_height
        self.helpfile = "./Stellpult_Grafik_help.txt"
        self.LED_on = "./images/LED_gruen.gif"
        self.LED_off	= "./images/LED_rot.gif"
        self.Stellpult_img = "./images/Gleisstellbild-v3.gif"
        self.button_test = "./images/test.gif"
        self.button_shutdown = "./images/shutdown.gif"
        self.button_exit = "./images/exit.gif"
        self.config_file = config_file
        self.switch_on = "./images/Schalter_ein.gif"
        self.switch_off = "./images/Schalter_aus.gif"       

        if file != "":
            self.config_file = file    
    
        try:
            f = open(self.config_file)
        except:
            print("config file ", self.config_file, " nicht gefunden")
        exit

        inhalt = f.readlines()
        for zeile in inhalt:
            #print ("line: ", zeile) 
            name, v = zeile.split("\t",3)
            
            if v[len(v)-1] == "\n":   # \n am ende der zeile loeschen
                value = v[:len(v)-1]
                if debug_level >2:
                    print ("name=", name, "wert=", repr(value))
                
            if name == "button_color":
                self.button_color = value
            elif name == "window_bg":
                self.window_bg = value
            elif name == "width":
                self.width = int(value)
            elif name == "height":
                self.height = int(value)
            elif name == "helpfile":
                self.helpfile = value
            elif name == "LED_on":
                self.LED_on = value
            elif name == "LED_off":
                self.LED_off = value
            elif name == "Stellpult_img":
                self.Stellpult_img = value
            elif name == "button_test":
                self.button_test = value
            elif name == "button_shutdown":
                self.button_shutdown = value
            elif name == "button_exit":
                self.button_exit = value
            elif name == "logo":
                self.logo = value
            elif name == "switch_on":
                self.switch_on = value
            elif name == "switch_off":
                self.switch_off = value
            else:
                print("unbekannte ID ", name, "mit Wert ", value)
                


########################################################################
class RedirectText(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, text_ctrl):
        """Constructor"""
        self.output = text_ctrl
 
    #----------------------------------------------------------------------
    def write(self, string):
        """"""
        self.output.insert(END, string)
 
 

class MyApp(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent, title):
        """Constructor"""
        self.root = parent
        self.title = title
        self.root.title(self.title)
        self.frame = Frame(parent)
        self.frame.pack()
 
        self.text = scrolledtext.ScrolledText(self.frame)
        self.text.pack()
 
        # redirect stdout
        redir = RedirectText(self.text)
        sys.stdout = redir
        del redir

    def end(self):
       sys.stdout=out
       
       
   
        
        
########################################################################
        


#--------------------------------------------------------------------------------------             
# Raspi herunterfahren
#--------------------------------------------------------------------------------------
def shutdown():
    # nochmal nachfragen
    if messagebox.askokcancel("Shutdown", "wirklich herunterfahren?", parent=window):
        GPIO.cleanup()  # GPIOs resetten
        root.destroy()  # Fenster schliessen
        print("shutdown")
        os.system("shutdown -h now")
    else:
        return

#--------------------------------------------------------------------------------------             
# Programm beenden
#--------------------------------------------------------------------------------------
def quit():
    # nochmal nachfragen
    if messagebox.askokcancel("Programm beenden", "wirklich beenden?", parent=window):
        GPIO.cleanup()  # GPIOs resetten
        root.destroy()  # Fenster schliessen
    else:
        return
#--------------------------------------------------------------------------------------             
# Hilfetext ausgeben
#--------------------------------------------------------------------------------------

def help_event(event):
    try:
        h = open(helpfile)
    except:
        print(helpfile, " nicht gefunden")

    inhalt = h.readlines()
    h.close()
    if debug_level >2:
        print (helpfile)
        print (inhalt)

    helpw = Tk()
    helpw.title("Hilfe")
    helpw.frame = Frame(helpw, bg=wcolor)
    helpw.frame.pack()
# Alternative mit Scrollbar 
#    helpw.text = scrolledtext.ScrolledText(helpw.frame)
#    helpw.text.insert(END,inhalt)

    helpw.text = Text(helpw.frame, height=12, width=80)
    helpw.text.pack()
    for zeile in inhalt:
       helpw.text.insert(END, zeile)
    b=Button(helpw, text="schliessen", command=helpw.destroy, bg=button_color, takefocus=True)
    b.focus_set()
    b.pack()
    
#--------------------------------------------------------------------------------------             
# Testprogramm, Aufruf mit Strg+t, schaltet alle Weichen udn Abstellgleise
#--------------------------------------------------------------------------------------    
def weichentest():
    
    global debug_level

    l=debug_level
    debug_level=3
    for i in range(0,10):
        print("======================================================")
        weichen[i].stellen(0)
        weichen[i].stellen(1)

    print("= Abstellgleise ==========================================")
    for i in range(0,4):
        abstellgleis[i].switch()
        time.sleep(delay)
        abstellgleis[i].switch()
        time.sleep(delay)
    debug_level=l

    
def test():
    tw = Toplevel(None, height=300, width=400)
    l=MyApp(tw, "Test Output")
    button=Button(tw, text="schliessen", command=tw.destroy, highlightthickness=1, takefocus=True)
    button.focus_set()
    button.pack()
    weichentest()
    l.end()

# Wrapper fuer Tastatur events 
def test_event(event):
    test()

def quit_event(event):
    quit()

def debuglevel(event):
    global debug_level, debug_level_text
    if "KP_" in event.keysym:
        debug_level = int(event.keysym[3:])
    elif event.char in "0123456789":
        try:
            debug_level = int(event.char)
        except:
            return
    if debug_level == 0:
        debug_level_text.set("")
    else:
        debug_level_text.set("Debug Level = " + str(debug_level))    
   
       
#--------------------------------------------------------------------------------------             
# Klassen Definitionen
#--------------------------------------------------------------------------------------   
class Led_image:
    def __init__(self, on, off):
        self.on  = PhotoImage(file=on)
        self.off = PhotoImage(file=off)
    
    def display(self,modus):
        if modus == 0:
            print ("led on: ", self.on)
        elif modus == 1:
            print ("led off:", self.off)
        else:
            print ("Fehler: led nich definiert")
        

    
########################################################################################
class Fahrstrasse:    
    def __init__(self, nr):
#              xpos, ypos, Button Text,          Weichenstellg, Funktionstaste
        fstr =[[540, 210, "Abstellgleis 3 [F3]" , "1001nnnnnn", 'F3'], \
               [540, 150, "Abstellgleis 2 [F2]" , "101nnnnnnn", "F2"], \
               [540,  95, "Abstellgleis 1 [F1]" , "11nnn0nnnn", "F1"], \
               [600, 370, "Lok 2 [F5]"          , "10000nnnnn", "F5"], \
               [600, 310, "Lok 1 [F4]"          , "10001nnnnn", "F4"], \
               [195, 235, "Bhf 1 [F6]"          , "0nnnnnn1nn", "F6"], \
               [195, 295, "Bhf 2 [F7]"          , "0nnnnnn010", "F7"], \
               [177, 370, "Bhf Durchfahrt [F9]" , "0nnnnnn011", "F9"], \
               [250, 430, "Bekohlung [F8]"      , "0nnnnnn00n", "F8"]]
        
        self.number = nr
        self.x =    fstr[nr-1][0]
        self.y =    fstr[nr-1][1]
        self.name = fstr[nr-1][2]
        self.code = fstr[nr-1][3]
        self.binding = fstr[nr-1][4]

    def weg_stellen(self): #-----------------------------------------------------------------------
        if debug_level >0:
            print(self.name, self.code)
            
        for i in range(0,len(self.code)):
            
            if self.code[i] != 'n':
                r=int(self.code[i])

                if debug_level >1:
                    print("Weg stellen - Weiche ", i+1, "auf ", r)
                weichen[i].stellen(r)

###################################################################################################                
class Weiche:
    def __init__(self, nr, richtung):
        # LED Koordinaten, je zwei Leds pro Weiche
        ledc = [[293,  17, 263,  38], \
                [327, 102, 359,  79], \
                [379, 158, 409, 137], \
                [443, 222, 473, 197], \
                [542, 326, 568, 301], \
                [645,  78, 610,  58], \
                [610,  17, 635,  39], \
                [480, 422, 485, 386], \
                [390, 422, 397, 386], \
                [139, 336, 160, 361]]

        # Koordinaten fuer Weichenbeschriftung
        wlabel = [225,  27], \
                 [272,  75], \
                 [330, 135], \
                 [385, 194], \
                 [487, 300], \
                 [558,  52], \
                 [655,  35], \
                 [510, 435], \
                 [421, 435], \
                 [120, 300]   
        
        # benutzte GPIO ports des RaspberryPi B+
        # jeweils 2 fuer einen Weichenantrieb (gerade=0, rund=1)      
        pin_bcm = [ 2,  3,  4, 17, 27, 22, 10,  9, \
                   11,  5,  6, 13, 19, 26, 14, 15, \
                   18, 23, 24, 25]
        self.nr = nr                    # Nr der Weiche (1-10
        self.label = "W"+str(nr)        # Bezeichnung W1 - W10
        self.labelx = wlabel[nr-1][0]   # x-Position des Labels
        self.labely = wlabel[nr-1][1]   # y-Position des Labels
        self.richtung = richtung        # Stellung der Weiche 0=gerade, 1=rund
        self.x1 = ledc[nr-1][0]         # Position des Tasters fuer Gerade
        self.y1 = ledc[nr-1][1]
        self.x2 = ledc[nr-1][2]         # Position des Tasters fuer rund
        self.y2 = ledc[nr-1][3]
        self.img0 = led.on              # Icon fuer Taster gerade
        self.img1 = led.off             # Icon fuer Taster rund
        self.bcm = [pin_bcm[(self.nr-1)*2], pin_bcm[(self.nr-1)*2+1]] # GPIO Pons für gerade und rund Schaltung
        self.s0 = Button (window, image=led.on, command=self.stellen_g, bd=0, highlightthickness=0, highlightcolor="yellow", bg=wcolor, takefocus=True)
        self.s1 = Button (window, image=led.off, command=self.stellen_r, bd=0, highlightthickness=0, highlightcolor="yellow", bg=wcolor, takefocus=True)
        self.w0 = window.create_window(self.x1, self.y1, window=self.s0, anchor=CENTER)
        self.w1 = window.create_window(self.x2, self.y2, window=self.s1, anchor=CENTER)

        # initialize GPIO ports to output 3.3V, one per Relay
        GPIO.setup(self.bcm[0],GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.bcm[1],GPIO.OUT, initial=GPIO.HIGH)

    # Leds zeichnen ------------------------------------------------------------
    def redraw(self):
        self.s0.configure(image=self.img0)
        self.s1.configure(image=self.img1)
        window.update()
        
    # Weiche stellen -----------------------------------------------------------
    def stellen(self, richtung):
        if debug_level >1:
            print ("Weiche ", self.nr, "steht auf ", self.richtung)
            
        if self.richtung != richtung:
            self.richtung=richtung
            if self.richtung == 0:
                self.img0 = led.on
                self.img1 = led.off
            elif self.richtung == 1:
                self.img0 = led.off
                self.img1 = led.on
            else:
                print ("Fehler: Weiche stellen: ungueltige Richtung", hex(richtung))

        if debug_level >0:
            print ("stelle Weiche ", self.nr, "auf ", self.richtung)   
        
        self.redraw()
        self.display()  # Informationen zur Weiche ausgeben

        bcm=self.bcm[self.richtung]
        
        GPIO.output(bcm, GPIO.LOW)  # hier passierts: der GPIO Pin wird auf Null gestellt und zieht damit das Relais an
        if debug_level >2:
            print("Weiche", self.nr,': gpio write ', bcm)
        time.sleep(delay)           # warten für einen kurzen Impuls
        GPIO.output(bcm, GPIO.HIGH) # und jetzt den GPIO Pin wieder mit Spannung belegen
        return (bcm)

    # Wrapper für Callbacks ----------------------------------------------------
    def stellen_g(self):
        self.stellen(0)

    def stellen_r(self):
        self.stellen(1)
        
    # Debug Informationen ausgeben ---------------------------------------------
    def display(self):
        if debug_level >2:
            print ("\nWeiche ", self.nr)
            print ("  Richtung:   ", self.richtung)
            print ("  Koordinaten: G(",self.x1,":", self.y1, "), R(", self.x2, ":", self.y2, ")")
            print ("  Image0:     ", self.img0)
            print ("  Image1:     ", self.img1)
            print ("  BCM:         G=", self.bcm[0], "R=", self.bcm[1])
            print ("  S0:         ", self.s0)
            print ("  S1:         ", self.s1)       
            print ("  Window0:    ", self.w0)
            print ("  Window1:    ", self.w1, "\n")


###################################################################################################
class Abstellgleis:
            
    def __init__(self, nr):
        x = 710
    # Ein/Aus Schalter   x, y, state, bcm
        abstellgleis = [[x,  83,  on, 8],\
                        [x, 142,  on, 7],\
                        [x, 200,  on, 12],\
                        [x, 330
                         ,  on, 16]] # Lokschuppen: beide Gleise werden gemeinsam geschaltet
        
        self.nr = nr
        self.image = image_on
        self.state = on # Abstellgleis hat Strom
        i = nr
        if 0 <= i <= len(abstellgleis) :
            self.bcm = abstellgleis[i][3]
            self.button = Button (window, image=self.image, command=self.switch, bd=0, highlightthickness=0, highlightcolor="yellow", bg=wcolor, takefocus=True)
            self.window = window.create_window(abstellgleis[i][0], abstellgleis[i][1], window=self.button, anchor=CENTER)
            # initialize GPIO ports to output 3.3V, one per Relay
            GPIO.setup(self.bcm,GPIO.OUT, initial=on)
        else:
            print("init Abstellgleis failed ", self.nr)
            exit(0)
        

    # Schalter umlegen ----------------------------------------------------------------------------        
    def switch(self):
        if self.state == on:
            self.state = off
            self.image = image_off
        else:
            self.state = on
            self.image = image_on

        # hier das gpio commando
        GPIO.output(self.bcm, self.state)  # Anders als bei den Weichen wird das Relais noch nicht zurückgeschaltet         
        self.button.configure(image=self.image) # Bild aendern
        window.update()
        self.display()   
        
    # Debug Informationen ausgeben ---------------------------------------------
    def display(self):
        if debug_level >2:
            print("Abstellgleis", self.nr,': gpio write ', self.bcm, self.state) 
 
               
#--------------------------------------------------------------------------------------------------
# Behandlung der Function Keys F1 - F9
#--------------------------------------------------------------------------------------------------

def fkey_callback(event):
    if event.char != event.keysym and len(event.char) > -1 :
        for i in range (0,9):
            f = Fahrstrasse(i+1)
            if debug_level > 1:
                print (f.binding, event.keysym)
            if f.binding == event.keysym:
                f.weg_stellen()
                break
#--------------------------------------------------------------------------------------------------
# Behandlung des Keyboard Inputs zur direkten Weichenansteuerung, z.B. w8r fuer Weiche 8 auf rund
#--------------------------------------------------------------------------------------------------
            
def key(event):
    global cmd
    global weichen

    if debug_level >3:
        print ("pressed ", event.char, repr(event.char))
        print ("        ", event.keysym)
        print ("cmd: ", cmd, "event.char ", event.char)

    if event.char == "w":
        cmd="w"  # Sequenz für Abstellgleis (a) oder Lokschuppen(l) initialisiert
    elif event.char in "al":
        cmd=str(event.char)
    elif cmd[0] == "w" and event.char in "gr":
        nr=int(cmd[1:])
        if event.char == "g":
            r=0
        else:
            r=1
        if 0 <= nr <= 10:
            if debug_level >1:
                print ("Weiche ", nr, "auf", r)
            weichen[nr-1].stellen(r)
        cmd="."
    elif cmd[0] == "w" and event.char in "0123456789":
        cmd=cmd+event.char
    elif cmd[0] in "al" and event.char in "123":
        cmd=cmd+str(event.char)
        nr=int(event.char)-1
        if cmd[0] == "l":
            nr=3  # Lok1 und 2 sind Abstellgleis 3 und 4
        abstellgleis[nr].switch()
        cmd="."
    else:
        if cmd[0] =="." and event.char in "0123456789":
            debuglevel(event)
        cmd="."
    
#--------------------------------------------------------------------------------------------------
# gipt koordinaten bei Mauscklick aus - nur für Layout Gestaltung
#--------------------------------------------------------------------------------------------------

def mouse_callback(event):
    if debug_level > 2:
        print ("clicked at ", event.x, event.y)
        

#-------------------------------------------------------------------------------------------------- 
# Initialisierung
#--------------------------------------------------------------------------------------------------

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # set board mode to Broadcom numbering scheme

# Behandlung der Argumente
# cmd [-d|--debug <debug-level> -f|--file <config_file>]

try:
    opts, args = getopt.getopt(sys.argv[1:], "hd:f:", ["help", "debug=", "file="])
    for o, a in opts:
        if o in ("-h", "--help"):
            print ("usage: argv[0] -d | --debug <level> -f|--file <config_file>" )
            quit()
        elif o in ("-d", "--debug"):
            debug_level = int(a)
            if debug_level >0:
                debug_level_text.set("Debug Level = " + a)
                print ("cmd:", sys.argv)
        elif o in ("-f", "--file"):
            skin.config_file = a
        else:
            assert False, "falsche Option"
            exit
            
except getopt.GetoptError as err:
    print (err)
    exit
#---------------------------------------------------------------------------------------------------
# Benutzeroberflaeche definieren
#---------------------------------------------------------------------------------------------------
root = Tk()
root.title ("Stellpult "+str(version))
#root.overrideredirect(1)
root.attributes('-fullscreen', True)

skin = Skin(config_file) # Konfiguration einlesen

window = Canvas(root, 
           width  = skin.width, 
           height = skin.height)

canvas_width = skin.width
canvas_height= skin.height

debug_level_text = StringVar(window)

# Hintergrund Image in Hauptfenster laden
try:
    img1 = PhotoImage(file=skin.Stellpult_img)
    window.create_image(0,0, anchor=NW, image=img1)
except:
    print("Fehler: kein Gleisbild")
    exit(0)
    
# Logo in rechte obere Ecke laden, wenn vorhanden
try:
    img2 = PhotoImage(file=skin.logo)
    window.create_image(skin.width-5,10, anchor=NE, image=img2)
except:
    print ("kein Logo")

window.pack()

# LED Schalter und Label fuer Weichen in Root-Window laden
led = Led_image(skin.LED_on, skin.LED_off)
for i in range(0,10):
    w = Weiche(i+1,0)  
    l=Label(None, text=w.label, bg=skin.window_bg)
    window.create_window(w.labelx, w.labely, window=l, anchor=NW)
    weichen.append(w)

# Schalter fuer Abstellgleise laden
try:
    image_on = PhotoImage(file=skin.switch_on)
    image_off = PhotoImage(file=skin.switch_off)
except:
    print ("Fehler: Keine Dateien für Schalter: ", skin.switch_on)
    exit (0)
for i in range (0,4):
    gls = Abstellgleis(i)
    abstellgleis.append(gls)

# Buttons fuer Fahrstrassen laden
for i in range(1,10):
    fahrweg = Fahrstrasse(i)
    if i == 8:
        fahrweg.weg_stellen() # Initialisierung auf Fahrstrasse Bahnhof Durchfahrt bei Start
    b = Button(None, text=fahrweg.name, command=fahrweg.weg_stellen, bd=1, highlightthickness=1, highlightcolor="orange",bg=skin.button_color, takefocus=True)
    window.create_window(fahrweg.x, fahrweg.y, window=b, anchor=NW)
    bttn.append(b)
    fkey="<F"+str(i)+">"
    window.bind(fkey, fkey_callback)


    window.bind("<Button-1>", mouse_callback) # hat keine Funktion ausser die Mauskoordinaten auszgeben

window.focus_set()

# Exit Button laden
exit_img = PhotoImage(file=skin.button_exit)
exitb = Button (None, image=exit_img, command=quit, bd=0, highlightthickness=0, highlightcolor="red", bg=skin.window_bg, takefocus=True)
window.create_window(canvas_width-40, canvas_height-50, window=exitb, anchor=NW)

# Shutdown Button laden
sd_img = PhotoImage(file=skin.button_shutdown)
sdb = Button (None, image=sd_img, command=shutdown, bd=0, highlightthickness=0, highlightcolor="red", bg=skin.window_bg, takefocus=True)
window.create_window(canvas_width-80, canvas_height-50, window=sdb, anchor=NW)

# Test Button laden
test_img = PhotoImage(file=skin.button_test)
testb = Button (None, image=test_img, command=test, bd=0, highlightthickness=0, highlightcolor="blue", bg=skin.window_bg, takefocus=True)
window.create_window(canvas_width-120, canvas_height-50, window=testb, anchor=NW)

# weitere Key bindngs
window.bind("<Control-x>", quit_event)  # beenden bei Strg-x
window.bind("<Control-t>", test_event)  # testen bei Strg-t
window.bind("<Control-h>", help_event)  # Hilfetext ausgeben
for k in range(0,10):                   # 0-9 aus dem Num Block setzt den Debuglevel
    fkey="<KP_"+str(k)+">"
    window.bind(fkey,debuglevel)

window.bind("<Key>",key)                # alle anderen Tatstatureingaben

# Debug Level anzeigen
dlabel = Label (window, textvariable=debug_level_text, bg=wcolor, anchor=NW)
if debug_level >0:
    debug_level_text.set("Debug Level = " + str(debug_level))
window.create_window(10, 10, window=dlabel, anchor=NW)

# Lok IDs anzeigen
xpos = 110
ypos = 75
img = []

window.create_rectangle (xpos-5, ypos-15, xpos+135, ypos+140)
for i in range (0,4):
    imgf = "./images/Lok_"+str(i+1)+".gif"
    try:
        img.append(PhotoImage(file=imgf))
        txt="Lok "+str(i+1)
        if debug_level >2:
            print (txt, imgf, img[i])
        wlabel=Label(window, text=txt, bg=skin.window_bg)
        window.create_window(xpos, ypos, window=wlabel, anchor=NW)
        window.create_image(xpos+50,ypos-10, image=img[i], anchor=NW)
        ypos=ypos+35
    except:
        print("Datei mit Lok Image fehlt: ", imgf)


mainloop() # tkinter never ending main loop   

exit

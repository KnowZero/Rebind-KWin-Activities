#!/usr/bin/env python3
import subprocess
import dbus
import dbus.service
import os
import signal
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

SCRIPT_NAME = "RebindKWinActivities"

class RebindKWinActivities:
    """Main class to restart kwin activities"""
    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.sigCount = 0
        self.loop = GLib.MainLoop()
        self.bus = dbus.SessionBus()
        self.window_list = self.get_window_list()
        print("Found Windows:", len(self.window_list))
        
        signal.signal(signal.SIGINT, self.cleanup)
        self.script_id = self.dbus_send(
                service='org.kde.KWin', 
                path='/Scripting', 
                interface='org.kde.kwin.Scripting'
        ).loadScript(os.path.dirname(os.path.realpath(__file__)) + '/'+SCRIPT_NAME+'.js', SCRIPT_NAME, signature='ss')
        
        if int(self.script_id) > -1:
            print("Loaded KWin script into ID:", self.script_id)
            self.dbus_listen()
            #time.sleep(10.0)
            self.dbus_send(
                    service='org.kde.KWin', 
                    path='/' + str(self.script_id), 
                    interface='org.kde.kwin.Script'
            ).run()
            
            print("Waiting for callback")
            self.dbus_wait()
            print("KWin script finished executing")
            
        else:
             print("Failed to load KWin script!")
             
        self.cleanup()
            
    def cleanup(self, signal=None, frame=None):
        if self.sigCount == 0:
            self.sigCount+=1
            self.dbus_send(
                    service='org.kde.KWin', 
                    path='/Scripting', 
                    interface='org.kde.kwin.Scripting'
            ).unloadScript(SCRIPT_NAME)
            print ("Cleanup: Removed Script")
        elif signal is not None:
            print("Failed to remove script!")
        
        if signal is not None:
            exit()
        
    
    def dbus_listen(self):
        self.DBusListen(self)
    
    def dbus_wait(self):
        self.loop.run()
    
    def dbus_send(self, service, path, interface ):
        obj = self.bus.get_object(service, path)
        return dbus.Interface(obj, interface)
        

    def wmctrl(self):
        process = subprocess.Popen(['wmctrl', '-lp'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        return str(stdout,'utf-8').split('\n')
    
    def get_window_list(self):
        window_list = []
        
        for item in self.wmctrl():
            item = item.split(' ')
            if len(item) > 2 and item[1] != '-1':
                
                process = subprocess.Popen(['xprop', '-id', item[0], '_KDE_NET_WM_ACTIVITIES'],
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                uuid =  str(stdout,'utf-8').replace('_KDE_NET_WM_ACTIVITIES(STRING) = "','').replace('"\n','')
                
                if 'not found' not in uuid:
                    if not item[3]: item[3] = 0
                    
                    window_list.append({'wid':item[0], 'pid':item[3], 'aid':uuid.split(',') })

        return window_list

    class DBusListen(dbus.service.Object):
        RES_ENUM = {
                '0':['UNKNOWN FAILURE!','\033[91m'],
                '1':['SUCCESS','\033[92m'],
                '2':['activities already exist so skipped',''],
                '3':['SKIPPED DUE TO UNKNOWN ACTIVITY!','\033[93m'],
                '8':['failed, but not a normal window so it is okay',''],
                '9':['FAILED!','\033[91m']
        }
        
        def __init__(self, caller):
            self.caller = caller
            self.loop = caller.loop
            bus = dbus.SessionBus()
            bus.request_name('org.kde.KWin.Script.' + SCRIPT_NAME)
            bus_name = dbus.service.BusName('org.kde.KWin.Scripting', bus=bus)
            dbus.service.Object.__init__(self, bus_name, '/callback')

        @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="", out_signature="aa{sv}")
        def WindowList(self):
            print ("Sent Window list to KWin Script")
            return_list = dbus.Array()
            for rec in self.caller.window_list:
                return_list.append(dbus.Dictionary(rec, signature='sv'))
                
            return return_list

        @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="aa{sv}", out_signature="")
        def Finish(self, result):
            
            self.caller.cleanup()
            
            print ("Results:")
            for rec in result:
                print ( self.RES_ENUM[ rec['result'] ][1] + rec['wid'], rec['pid'], rec['title'], ':', self.RES_ENUM[ rec['result'] ][0] + '\033[0m'  )
            
            input("Press Enter to continue...")
            self.loop.quit()

if __name__ == '__main__':
    print("Starting...")
    RebindKWinActivities()

#! /usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#

import pygtk
pygtk.require('2.0')
import os, sys, gtk, gobject

import hashlib
import researchSharingDemoTest


def getID(email):
    id=hashlib.sha1()
    id.update(email)
    return id.digest()


class LoginWindow:
    def __init__(self,name=None,eid=None,port=None,nip=None,nport=None,grps=None):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        
        
        self.window.set_default_size(400, 200)
        #print(name)
        
        self.window.connect("delete-event", self.exitApp)
        
        # Layout the window
        highLevelVbox = gtk.VBox(spacing=3)
        self.window.add(highLevelVbox)
        highLevelVbox.show()
        
        notebook = gtk.Notebook()
        notebook.set_tab_pos(pos=gtk.POS_TOP)
        notebook.show()
        highLevelVbox.pack_start(notebook,expand=True, fill=True)
        
        vbox = gtk.VBox(spacing=3)
        vbox.show()
        
        notebook.append_page(vbox, gtk.Label('Current User Login'))
     
       
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("Name:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.peerName = gtk.Entry()
        hbox.pack_start(self.peerName, expand=True, fill=True)
        if(name):
            self.peerName.set_text(name)
        self.peerName.show()	
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("Email:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.eid = gtk.Entry()
        hbox.pack_start(self.eid, expand=True, fill=True)
        if(eid):
            self.eid.set_text(eid)
        self.eid.show()	
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("Groups:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.grps = gtk.Entry()
        hbox.pack_start(self.grps, expand=True, fill=True)
        if(grps):
            self.grps.set_text(grps)
        self.eid.show()	
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("Port:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.port = gtk.Entry()
        hbox.pack_start(self.port, expand=True, fill=True)
        if(port):
            self.port.set_text(port)
        self.port.show()	
        
        
        self.guest =  gtk.CheckButton('Guest Login')
        hbox.pack_start(self.guest, expand=False, fill=False)
        
        self.guest.show()
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("BootStrap Node IP:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.bs_nip = gtk.Entry()
        hbox.pack_start(self.bs_nip, expand=True, fill=True)
        if(nip):
            self.bs_nip.set_text(nip)
        self.bs_nip.show()	
        label = gtk.Label("Port:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.bs_nport = gtk.Entry()
        hbox.pack_start(self.bs_nport, expand=True, fill=True)
        if(nport):
            self.bs_nport.set_text(nport)
        self.bs_nport.show()	
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("BootStrap Nodes Filename:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.bs_nfile = gtk.Entry()
        hbox.pack_start(self.bs_nfile, expand=True, fill=True)
        self.bs_nfile.set_text('You may give absolute path. However Relative path will suffice.')
        self.bs_nfile.show()	
        
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        button = gtk.Button('Create New Network')
        hbox.pack_start(button, expand=False, fill=False)
        button.connect("clicked", self.create)
        button.show()
        
        button = gtk.Button('Connect To Bootstrap Node IP')
        hbox.pack_start(button, expand=False, fill=False)
        button.connect("clicked", self.bs_ip)
        button.show()
        
        button = gtk.Button('Connect To Bootstrap Nodes from File')
        hbox.pack_start(button, expand=False, fill=False)
        button.connect("clicked", self.bs_file)
        button.show()
        print('reached')

        
        
        
        vbox.pack_start(hbox,expand=False, fill=False)
        self.window.set_title('COP - User Login')
        self.window.show_all()
        self.window.present()
        print('reached')
        
        
    def exitApp(self, widget, data=None):
        self.record()        
        gtk.main_quit()
    
    def record(self):
        fin = open("userdata",'w')
        fin.write(self.peerName.get_text()+'\n')
        fin.write(self.eid.get_text()+'\n')
        fin.write(self.port.get_text()+'\n')
        fin.write(self.grps.get_text()+'\n')
        fin.write(self.bs_nip.get_text()+'\n')
        fin.write(self.bs_nport.get_text()+'\n')
        fin.close()
    
    def create(self,sender=None):
        name= self.peerName.get_text()
        #print 'name',name
        eid= self.eid.get_text()
        id = getID(self.eid.get_text())
        guest=self.guest.get_active()
        port=self.port.get_text()
        grps = self.grps.get_text()
        #print 'port',port
        if(not guest):
            self.record()
        self.window.destroy()
        gtk.main_quit()
        researchSharingDemoTest.initall(name,eid,id,port,guest,None,grps)
        
        
        
    def bs_file(self,sender):
        name= self.peerName.get_text()
        #print 'name',name
        id = getID(self.eid.get_text())
        eid= self.eid.get_text()
        guest=self.guest.get_active()
        port=self.port.get_text()
        grps = self.grps.get_text()
        knownNodes = []
        f = open(self.bs_nfile.get_text(), 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            ipAddress, udpPort = line.split()
            knownNodes.append((ipAddress, int(udpPort)))
        #print 'port',port
        if(not guest):
            self.record()
        self.window.destroy()
        gtk.main_quit()
        researchSharingDemoTest.initall(name,eid,id,port,guest,knownNodes,grps)
       
        
    def bs_ip(self,sender):
        name= self.peerName.get_text()
        #print 'name',name
        eid= self.eid.get_text()
        id = getID(self.eid.get_text())
        guest=self.guest.get_active()
        port=self.port.get_text()
        grps = self.grps.get_text()
        knownNodes = [(self.bs_nip.get_text(), int(self.bs_nport.get_text()))]
        #print 'port',port
        if(not guest):
            self.record()
        self.window.destroy()
        gtk.main_quit()
        researchSharingDemoTest.initall(name,eid,id,port,guest,knownNodes,grps)
        
        
    def main(self):
        gtk.main()
    
if __name__ == '__main__':
    try:
     fin = open("userdata",'r')
     name = fin.readline().strip()
     eid = fin.readline().strip()
     port = fin.readline().strip()
     grps = fin.readline().strip()
     nip = fin.readline().strip()
     nport = fin.readline().strip()
     
     fin.close()
     window = LoginWindow(name,eid,port,nip,nport,grps)
    except IOError:
     print 'thisone'
     window = LoginWindow()	    
    window.main()   
       
    

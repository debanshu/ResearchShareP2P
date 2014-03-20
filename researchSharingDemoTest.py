#! /usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#

import pygtk
pygtk.require('2.0')
import os, sys, gtk, gobject

from twisted.internet import gtk2reactor
gtk2reactor.install()
import twisted.internet.reactor

from twisted.internet import defer
from twisted.internet.protocol import Protocol, ServerFactory, ClientCreator

import hashlib

import entangled.node
from entangled.kademlia.datastore import SQLiteDataStore

def getID(email):
    id=hashlib.sha1()
    id.update(email)
    return id.digest()

def initall(name,eid,nid,port,guest,knownNodes,groups):
    dataStore = None#SQLiteDataStore(os.path.expanduser('~')+'/.entangled/fileshare.sqlite')
			
		
    node = entangled.node.EntangledNode(id = nid,udpPort= int(port), dataStore=dataStore)
		
    print node.id
    node.invalidKeywords.extend(('mp3', 'png', 'jpg', 'txt', 'ogg'))
    node.keywordSplitters.extend(('-', '!','.','_',',',':'))
    window = FileShareWindow(node,port,groups,name,eid,guest)
		
    window.set_title('COP -Research Sharing Demo')
    window.present()
		
    node.joinNetwork(knownNodes)
    twisted.internet.reactor.run()
    
    



class FileServer(Protocol):
    def dataReceived(self, data):
        
        request = data.strip()
        for entry in os.walk(self.factory.sharePath):
            for filename in entry[2]:
                if filename == request:
                    fullPath = '%s/%s' % (entry[0], filename)
                    f = open(fullPath, 'r')
                    buf = f.read()
                    self.transport.write(buf)
                    f.close()
                    break
        self.transport.loseConnection()

class FileGetter(Protocol):
    def connectionMade(self):
        self.buffer = ''
        self.filename = ''
        
    def requestFile(self, filename, guiWindow):
        self.window = guiWindow
        self.filename = filename
        self.transport.write('%s\r\n' % filename)

    def dataReceived(self, data):
        self.buffer += data
    
    def connectionLost(self, reason):
        if len(self.buffer) == 0:
             dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                        "An error occurred; file could not be retrieved.")
             dialog.run()
             dialog.destroy()
             return
     
        fd = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                   buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        fd.set_default_response(gtk.RESPONSE_OK)
        fd.set_current_name(self.filename)
        response = fd.run()
        if response == gtk.RESPONSE_OK:
            destfilename = fd.get_filename()
            f = open(destfilename, 'w')
            f.write(self.buffer)
            f.close()
        fd.destroy()


class FileShareWindow(gtk.Window):
    def __init__(self, node,port,groups,name,eid,guest):
        gtk.Window.__init__(self)
        
        self.set_default_size(800, 600)
        
        self.trayIcon = gtk.status_icon_new_from_stock(gtk.STOCK_FIND)
        self.trayIcon.connect('popup-menu', self._trayIconRightClick)
        self.trayIcon.connect('activate', self._trayIconClick)
        
        self.node = node
        self.groups = groups
        
        self.connect("delete-event", self._hideWindow)
        
        # Layout the window
        highLevelVbox = gtk.VBox(spacing=3)
        self.add(highLevelVbox)
        highLevelVbox.show()
        
        notebook = gtk.Notebook()
        notebook.set_tab_pos(pos=gtk.POS_TOP)
        notebook.show()
        highLevelVbox.pack_start(notebook,expand=True, fill=True)
        
        ###USER INFO
        hbox2 = gtk.HBox(spacing=3)
        hbox2.show()
        
        notebook.append_page(hbox2, gtk.Label('User Information'))
        
        vbox = gtk.VBox(spacing=3)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)
        self.userList = gtk.TreeStore(str)
        
        # Create tree view
        self.dTV = gtk.TreeView(gtk.TreeStore(str))
        self.dTV.set_rules_hint(True)
        self.dTV.set_search_column(0)
        #self.dTV.connect('row-activated', self.downloadFile)
        sw.add(self.dTV)
        column = gtk.TreeViewColumn('Current Online Users:', gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.dTV.append_column(column)
        self.dTV.set_reorderable(True)
        self.dTV.set_show_expanders(False)
        self.dTV.set_level_indentation(10)
        
        vbox.show()
        hbox2.pack_start(vbox, expand=True, fill=True)
        
        
        
        vbox = gtk.VBox(spacing=3)       
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        if(guest):
            g='YES'
        else:
            g='NO'
        frame = gtk.Frame("Currently Logged User:")
        label = gtk.Label("Name:\t"+name+"\nEmail:\t"+eid+"\nGuest Login:\t"+g)        
        labelgrp = gtk.Label("Groups:\t"+self.groups)
        vboxLabel = gtk.VBox(spacing=3)
        vboxLabel.pack_start(label,expand=False, fill=False)
        vboxLabel.pack_start(labelgrp,expand=False, fill=False)
        hbox.pack_start(frame, expand=True, fill=True)
        label.show()  
        labelgrp.show()
        frame.add(vboxLabel)
        vboxLabel .show()
        frame.show()
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        aGrpTxt = gtk.Entry()
        hbox.pack_start(aGrpTxt, expand=True, fill=True)
        aGrpTxt.show()
        aGrpBtn = gtk.Button('Add Group(s)')
        hbox.pack_start(aGrpBtn, expand=True, fill=True)
        
        
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()
        dGrpTxt = gtk.Entry()
        hbox.pack_start(dGrpTxt, expand=True, fill=True)
        dGrpTxt.show()
        dGrpBtn = gtk.Button('Delete Group')
        hbox.pack_start(dGrpBtn, expand=True, fill=True)
        vbox.pack_start(hbox,expand=False, fill=False)
        
        hbox = gtk.HBox(False, 5)
        hbox.show()  
        #chat logs todo        
        frame = gtk.Frame('Chat Logs')
        textview = gtk.TextView()
        frame.add(textview)
        textview.set_editable(False)
        textbuffer = textview.get_buffer()
        textbuffer.set_text('Chat Log Todo')
        hbox.pack_start(frame, expand=True, fill=True)
        textview.show()
        frame.show()
        vbox.pack_start(hbox)
        
        vbox.show()
        hbox2.pack_start(vbox, expand=True, fill=True)
        
        
        
        ###search info
        vbox = gtk.VBox(spacing=3)
        vbox.show()
        
        notebook.append_page(vbox, gtk.Label('Search P2P Network'))

        
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)
        # Create tree model
        model = self.createListStore([])
        self.actualModel = []
        # Create tree view
        self.dhtTreeView = gtk.TreeView(model)
        self.dhtTreeView.set_rules_hint(True)
        self.dhtTreeView.set_search_column(0)
        self.dhtTreeView.connect('row-activated', self.downloadFile)
        # Add the tree view to the scrolling window
        sw.add(self.dhtTreeView)
        # column for file name/description
        column = gtk.TreeViewColumn('File list:', gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.dhtTreeView.append_column(column)
	#column = gtk.TreeViewColumn('Associated Group:', gtk.CellRendererText(), text=0)
        #column.set_sort_column_id(1)
        #self.dhtTreeView.append_column(column)

        # Add the controls
        # Search for keyword
        hbox = gtk.HBox(False, 5)
        hbox.show()
        label = gtk.Label("Smart Search:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        entryKeyword = gtk.Entry()
        hbox.pack_start(entryKeyword, expand=True, fill=True)
        entryKeyword.show()
		
	
        labelGrp = gtk.Label("in Group:")
        hbox.pack_start(labelGrp, False, False, 0)
        labelGrp.show()
        entryKeywordGrp = gtk.Entry()
        hbox.pack_start(entryKeywordGrp, expand=True, fill=True)
        entryKeywordGrp.set_text(self.groups)
        print groups
        entryKeywordGrp.show()
        
        button = gtk.Button('Search')
        hbox.pack_start(button, expand=False, fill=False)
        button.connect("clicked", self.search, entryKeyword, entryKeywordGrp)
        button.show()
        
        self.progressBar = gtk.ProgressBar()
        self.progressBar.show()
        hbox.pack_start(self.progressBar, expand=True, fill=True)
        self.progressBar.show()
        
        vbox.pack_start(hbox,expand=False, fill=False)
	#vbox.pack_start(hboxGrp, expand=False, fill=False)
        
        
        ######### Publish data
        vbox = gtk.VBox(spacing=3)
        vbox.show()
        notebook.append_page(vbox, gtk.Label('Share Local Files'))
        
        
        # List view
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)
        model = self.createListStore([])
        self.localTreeView = gtk.TreeView(model)
        self.localTreeView.set_rules_hint(True)
        self.localTreeView.set_search_column(0)
        self.localTreeView.connect('row-activated', self.downloadFile)
        sw.add(self.localTreeView)
        column = gtk.TreeViewColumn('Shared Files:', gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.localTreeView.append_column(column)
        
        
        hbox = gtk.HBox(False, 8)
        hbox.show()
        label = gtk.Label("Share directory:")
        hbox.pack_start(label, False, False, 0)
        label.show()
        self.entryDir = gtk.Entry()
        hbox.pack_start(self.entryDir, expand=True, fill=True)
        self.entryDir.show()
        '''
        labelGrp = gtk.Label("Publisher Group:")
        hbox.pack_start(labelGrp, False, False, 0)
        labelGrp.show()
        '''
        entryKeywordGrp2 = gtk.Entry()
        '''
        hbox.pack_start(entryKeywordGrp2, expand=True, fill=True)
        entryKeywordGrp2.show()
        '''
        entryKeywordGrp2.set_text(self.groups)
        
        button = gtk.Button('Browse')
        hbox.pack_start(button, expand=False, fill=False)
        button.connect("clicked", self.browseDirectory, self.entryDir.get_text)
        button.show()
        button = gtk.Button('Publish')
        hbox.pack_start(button, expand=False, fill=False)
        
        
            
	
        button.connect("clicked", self.publishDirectory, self.entryDir.get_text, entryKeywordGrp2,(not guest))
        button.show()
        vbox.pack_start(hbox, expand=False, fill=False)
        
        aGrpBtn.connect("clicked",self.addGroup,aGrpTxt,entryKeywordGrp2,entryKeywordGrp,labelgrp)
        aGrpBtn.show()
        dGrpBtn.connect("clicked",self.delGroup,dGrpTxt,entryKeywordGrp2,entryKeywordGrp,labelgrp)
        dGrpBtn.show()
        
        

        self._setupTCPNetworking(port)
        if(not guest):
            self.publishOldFiles(entryKeywordGrp2)

        #no longer used
        #df = self.node.publishData(name+':us3rn@me:'+self.groups.replace(',',':'),self.node.id)
        #df.addCallback(self.updateUsers)
        
        self.publishMyself(name,eid)
        gobject.timeout_add(5000, self.updateUsers)
        self.show_all()
        
        

        
    def publishMyself(self,name,eid):
        for g in self.groups.split(','):
            g='GlobalGroup'+g
            df=self.node.iterativeFindValue(getID(g))
            def res(r):
                if type(r) is list:
                    self.node.iterativeStore(getID(g),name+','+eid)
                else:
                    self.node.iterativeStore(getID(g),r[getID(g)]+','+name+','+eid)
            df.addCallback(res)
        
        
    def test2(self,k):
        d=self.node.iterativeFindValue(getID(k))
        def res(r):
            if type(r) is list:
                print 'not there'
            else:
                print r
        d.addCallback(res)
        
    
    def updateUsers(self,result=None):
        model = gtk.TreeStore(str)
        self.userList =None
        self.userList = gtk.TreeStore(str)
        for grp in self.groups.split(','):
            row = model.append(None,['Group Name: %s' % grp])
            row2 = self.userList.append(None,['Group Name: %s' % grp])
            g='GlobalGroup'+grp
            df=self.node.iterativeFindValue(getID(g))
            def gotValue(res):
                if (not (type(res) is list)):
                    print res
                    result = res[getID(g)].split(',')
                    for i in xrange(0,len(result),2):
                            model.append(row,[result[i]])
                            self.userList.append(row2,[result[i]+','+result[i+1]])
                    self.dTV.set_model(model)
                    self.dTV.expand_all()     
                        
                
            def error(failure):
                print 'GUI: an error occurred:', failure.getErrorMessage()
                            
            df.addCallback(gotValue)
            df.addErrback(error)
        print 'updated'
        return True
        
        
            
    def main(self):
        gtk.main()
    
    
    def addGroup(self,sender,txt,entryKeywordGrp2,entryKeywordGrp,labelgrp):
        self.groups= self.groups +','+txt.get_text()
        txt.set_text('')
        entryKeywordGrp2.set_text(self.groups)
        entryKeywordGrp.set_text(self.groups)
        labelgrp.set_text("Groups:\t"+self.groups)
    
    def delGroup(self,sender,txt,entryKeywordGrp2,entryKeywordGrp,labelgrp):
        grps= self.groups.split(',')
        grps.remove(txt.get_text())        
        self.groups= ','.join(grps)
        txt.set_text('')
        entryKeywordGrp2.set_text(self.groups)
        entryKeywordGrp.set_text(self.groups)
        labelgrp.set_text("Groups:\t"+self.groups)
    
    def publishOldFiles(self,entryKeywordGrp2):
        #publish old files
        try:
            recFile= open('record','r')
            paths = recFile.readlines()
            for p in paths:
                self.entryDir.set_text(p.split(':')[0])
                entryKeywordGrp2.set_text(':'.join(p.split(':')[1:]))
                self.publishDirectory(self, self.entryDir.get_text, entryKeywordGrp2, False)
            self.entryDir.set_text('')
            entryKeywordGrp2.set_text(self.groups)
            recFile.close()
        except IOError:
            recFile= open('record','w')
            recFile.close() 

    def _showTrayIconMenu(self, event_button, event_time, icon):
        menu = gtk.Menu()
        if not self.get_property('visible'):
            showItem = gtk.MenuItem('Show main window')
            showItem.connect('activate', self._trayIconClick)
            showItem.show()
            menu.append(showItem)
        item = gtk.MenuItem('Quit')
        item.connect('activate', gtk.main_quit)
        item.show()
        menu.append(item)
        menu.popup(None, None, gtk.status_icon_position_menu, event_button,event_time, icon)

    def _trayIconRightClick(self, icon, event_button, event_time):
        self._showTrayIconMenu(event_button, event_time, icon)

    def _trayIconClick(self, icon):
        if self.get_property('visible'):
            self.hide_all()
        else:
            self.show_all()
            

    def _hideWindow(self, *args):
        self.hide_all()
        return True

    def _setupTCPNetworking(self,port):
        # Next lines are magic:
        self.factory = ServerFactory()
        self.factory.protocol = FileServer
        self.factory.sharePath = '.'
        print 'port2',port
        twisted.internet.reactor.listenTCP(int(port), self.factory)


    def createListStore(self, data):
        lstore = gtk.ListStore(gobject.TYPE_STRING)
        for item in data:
            iter = lstore.append()
            lstore.set(iter, 0, item)
        return lstore
    
    def search(self, sender, entryKeyword,entryKeywordGrp):
        sender.set_sensitive(False)
        keyword = entryKeyword.get_text()
        #setting nullset as a subset of all sets
        Pgroup = entryKeywordGrp.get_text().replace(',',':')
        if Pgroup == '':
            group = set()
        else:
            group = set(Pgroup.split(':'))
                
	#group = set(entryKeywordGrp.get_text().split(','))
	entryKeywordGrp.set_sensitive(False)
	print(group)
        entryKeyword.set_sensitive(False)
        def gotValue(result):
            sender.set_sensitive(True)
            result2=[] #for storing filetered via group with tags
            result3 = [] # for storing filtered via group without tags
            self.actualModel = []
            entryKeywordGrp.set_sensitive(True)
            entryKeyword.set_sensitive(True)
            print 'result',result
            for x in result:
                tags = set (x.split(':')[1:])
                if group <= tags:
                    result2.append(x)             
                    result3.append(x.split(':')[0])
			
            self.actualModel = self.createListStore(result2)
            model2 = self.createListStore(result3)
			
            self.dhtTreeView.set_model(model2)
        def error(failure):
            print 'GUI: an error occurred:', failure.getErrorMessage()
            sender.set_sensitive(True)
            entryKeywordGrp.set_sensitive(True)
            entryKeyword.set_sensitive(True)
						
        df = self.node.searchForKeywords(keyword)
        df.addCallback(gotValue)
        df.addErrback(error)
    
    def publishDirectory(self, sender, dirPathFunc,pGroup,to_write):
        sender.set_sensitive(False)
        path = dirPathFunc()
        #print path
        files = []
        paths = []
        group = pGroup.get_text().replace(',',':')
        pGroup.set_text(self.groups)
        if (to_write == True ):
            recFile = open('record','a')
            recFile.write(path+':'+group+'\n')
            recFile.close()        
        outerDf = defer.Deferred()
        self.factory.sharePath = path
        for entry in os.walk(path):
            for file in entry[2]:
                if file not in files and file not in ('.directory'):
                    files.append(file)
                    paths.append(entry[0])
        files.sort()
        model = self.localTreeView.get_model()
        
        print 'files: ', len(files)
        def publishNextFile(result=None):
            if len(files) > 0:
                #twisted.internet.reactor.iterate()
                filename = files.pop()
                iter = model.append()
                print '-->',filename
		print '-->',group
                print 'nodes-id',self.node.id
                model.set(iter, 0, '%s/%s' % (paths.pop(), filename))
                #publish data file instead of self.node.id to store files directly on dht
                df = self.node.publishData(filename+':'+group, self.node.id)
                df.addCallback(publishNextFile)
            else:
                print '** done **'
                outerDf.callback(None)
        def completed(result):
            sender.set_sensitive(True)
        publishNextFile()
        outerDf.addCallback(completed)
    
    def browseDirectory(self, sender, dirPathFunc):
        fd = gtk.FileChooserDialog(title='Choose directory to share...', action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        fd.set_default_response(gtk.RESPONSE_OK)
        path = dirPathFunc().strip()
        if len(path):
            fd.set_current_folder(path)
        response = fd.run()
        if response == gtk.RESPONSE_OK:
            self.entryDir.set_text(fd.get_filename())
        fd.destroy()
        
    def downloadFile(self, treeView, path, column):
        #model = treeView.get_model()
        model = self.actualModel
        iter = model.get_iter(path)
        filename = model.get(iter, 0)[0]
	print 'filename ',filename
	
        h = hashlib.sha1()
        h.update(filename)
        key = h.digest()
        
        def getTargetNode(result):
            #print 'result2',result
            targetNodeID = result[key]
            
            print 'targetNodeID',targetNodeID
            df = self.node.findContact(targetNodeID)
            return df
        def getFile(protocol):
            if protocol != None:
                protocol.requestFile(filename.split(':')[0], self)
        def connectToPeer(contact):
            if contact == None:
                print 'key',key
                print 'current id',self.node.id
                dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                        "File could not be retrieved.\nThe host that published this file is no longer on-line.")
                dialog.run()
                dialog.destroy()
            else:
                c = ClientCreator(twisted.internet.reactor, FileGetter)
                df = c.connectTCP(contact.address, contact.port)
                return df
        
        df = self.node.iterativeFindValue(key)
        df.addCallback(getTargetNode)
        df.addCallback(connectToPeer)
        df.addCallback(getFile)
        
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage:\n%s UDP_PORT  [KNOWN_NODE_IP  KNOWN_NODE_PORT]' % sys.argv[0]
        print 'or:\n%s UDP_PORT  [FILE_WITH_KNOWN_NODES]' % sys.argv[0]
        print '\nIf a file is specified, it should containg one IP address and UDP port\nper line, seperated by a space.'
        sys.exit(1)
    try:
        int(sys.argv[1])
    except ValueError:
        print '\nUDP_PORT must be an integer value.\n'
        print 'Usage:\n%s UDP_PORT  [KNOWN_NODE_IP  KNOWN_NODE_PORT]' % sys.argv[0]
        print 'or:\n%s UDP_PORT  [FILE_WITH_KNOWN_NODES]' % sys.argv[0]
        print '\nIf a file is specified, it should contain one IP address and UDP port\nper line, seperated by a space.'
        sys.exit(1)
    
    if len(sys.argv) == 4:
        knownNodes = [(sys.argv[2], int(sys.argv[3]))]
    elif len(sys.argv) == 3:
        knownNodes = []
        f = open(sys.argv[2], 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            ipAddress, udpPort = line.split()
            knownNodes.append((ipAddress, int(udpPort)))
    else:
        knownNodes = None

    try:
        os.makedirs(os.path.expanduser('~')+'/.entangled')
    except OSError:
        pass
    
    #initall(int(sys.argv[1]))
    
    

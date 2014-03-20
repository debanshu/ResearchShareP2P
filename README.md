ResearchShareP2P
================

ResearchShareP2P is an experimental project written in Python which helps facilitate sharing of research data between clients, using a Peer-to-Peer decentralized network.  The application provides support for various features desired by such a system – like partial keyword search, grouping of clients (peers) into specific research groups, searching for clients of a specific group and complete mobility of the 
application.

The backbone of this application is the [EntangledP2P DHT framework](http://entangled.sourceforge.net/) and its file sharing demo.

The application can be started via Start.py

####History
This application was primarily built as an academic project under the guidance of Assistant Professor K.Hari Babu, CSIS Group BITS-Pilani, Pilani Campus; during Jan-May 2013.

####Technical Details
- Dependencies
	- Python 2.6x or above ( NOT Python 3 )
	- PyGTK (for GUI)
	- Entangled Library
	- Twisted ( the underlying networking library )
	- Zope Interface (for Twisted function calls)
	- SqLite Python bindings if using the Database-oriented datastore( in built in python from v2.6+ )
- Application Files
	- Start.py ( the starting connection GUI )
	- researchSharingDemoTest.py (the core application program )
- User Specific Files
	- userdata ( stores the non-guest user data in plaintext )
	- key.bin (stores keys in encrypted format )
	- chat.log ( dummy file for old chat logs )
	- record ( currently shared research files )

####TODO
- Implement chat windows between clients
- Overlay chat connction with possible real-time audio/video collaboration
- Add compatibility with Python 3.

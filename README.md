REQUIREMENTS
===

Database is saved in sqlite3. Python has a builtin module to access it.
    The command line utility of sqlite3 can also be used to acess it more easily.

Currently requires python packages flask, requests, pyinotify, ...
    One method of installation is using pip.

DOCUMENTATION
===

Sprint 1 design document (client-server communication) is CSCommie_design.doc.



Code notes
===

The database has fields (username, password, email, role) Currently, the role field is only "user", but eventually will be "admin" and other fields.

Server and client side communication is via strings. The constants package provides variables TRUE and FALSE that stands for 'true' and 'false'

"""Simple HTTP server based on the asyncore / asynchat framework

Under asyncore, every time a socket is created it enters a table which is
scanned through select calls by the asyncore.loop() function

All events (a client connecting to a server socket, a client sending data, 
a server receiving data) are handled by the instances of classes derived 
from asyncore.dispatcher

Here the server is represented by an instance of the Server class

When a client connects to it, its handle_accept() method creates an
instance of RequestHandler, one for each HTTP request. It is derived
from asynchat.async_chat, a class where incoming data on the connection
is processed when a "terminator" is received. The terminator can be :
- a string : here we'll use the string \r\n\r\n to handle the HTTP request
line and the HTTP headers
- an integer (n) : the data is processed when n bytes have been read. This
will be used for HTTP POST requests

The data is processed by a method called found_terminator. In RequestHandler,
found_terminator is first set to handle_request_line to handle the HTTP
request line (including the decoding of the query string) and the headers. 
If the method is POST, terminator is set to the number of bytes to read
(the content-length header), and found_terminator is set to handle_post_data

After that, the handle_data() method is called and the connection is closed

Subclasses of RequestHandler only have to override the handle_data() method

"""
import asynchat,asyncore,socket,SimpleHTTPServer, select, urllib, urlparse
import posixpath,sys, cgi,cStringIO, os

class socketStream:

    def __init__(self,sock):
        self.sock=sock
        self.closed=1   # compatibility with SocketServer
    
    def write(self,data):
        self.sock.send(data)

class RequestHandler(asynchat.async_chat,
    SimpleHTTPServer.SimpleHTTPRequestHandler):

    def __init__(self,conn,addr,server):
        asynchat.async_chat.__init__(self,conn)
        self.client_address=addr
        self.connection=conn
        self.server=server
        self.wfile=socketStream(self.socket)
        # sets the terminator : when it is received, this means that the
        # http request is complete ; control will be passed to
        # self.found_terminator
        self.set_terminator ('\r\n\r\n')
        self.buffer=cStringIO.StringIO()
        self.found_terminator=self.handle_request_line

    def collect_incoming_data(self,data):
        """Collects the data arriving on the connexion"""
        self.buffer.write(data)

    def prepare_POST(self):
        """Prepare to read the request body"""
        bytesToRead = int(self.headers.getheader('content-length'))
        # set terminator to length (will read bytesToRead bytes)
        self.set_terminator(bytesToRead)
        self.buffer=cStringIO.StringIO()
        # control will be passed to a new found_terminator
        self.found_terminator=self.handle_post_data
    
    def handle_post_data(self):
        """Called when a POST request body has been read"""
        self.rfile=cStringIO.StringIO(self.buffer.getvalue())
        self.do_POST()
        self.finish()
            
    def do_GET(self):
        """Begins serving a GET request"""
        # nothing more to do before handle_data()
        self.handle_data()
        
    def do_POST(self):
        """Begins serving a POST request. The request data must be readable
        on a file-like object called self.rfile"""
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        length = int(self.headers.getheader('content-length'))
        if ctype == 'multipart/form-data':
            query=cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            qs=self.rfile.read(length)
            query=cgi.parse_qs(qs, keep_blank_values=1)
        else:
            query = ''                   # Unknown content-type
        # some browsers send 2 more bytes...
        [ready_to_read,x,y]=select.select([self.connection],[],[],0)
        if ready_to_read:
            self.rfile.read(2)

        self.QUERY.update(self.query(query))
        self.handle_data()

    def query(self,parsedQuery):
        """Returns the QUERY dictionary, similar to the result of cgi.parse_qs
        except that :
        - if the key ends with [], returns the value (a Python list)
        - if not, returns a string, empty if the list is empty, or with the
        first value in the list"""
        res={}
        for item in parsedQuery.keys():
            value=parsedQuery[item] # a Python list
            if item.endswith("[]"):
                res[item[:-2]]=value
            else:
                if len(value)==0:
                    res[item]=''
                else:
                    res[item]=value[0]
        return res

    def handle_data(self):
        """Class to override"""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)

    def handle_request_line(self):
        """Called when the http request line and headers have been received"""

        # prepare attributes needed in parse_request()
        self.rfile=cStringIO.StringIO(self.buffer.getvalue())
        self.raw_requestline=self.rfile.readline()
        self.parse_request()

        # if there is a Query String, decodes it in a QUERY dictionary
        self.path_without_qs,self.qs=self.path,''
        if self.path.find('?')>=0:
            self.qs=self.path[self.path.find('?')+1:]
            self.path_without_qs=self.path[:self.path.find('?')]
        self.QUERY=self.query(cgi.parse_qs(self.qs,1))

        if self.command in ['GET','HEAD']:
            # if method is GET or HEAD, call do_GET or do_HEAD and finish
            method="do_"+self.command
            if hasattr(self,method):
                getattr(self,method)()
                self.finish()
        elif self.command=="POST":
            # if method is POST, call prepare_POST, don't finish before
            self.prepare_POST()
        else:
            self.send_error(501, "Unsupported method (%s)" %self.command)

    def list_directory(self, path):
        """Override SimpleHTTPServer method for subdirectories"""
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(lambda a, b: cmp(a.lower(), b.lower()))
        f = cStringIO.StringIO()
        f.write("<title>Directory listing for %s</title>\n" % self.path)
        f.write("<h2>Directory listing for %s</h2>\n" % self.path)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = cgi.escape(name)
            linkname=cgi.escape(urlparse.urljoin(self.path,name))
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n' % (linkname, displayname))
        f.write("</ul>\n<hr>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def finish(self):
        """Reset terminator (required after POST method), then close"""
        self.set_terminator ('\r\n\r\n')
        self.close()

class Server(asyncore.dispatcher):
    """Copied from http_server in medusa"""
    def __init__ (self, ip, port,handler):
        self.ip = ip
        self.port = port
        self.handler=handler
        asyncore.dispatcher.__init__ (self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)

        self.set_reuse_addr()
        self.bind ((ip, port))

        # lower this to 5 if your OS complains
        self.listen (1024)

    def handle_accept (self):
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info ('warning: server accept() threw an exception', 'warning')
            return
        except TypeError:
            self.log_info ('warning: server accept() threw EWOULDBLOCK', 'warning')
            return
        # creates an instance of the handler class to handle the request/response
        # on the incoming connexion
        self.handler(conn,addr,self)

if __name__=="__main__":
    # launch the server on port 8080
    s=Server('',8080,RequestHandler)
    print "SimpleAsyncHTTPServer running on port 8080"
    asyncore.loop()


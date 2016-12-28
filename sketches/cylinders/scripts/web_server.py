import logging, threading, time, socket, os
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from evento import Event

def createRequestHandler(event_manager = None, requestEvent = None, _options = {}):
    class CustomHandler(SimpleHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            # do_stuff_with(self, init_args)
            self.options = _options
            self.root_path = self.options['serve'] if 'serve' in _options else '.'
            self.event_manager = event_manager
            self.requestEvent = requestEvent
            super(CustomHandler, self).__init__(*args, **kwargs)


        def process_request(self):
            result = False
            if self.event_manager != None and 'output_events' in self.options:
                if self.path in self.options['output_events']:
                    self.event_manager.fire(self.options['output_events'][self.path])
                    result = True

            if 'responses' in self.options and self.path in self.options['responses']:
                self.wfile.write(self.options['responses'][self.path])
                # self.wfile.close()
                result = True
            elif result == True:
                self.send_response(200)
                self.end_headers()

            if self.requestEvent:
                self.requestEvent(self)

            return result

        def do_HEAD(self):
            try:
                if self.process_request():
                    return
                super(CustomHandler, self).do_HEAD()
            except:
                pass

        def do_GET(self):
            try:
                if self.process_request():
                    return
                super(CustomHandler, self).do_GET()
            except:
                pass

        def do_POST(self):
            try:
                if self.process_request():
                    return
                super(CustomHandler, self).do_POST()
            except:
                pass

        def translate_path(self, path):
            if self.event_manager != None and 'output_events' in self.options:
                if path in self.options['output_events']:
                    self.event_manager.fire(self.options['output_events'][path])
                    # self.send_error(204)
                    self.send_response(200)
                    self.wfile.write('OK')
                    self.wfile.close()
                    return ''

            relative_path = path[1:] if path.startswith('/') else path
            # if relative_path == '' or relative_path.endswith('index.html'):
            return SimpleHTTPRequestHandler.translate_path(self, os.path.join(self.root_path, relative_path))

        # cleanup log
        def log_request(self, *args, **kwargs):
            pass

        def log_error(self, *args, **kwargs):
            pass

    return CustomHandler

class WebServer(threading.Thread):
    def __init__(self, options = {}):
        threading.Thread.__init__(self)
        self.options = options
        self.http_server = None
        self.event_manager = None
        self.threading_event = None
        self.daemon=True

        # attributes
        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        self.requestEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        self.event_manager = event_manager
        self.logger.debug("Starting http server thread")
        self.threading_event = threading.Event()
        self.threading_event.set()
        self.start() # start thread

    def destroy(self):
        self.event_manager = None

        if not self.isAlive():
            return

        if self.http_server:
            self.http_server.socket.close()

        self.threading_event.clear()

        try:
            with urllib.request.urlopen('http://127.0.0.1:{0}'.format(self.port())) as f:
                f.read()
        except urllib.error.URLError:
            pass
        # self.logger.debug('Sending dummy HTTP request to stop HTTP server from blocking...')
        # try:
        #     connection = httplib.HTTPConnection('127.0.0.1', self.port())
        #     connection.request('HEAD', '/')
        #     connection.getresponse()
        # except socket.error:
        #     pass

        self.join()

    # thread function
    def run(self):
        self.logger.warning('Starting HTTP server on port {0}'.format(self.port()))
        HandlerClass = createRequestHandler(self.event_manager, self.requestEvent, self.options)
        # self.http_server = HTTPServer(('', self.port()), HandlerClass)
        self.http_server = HTTPServer(('', self.port()), HandlerClass)

        # # self.httpd.serve_forever()
        # # self.httpd.server_activate()
        # while self.threading_event.is_set(): #not self.kill:
        #     try:
        #         self.http_server.handle_request()
        #     except Exception as exc:
        #         print('http exception:')
        #         print(exc)
        try:
            self.http_server.serve_forever()
        except:
            pass

        print('http server closed')

        self.logger.warning('Closing HTTP server at port {0}'.format(self.port()))
        self.http_server.server_close()
        self.http_server = None

    def port(self):
        return self.options['port'] if 'port' in self.options else 2031

# for testing
if __name__ == '__main__':
    logging.basicConfig()
    ws = WebServer({'verbose': True, 'serve': 'examples'})
    try:
        ws.setup()
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt. Quitting.')

    ws.destroy()

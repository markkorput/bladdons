import logging, threading, os, urllib.request, re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from evento import Event

def createRequestHandlerClass(folder='.', requestEvent=Event(), fileNotFoundRequestEvent=Event(), custom_handlers=[]):
    class CustomHandler(SimpleHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            # do_stuff_with(self, init_args)
            self.root_path = folder
            self.requestEvent = requestEvent
            self.fileNotFoundRequestEvent = fileNotFoundRequestEvent
            self.custom_handlers = custom_handlers
            self.compiled_handlers = list(map(lambda x: [re.compile(x[0]), x[1]], custom_handlers))
            self._handled = False
            super(CustomHandler, self).__init__(*args, **kwargs)

        def do_HEAD(self):
            print('HEAD request')
            print(self)

        def do_GET(self):
            for regex, handler in self.compiled_handlers:
                match = regex.findall(self.path)
                if len(match) == 1:
                    handler(self, *match[0])
                    if self.get_handled():
                        return

            # notify listeners about request and give them a chance to process the request
            self.requestEvent(self)

            # if any of the listeners marked the request as handled, we're done
            if self.get_handled():
                return

            file_path = self.translate_path(self.path)

            if os.path.isfile(file_path):
                # if the request path matches with any of the local files in the public folder,
                # simply let SimpleHTTPRequestHandler serve that file
                return super(CustomHandler, self).do_GET()

            # trigger file not found request event and give listeners a chance to handle the request
            fileNotFoundRequestEvent(self)

            # again, if any of the listeners marked the request as handled, we're done
            if self.get_handled():
                return

            # let the original handler respond with a 404
            return super(CustomHandler, self).do_GET()

        def do_POST(self):
            print('POST REQUEST')
            print(self)

        def translate_path(self, path):
            # we only provide acces into the specified folder, so turn ay absolute path into a relative path
            relative_path = path[1:] if path.startswith('/') else path
            full_path = os.path.join(self.root_path, relative_path)
            return SimpleHTTPRequestHandler.translate_path(self, full_path)

        def get_handled(self):
            return self._handled

        def set_handled(self, value=True):
            self._handled = value

        def respond_ok(self):
            self.send_response(200)
            self.end_headers()
            self.set_handled()
            # self.wfile.write(self.options['responses'][self.path])

        # cleanup log
        def log_request(self, *args, **kwargs):
            pass

        def log_error(self, *args, **kwargs):
            pass

    return CustomHandler

class WebServer(threading.Thread):
    def __init__(self, verbose=False, folder='.', port=2031):
        threading.Thread.__init__(self)
        self.folder = folder
        self.port = port
        self.http_server = None

        # attributes
        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)

        self.requestEvent = Event()
        self.fileNotFoundRequestEvent = Event()
        self._added_handlers = []

    def __del__(self):
        self.destroy()

    def setup(self):
        self.logger.debug("Starting http server thread")
        self.start() # start thread

    def destroy(self):
        if not self.isAlive():
            return

        if self.http_server:
            self.http_server.socket.close()

        # wait until server thread finishes
        self.join()

    # thread function
    def run(self):
        self.logger.warning('Starting HTTP server on port {0}'.format(self.port))
        HandlerClass = createRequestHandlerClass(folder=self.folder, requestEvent=self.requestEvent, fileNotFoundRequestEvent=self.fileNotFoundRequestEvent, custom_handlers=self._added_handlers)

        # self.http_server = HTTPServer(('', self.port, HandlerClass)
        self.http_server = HTTPServer(('', self.port), HandlerClass)

        try:
            self.http_server.serve_forever()
        except OSError as err:
            # OSError #9 ("Bad file descriptor") is caused by closing of the socket,
            # which is our way of shutting down the HTTP server
            if err.errno != 9:
                self.logger.error(err)
        except ValueError:
            pass

        self.logger.warning('Closing HTTP server at port {0}'.format(self.port))
        self.http_server.server_close()
        self.http_server = None

    def add_handler(self, pattern, handler):
        self._added_handlers.append((pattern, handler))

    def clear_handlers(self):
        self._added_handlers.clear()

# for testing
if __name__ == '__main__':
    import time

    logging.basicConfig()
    ws = WebServer(verbose=True, folder='examples')
    try:
        ws.setup()
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt. Quitting.')

    ws.destroy()

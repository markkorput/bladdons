import logging, re, math
from .web_server import WebServer

class HttpRot:
    def __init__(self, verbose=False, wwwFolder='scripts/www/'):
        self.logger = logging.getLogger(__name__)
        if verbose:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

        self.web_server = WebServer({
            'verbose': verbose,
            'serve': wwwFolder})

        self.rotation = [0.0,0.0,0.0]

    def __del__(self):
        self.destroy()

    def setup(self):
        self.web_server.setup()
        self.web_server.requestEvent += self._onRequest

    def destroy(self):
        self.web_server.destroy()

        if self._onRequest in self.web_server.requestEvent:
            self.web_server.requestEvent -= self._onRequest

    def _onRequest(self, handler):
        result = re.compile('^\/rot/(.+)\/(.+)\/(.+)$').findall(handler.path)
        if len(result) != 1 or len(result[0]) != 3:
            return

        try:
            a = float(result[0][0])
        except:
            a = 0.0

        try:
            b = float(result[0][1])
        except:
            b = 0.0

        try:
            c = float(result[0][2])
        except:
            c = 0.0

        self.logger.debug('Got orientation data from HTTP-server: {0}, {1}, {2}'.format(a,b,c))
        # self.orientator.localOrientation = [math.radians(c),math.radians(-b),math.radians(a)]
        self.rotation = [math.radians(c),math.radians(-b),math.radians(a)]

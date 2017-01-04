import logging, re, math
from .web_server import WebServer
from .anim import Anim

class HttpRot:
    def __init__(self, verbose=False, wwwFolder='scripts/www/'):
        self.logger = logging.getLogger(__name__)
        if verbose:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

        self.web_server = WebServer(verbose=verbose, folder=wwwFolder)
        self.rotation = [0.0,0.0,0.0]
        self.anim = Anim(0.1)
        self.anim._from = self.rotation
        self.anim._to = self.rotation
        self._queued_args = None

    def __del__(self):
        self.destroy()

    def setup(self):
        # self.web_server.add_handler('^/rot/(-{0,1}\d*\.{0,1}\d*)/(-{0,1}\d*\.{0,1}\d*)/(-{0,1}\d*\.{0,1}\d*)$', self._onRot)
        self.web_server.add_handler('^/rot/.+$', self._onRot)
        self.web_server.setup()

    def update(self):
        if self._queued_args:
            self.anim._from = self.rotation

            values = None
            try:
                values = list(map(lambda x: math.radians(float(x)), self._queued_args))
            except Exception as err:
                self.logger.warning('Invalid rotation value(s): {0}'.format(self._queued_args))
                values = [0.0,0.0,0.0]

            values[1] = -values[1]
            # self.logger.debug('Got orientation data from HTTP-server: {0}'.format(values))
            self.anim._from = self.rotation
            self.anim._to = values
            self.anim.start()
            self._queued_args = None

        if self.anim.active:
            self.anim.update()
            self.rotation = [
                self.anim._from[0] + (self.anim._to[0]-self.anim._from[0]) * self.anim.progress,
                self.anim._from[1] + (self.anim._to[1]-self.anim._from[1]) * self.anim.progress,
                self.anim._from[2] + (self.anim._to[2]-self.anim._from[2]) * self.anim.progress]

    def destroy(self):
        self.web_server.clear_handlers()
        self.web_server.destroy()

    def _onRot(self, handler, *args):
        parts = handler.path.split('/')
        if len(parts) >= 5:
            self._queued_args = (parts[4], parts[3], parts[2])
        handler.respond_ok()

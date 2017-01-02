import logging, re, math
from .web_server import WebServer
from .anim import Anim, Manager

class HttpRot:
    def __init__(self, verbose=False, wwwFolder='scripts/www/'):
        self.logger = logging.getLogger(__name__)
        if verbose:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

        self.web_server = WebServer(verbose=verbose, folder=wwwFolder)
        self.rotation = [0.0,0.0,0.0]
        self.anim_manager = Manager(removeFinished=False, verbose=verbose)
        self.anim = Anim(0.05)
        self.anim._from = self.rotation
        self.anim._to = self.rotation
        self.anim_manager.add(self.anim)
        self.queued_args = None

    def __del__(self):
        self.destroy()

    def setup(self):
        # self.web_server.add_handler('^/rot/(-{0,1}\d*\.{0,1}\d*)/(-{0,1}\d*\.{0,1}\d*)/(-{0,1}\d*\.{0,1}\d*)$', self._onRot)
        self.web_server.add_handler('^/rot/.+$', self._onRot)
        self.web_server.setup()

    def update(self):
        if self.queued_args:
            self.anim._from = self.rotation

            values = None
            try:
                values = list(map(lambda x: math.radians(x), self.queued_args))
            except:
                values = None

            if values == None or len(values) != 3:
                print('Invalid rotation value(s): {0}'.format(self.queued_args))
            else:
                self.logger.warning('Got orientation data from HTTP-server: {0}'.format(values))
                self.anim._to = values
                self.anim.start()

            self.queued_args = None

        self.anim_manager.update()
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
            self.queued_args = (parts[2], parts[3], parts[4])
        handler.respond_ok()

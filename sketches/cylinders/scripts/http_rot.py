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
        anim = Anim(0.05)
        anim._from = self.rotation
        anim._to = self.rotation
        self.anim_manager.add(anim)

    def __del__(self):
        self.destroy()

    def setup(self):
        # self.web_server.add_handler('^/rot/(-{0,1}\d*\.{0,1}\d*)/(-{0,1}\d*\.{0,1}\d*)/(-{0,1}\d*\.{0,1}\d*)$', self._onRot)
        self.web_server.add_handler('^/rot/(.+)/(.+)/(.+)$', self._onRot)
        self.web_server.setup()

    def update(self):
        self.anim_manager.update()

        anim = self.anim_manager.anims[0]
        self.rotation = [
            anim._from[0] + (anim._to[0]-anim._from[0]) * anim.progress,
            anim._from[1] + (anim._to[1]-anim._from[1]) * anim.progress,
            anim._from[2] + (anim._to[2]-anim._from[2]) * anim.progress]

    def destroy(self):
        self.web_server.clear_handlers()
        self.web_server.destroy()

    def _onRot(self, handler, *args):
        handler.respond_ok()
        anim = self.anim_manager.anims[0]
        anim._from = self.rotation
        values = map(lambda x: float(x), args)

        try:
            values = list(map(lambda x: math.radians(x), values))
        except:
            print('Invalid rotation value(s): {0}'.format(args))
            return

        self.logger.debug('Got orientation data from HTTP-server: {0}'.format(values))
        anim._to = values
        anim.start()

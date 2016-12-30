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
        self.web_server.setup()
        self.web_server.fileNotFoundRequestEvent += self._onFileNotFoundRequest

    def update(self):
        self.anim_manager.update()

        anim = self.anim_manager.anims[0]
        self.rotation = [
            anim._from[0] + (anim._to[0]-anim._from[0]) * anim.progress,
            anim._from[1] + (anim._to[1]-anim._from[1]) * anim.progress,
            anim._from[2] + (anim._to[2]-anim._from[2]) * anim.progress]

    def destroy(self):
        self.web_server.destroy()

        if self._onFileNotFoundRequest in self.web_server.fileNotFoundRequestEvent:
            self.web_server.fileNotFoundRequestEvent -= self._onFileNotFoundRequest

    def _onFileNotFoundRequest(self, handler):
        result = re.compile('^\/rot/(.+)\/(.+)\/(.+)$').findall(handler.path)

        if len(result) != 1 or len(result[0]) != 3:
            return

        handler.respond_ok()

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
        # self.rotation = [math.radians(c),math.radians(-b),math.radians(a)]
        anim = self.anim_manager.anims[0]
        anim._from = self.rotation
        anim._to = [math.radians(c),math.radians(-b),math.radians(a)]
        anim.start()

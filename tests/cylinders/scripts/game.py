import logging, bge, bpy, re, math
from .ui import Ui
from .web_server import WebServer
from .spawner import Spawner

def setup(controller):
    Game.for_owner(controller.owner).setup()

def update(controller):
    Game.for_owner(controller.owner).update()

class Game:
    _instances_by_owner = {}

    @classmethod
    def for_owner(cls, owner):
        if owner in cls._instances_by_owner:
            return cls._instances_by_owner[owner]

        # Create new instance
        instance = cls(owner)
        # Store it so it can be found next time
        cls._instances_by_owner[owner] = instance
        return instance

    def __init__(self, owner):
        self.owner = owner

        verbose = 'verbose' in self.owner and self.owner['verbose']
        self.logger = logging.getLogger(__name__)
        if verbose:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

        self.ui = Ui.singleton(verbose=verbose)
        self.spawner = Spawner(verbose=verbose)

        self.web_server = WebServer({
            'verbose': verbose,
            'serve': 'scripts/www/'})

    def __del__(self):
        self.destroy()

    def setup(self):
        self.ui.setup()
        self.web_server.setup()
        self.spawner.setup(logicObject=self.owner)

        self.web_server.requestEvent += self._onRequest
        bpy.app.handlers.game_post.append(self._onGameEnded)

    def _onGameEnded(self, scene):
        self.destroy()

    def destroy(self):
        self.spawner.destroy()
        self.web_server.destroy()

        if self._onRequest in self.web_server.requestEvent:
            self.web_server.requestEvent -= self._onRequest

        if self._onGameEnded in bpy.app.handlers.game_post:
            bpy.app.handlers.game_post.remove(self._onGameEnded)

    def update(self):
        self.ui.update()
        self.spawner.update()
        self.spawner.spawn()

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
        self.spawner.rotation = [math.radians(c),math.radians(-b),math.radians(a)]

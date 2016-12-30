import logging, bpy
from .ui import Ui
from .spawner import Spawner
from .http_rot import HttpRot

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
            self.logger.setLevel(logging.DEBUG)

        self.ui = Ui.singleton(verbose=verbose)
        self.spawner = Spawner(verbose=verbose)
        self.http_rot = HttpRot()

    def __del__(self):
        self.destroy()

    def setup(self):
        self.ui.setup()
        self.http_rot.setup()
        self.spawner.setup(logicObject=self.owner)
        bpy.app.handlers.game_post.append(self._onGameEnded)

    def _onGameEnded(self, scene):
        self.destroy()

    def destroy(self):
        self.logger.debug('Game.destroy')
        self.spawner.destroy()
        self.http_rot.destroy()

        if self._onGameEnded in bpy.app.handlers.game_post:
            bpy.app.handlers.game_post.remove(self._onGameEnded)

    def update(self):
        self.ui.update()
        self.spawner.update()
        self.spawner.spawn(self.http_rot.rotation)
        self.http_rot.update()

import logging, time, math, bge
from ui import Ui
import anim
from strip import Strip

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
        self.ui = Ui.singleton(verbose=verbose)
        self.anim_manager = anim.Manager(verbose=verbose)

        self.logger = logging.getLogger(__name__)
        if verbose:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

    def setup(self):
        self.ui.setup()
        self.ui.keyPressEvent += self._onKey

    def update(self):
        self.ui.update()
        self.anim_manager.update()

    def _onKey(self, keyCode):
        if keyCode == bge.events.ONEKEY or keyCode == bge.events.PAD1:
            for strip in Strip.owner_instances():
                a = anim.Sin()
                a.setup(strip)
                self.anim_manager.start(a)

        if keyCode == bge.events.TWOKEY or keyCode == bge.events.PAD2:
            a = anim.Wipe()
            a.setup(Strip.owner_instances())
            self.anim_manager.start(a)

        if keyCode == bge.events.THREEKEY or keyCode == bge.events.PAD3:
            a = anim.Dance(duration=10.0)
            a.setup(Strip.owner_instances())
            self.anim_manager.start(a)

        if keyCode == bge.events.FOURKEY or keyCode == bge.events.PAD4:
            for strip in Strip.owner_instances():
                strip.owner.playAction('zigzag', 0, 100)

        if keyCode == bge.events.FIVEKEY or keyCode == bge.events.PAD5:
            for strip in Strip.owner_instances():
                for light in strip.lights:
                    light.playAction('lightdip', 200, 250)

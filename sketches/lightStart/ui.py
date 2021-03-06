import bge
import logging
from evento import Event

def onButton1(controller): onButton(controller, 1)
def onButton2(controller): onButton(controller, 2)
def onButton3(controller): onButton(controller, 3)
def onButton4(controller): onButton(controller, 4)
def onButton5(controller): onButton(controller, 5)

class Ui:
    _singleton_instance = None

    @classmethod
    def singleton(cls, *args, **kwargs):
        if not cls._singleton_instance:
            cls._singleton_instance = cls(*args, **kwargs)

        return cls._singleton_instance

    def __init__(self, verbose=True):
        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)

        self.keyPressEvent = Event()

    def setup(self):
        pass

    def update(self):
        # event-style
        for key, state in bge.logic.keyboard.events.items():
            if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
                self.keyPressEvent(key)

    def keyIsDown(self, keyCode):
        return bge.logic.KX_INPUT_ACTIVE == bge.logic.keyboard.events[keyCode]

    def keyPressed(self, keyCode):
        return bge.logic.KX_INPUT_JUST_ACTIVATED == bge.logic.keyboard.events[keyCode]

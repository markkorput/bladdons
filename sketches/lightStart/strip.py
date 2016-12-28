import logging, time, math
import time

def setup(controller):
    logging.getLogger().debug('script.setup')
    Strip.for_owner(controller.owner).setup()

# This method should be called by a controller in the blender object's
# game logic and that controller should be triggered by an 'always' sensor,
# with TRUE level triggering enabled (Pulse mode) so it gets called every game-loop iteration
def update(controller):
    # logging.getLogger().debug('script.update')
    Strip.for_owner(controller.owner).update()
    # PyMoCap.for_owner(owner).update()

class Strip:
    _instances_by_owner = {}

    @classmethod
    def for_owner(cls, owner, create=True):
        if owner in cls._instances_by_owner:
            return cls._instances_by_owner[owner]

        if not create:
            return None

        # Create new instance
        instance = cls(owner)
        # Store it so it can be found next time
        cls._instances_by_owner[owner] = instance
        return instance

    @classmethod
    def owner_instances(cls):
        return cls._instances_by_owner.values()

    def __init__(self, owner):
        self.owner = owner
        self.logger = logging.getLogger()
        if 'verbose' in self.owner and self.owner['verbose']:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

    def setup(self):
        self.logger.debug('Strip.setup for ' + self.owner.name)
        self.logger.debug('spawning light objects')

        self.lights = []
        for i in range(10):
            object = self.owner.scene.addObject(self.owner['lightshape'], self.owner['lightshape'])
            object.setParent(self.owner)
            object.localPosition = [0.0, 2.0 * (i+1), 0.0]
            self.lights.append(object)

    def update(self):
        self.logger.info('Strip.update')

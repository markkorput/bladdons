import logging, random

class Spawner:
    def __init__(self, verbose=False):
        self.rings = []

        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    def __del__(self):
        self.destroy()

    def setup(self, logicObject):
        self.logicObject = logicObject
        self.spawn_parent = self.logicObject.scene.objects[self.logicObject['spawner']] if 'spawner' in self.logicObject else self.logicObject
        self.orientator = self.logicObject.scene.objects[self.logicObject['orientator']] if 'orientator' in self.logicObject else self.logicObject
        self.spawnRot = self.logicObject['spawnRot'] if 'spawnRot' in self.logicObject else None
        self.rotation = [0.0,0.0,0.0]

    def destroy(self):
        pass

    def update(self):
        ended = []
        for ring in self.rings:
            if not ring.isPlayingAction():
                self.logger.debug('endObject')
                if ring.parent != self.spawn_parent:
                    ring.parent.endObject()
                ring.endObject()
                ended.append(ring)

        for ended_ring in ended:
            self.rings.remove(ended_ring)

    def spawn(self):
        ring_names = self._getRingNames()

        if len(ring_names) < 1:
            self.logger.warning("no ring name properties found on logicObject, can't spawn")
            return

        ring_name = random.choice(ring_names)

        try:
            self.logger.debug('spawning: ', ring_name)
            obj = self.logicObject.scene.addObject(ring_name, ring_name)

            if self.spawnRot:
                spawnRotObj = self.logicObject.scene.addObject(self.spawnRot, self.spawnRot)
                spawnRotObj.setParent(self.spawn_parent)
                obj.setParent(spawnRotObj)
                spawnRotObj.localOrientation = self.rotation
            else:
                obj.setParent(self.spawn_parent)

            self.rings.append(obj)

            self.logger.debug('playAction: ring1Action')
            obj.playAction('ring1Action', 26, 100)
        except ValueError as err:
            self.logger.error("Erro while spawning ring:\n\n{0}\n".format(err))

    def _getRingNames(self):
        i = 1
        names = []
        while('ring'+str(i) in self.logicObject):
            names.append(self.logicObject['ring'+str(i)])
            i += 1

        return names

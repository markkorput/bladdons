import logging, bge, bpy, random, re, math
from .ui import Ui
from .web_server import WebServer

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

        self.logger = logging.getLogger(__name__)
        if verbose:
            # print('verbosing for '+owner.name)
            self.logger.setLevel(logging.DEBUG)

        self.rings = []
        self.web_server = WebServer({
            'verbose': verbose,
            'serve': 'scripts/www/'})

        self.http_requests = []

    def __del__(self):
        self.destroy()

    def setup(self):
        self.ui.setup()
        self.web_server.setup()
        self.web_server.requestEvent += self._onRequest

        self.spawn_parent = self.owner.scene.objects[self.owner['spawner']] if 'spawner' in self.owner else self.owner
        self.orientator = self.owner.scene.objects[self.owner['orientator']] if 'orientator' in self.owner else self.owner
        self.spawnRot = self.owner['spawnRot'] if 'spawnRot' in self.owner else None

        self._rot = [0.0,0.0,0.0]
        self.logger.debug('spawn par:', self.spawn_parent.name)
        bpy.app.handlers.game_post.append(self._onGameEnded)

    def _onGameEnded(self, scene):
        self.destroy()

    def destroy(self):
        if self._onRequest in self.web_server.requestEvent:
            self.web_server.requestEvent -= self._onRequest
        self.web_server.destroy()

        if self._onKey in self.ui.keyPressEvent:
            self.ui.keyPressEvent -= self._onKey

        if self._onGameEnded in bpy.app.handlers.game_post:
            bpy.app.handlers.game_post.remove(self._onGameEnded)

    def update(self):
        self.ui.update()

        # if self.ui.keyIsDown(bge.events.PAD1):
        self.fire()

        for handler in self.http_requests:
            # print('got http: '+handler.path)
            self.logger.debug('got http: '+handler.path)
            result = re.compile('^\/rot/(.+)\/(.+)\/(.+)$').findall(handler.path)
            if len(result) == 1 and len(result[0]) == 3:
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

                self.logger.debug('got orientation data from HTTP-server: {0}, {1}, {2}'.format(a,b,c))
                # self.orientator.localOrientation = [math.radians(c),math.radians(-b),math.radians(a)]
                self._rot = [math.radians(c),math.radians(-b),math.radians(a)]

        self.http_requests = []
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

    def _onKey(self, keyCode):
        pass

    def fire(self):
        ring_names = self._getRingNames()

        if len(ring_names) < 1:
            self.logger.warning("no ring name properties found on owner object, can't spawn")
            return

        ring_name = random.choice(ring_names)

        try:
            self.logger.debug('spawning: ', ring_name)
            obj = self.owner.scene.addObject(ring_name, ring_name)

            if self.spawnRot:
                spawnRotObj = self.owner.scene.addObject(self.spawnRot, self.spawnRot)
                spawnRotObj.setParent(self.spawn_parent)
                obj.setParent(spawnRotObj)
                spawnRotObj.localOrientation = self._rot
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
        while('ring'+str(i) in self.owner):
            names.append(self.owner['ring'+str(i)])
            i += 1

        return names

    def _onRequest(self, handler):
        self.http_requests.append(handler)

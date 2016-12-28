import logging, time

class Anim:
    def __init__(self, duration=3.0):
        self.duration = duration
        self.t = None
        self.active = False
        self.progress = 0.0
        self.finished = False

    def start(self):
        self.t = 0.0
        self.active = True
        self.progress = 0.0
        self.finished = False

    def update(self, dt):
        if not self.active:
            return

        self.t += dt
        self.progress = (self.t / self.duration)
        if self.t >= self.duration:
            self.active = False
            self.finished = True

class Manager:
    _singleton_instance = None

    @classmethod
    def singleton(cls, *args, **kwargs):
        if not cls._singleton_instance:
            cls._singleton_instance = cls(*args, **kwargs)

        return cls._singleton_instance

    def __init__(self, verbose=False):
        self.anims = []
        self.last_update = None

        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    def add(self, anim):
        self.anims.append(anim)

    def update(self, dt=None):
        if not dt:
            if not self.last_update:
                self.last_update = time.time()
                dt = 0.0
            else:
                t = time.time()
                self.last_update, dt = (t, t - self.last_update)

        for anim in self.anims:
            anim.update(dt)
            if anim.finished:
                self.remove(anim)

    def remove(self, anim):
        try:
            self.anims.remove(anim)
        except:
            self.logger.warning("anim.Manager.remove: unknown anim")

    def clear(self):
        for anim in self.anims:
            self.remove(anim)

    def start(self, anim):
        anim.start()
        self.add(anim)

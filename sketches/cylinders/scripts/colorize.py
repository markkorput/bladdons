import time, random

class Colorize:
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

    @classmethod
    def destroy_by_owner(cls, owner):
        del cls._instances_by_owner[owner]

    def __init__(self, owner):
        self.owner = owner
        self.spawn_time = time.time()
        # self.colors =
        euler = self.owner.worldOrientation.to_euler()
        self.r = euler.x
        self.g = euler.y
        self.b = euler.z

    def get_colors(self):
        return (self.r, self.g, self.b)

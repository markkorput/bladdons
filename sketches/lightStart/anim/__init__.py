import math
from .anim import Anim, Manager

class Sin(Anim):
    def setup(self, strip):
        self.strip = strip

    def update(self, dt):
        Anim.update(self, dt)
        speed = self.strip.owner['sin_speed'] if 'sin_speed' in self.strip.owner else 1
        value = math.sin(self.progress * math.pi * 2 * 3 * speed)

        value = (value + 1)/2*len(self.strip.lights)
        for i, light in enumerate(self.strip.lights):
            light.visible = i <= value

class Wipe(Anim):
    def setup(self, strips, width = 1.5):
        self.strips = strips
        self.width = width
        self.min = None
        self.max = None

        for strip in self.strips:
            for light in strip.lights:
                if self.min == None or light.worldPosition.x < self.min:
                    self.min = light.worldPosition.x

                if self.max == None or light.worldPosition.x > self.max:
                    self.max = light.worldPosition.x

    def update(self, dt):
        Anim.update(self, dt)
        percentage = (math.sin(self.progress * math.pi * 2 * 3) + 1)/2
        pos = self.min + (self.max - self.min) * percentage

        for strip in self.strips:
            for light in strip.lights:
                light.visible = abs(light.worldPosition.x - pos) <= self.width

class Dance(Anim):
    def setup(self, strips, intensity = 1.0):
        self.strips = strips
        self.intensity = intensity

    def update(self, dt):
        Anim.update(self, dt)

        for stripidx, strip in enumerate(self.strips):
            numlights = len(strip.lights)
            for idx, light in enumerate(strip.lights):
                light.localPosition.z = math.sin(stripidx*1.5 + idx*0.3 + self.progress * math.pi * 2) * self.intensity

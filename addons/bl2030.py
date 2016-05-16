# blender-addon info
bl_info = {
    "name": "bl2030",
    "author": "Short Notion (Mark van de Korput)",
    "version": (0, 0, 1),
    "blender": (2, 75, 0),
    "location": "View3D > T-panel > Object Tools",
    "description": "Use blenders graph-editor to send OSC values",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"}

import bpy
from bpy.app.handlers import persistent
import logging

# bl2030 packages


# TODO; this should be configurable through a UI panel
class Config:
    def __init__(self):
        self.osc_host = '127.0.0.1'
        self.osc_port = '2031'
        self.debugging = True

class Runner:
    _instance = None
    _instances = {}

    def instance():
        if Runner._instance:
            return Runner._instance
        Runner._instance = Runner()
        return Runner._instance

    def instance_for(target):
        if target in Runner._instances:
            return Runner._instances[target]
        Runner._instances[target] = Runner()
        return Runner._instances[target]

    def __init__(self, options = {}):
        self.options = options
        self._object_wrappers = None
        self.osc_sender = None
        self.is_setup = False

    def setup(self):
        self.object_wrappers()
        cfg = Config()
        from osc_sender import OscSender
        self.osc_sender = OscSender({'host': cfg.osc_host, 'port': cfg.osc_port})
        self.osc_sender.setup()
        self.is_setup = True
        del OscSender

    def update(self):
        if not self.is_setup:
            self.setup()

        for ow in self.object_wrappers():
            for propwrap in ow.property_wrappers():
                val = propwrap.update()
                if val:
                    self.osc_sender.send(propwrap.property_name, [val])
                    # print('TODO: send ' + propwrap.property_name + ' with ' + str(val))

    def object_wrappers(self):
        if self._object_wrappers:
            return self._object_wrappers
        self._object_wrappers = self._get_relevant_object_wrappers()

        for ow in self._object_wrappers:
            print('Found object: '+ow.obj.name)
            for propwrap in ow.property_wrappers():
                print(' - ' + propwrap.property_name + ': ' +str(propwrap.get_current_value()))

        return self._object_wrappers

    def _get_relevant_object_wrappers(self):
        result = []
        for obj in bpy.context.scene.objects:
            objwrap = ObjectWrapper(obj)
            if objwrap.is_relevant():
                result.append(objwrap)
        return result

class ObjectWrapper:
    def __init__(self, obj):
        self.obj = obj
        self._prop_names = None
        self._prop_wrappers = None

    def is_relevant(self):
        return len(self.prop_names()) > 0

    def prop_names(self):
        if self._prop_names:
            return self._prop_names
        self._prop_names = self._get_relevant_property_names()
        return self._prop_names

    def _get_relevant_property_names(self):
        prop_names = []
        all_prop_names = self.obj.keys()
        for prop_name in all_prop_names:
            if prop_name.startswith('/'):
                prop_names.append(prop_name)
        return prop_names

    def property_wrappers(self):
        if self._prop_wrappers:
            return self._prop_wrappers
        self._prop_wrappers = self._get_prop_wrappers()
        return self._prop_wrappers

    def _get_prop_wrappers(self):
        result = []
        for prop_name in self.prop_names():
            result.append(PropertyWrapper(self.obj, prop_name))
        return result

class PropertyWrapper:
    def __init__(self, obj, property_name):
        self.obj = obj
        self.property_name = property_name
        self.prev_value = None

    def get_current_value(self):
        return self.obj[self.property_name]

    def changed_value(self):
        cur = self.get_current_value()
        if cur != self.prev_value:
            return cur
        return None

    def update(self):
        changed = self.changed_value()
        if changed:
            self.prev_value = changed
        return changed

#
# bl2030 add-on stuff
#


def setup():
    logging.getLogger().debug('bl2030.setup')
    Runner.instance().setup()
    # global manager
    # manager = Manager()
    # bpy.app.handlers.game_post.append(destroy)

# # This method should be called by a controller in the blender object's
# # game logic and that controller should be triggered by an 'always' sensor,
# # with TRUE level triggering enabled (Pulse mode) so it gets called every game-loop iteration
# def update(controller):
#     owner = controller.owner
#     bl2030.for_owner(owner).update()

@persistent
def destroy(scene):
    logging.getLogger().debug('bl2030.destroy')
    Runner.instance().destroy()
    #
    # for instance in PyMoCap._instances_by_owner.values():
    #     instance.destroy()
    #     PyMoCap._instances_by_owner = {}

@persistent
def frameHandler(scene):
    Runner.instance_for(scene).update()

def register():
  # bpy.utils.register_module(__name__)
  bpy.app.handlers.frame_change_pre.append(frameHandler)

def unregister():
  # bpy.utils.unregister_module(__name__)
  bpy.app.handlers.frame_change_pre.remove(frameHandler)

if __name__ == "__main__":
  # register()
  pass

# setup()
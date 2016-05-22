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
        Runner._instances[target] = Runner(target)
        return Runner._instances[target]

    def __init__(self, scene):
        self.scene = scene
        self.config = scene.bl2030cfg
        self.osc_sender = self._get_osc_sender()
        self._object_wrappers = None

    def _get_osc_sender(self):
        from osc_sender import OscSender
        osc_sender = OscSender({'host': self.config.host, 'port': self.config.port})
        osc_sender.setup()
        del OscSender
        return osc_sender

    def update(self):
        if self.config.live_update:
            if self.osc_sender.host() != self.config.host or self.osc_sender.port() != self.config.port:
                self.osc_sender.destroy()
                self.osc_sender = self._get_osc_sender()

        # check if we reached any of the markers,
        # if so, emit and OSC message
        cur_frame = self.scene.frame_current
        for marker in self.scene.timeline_markers:
            if marker.frame == cur_frame and marker.name.startswith('/'):
                self.osc_sender.send(marker.name)
                if self.config.verbose:
                    print(' - OSC from marker: '+marker.name)

        # check for each property wrapper if the value changed,
        # if so; emit an OSC message
        for ow in self.object_wrappers():
            if ow.obj.hide:
                continue

            for propwrap in ow.property_wrappers():
                val = propwrap.update()
                #print('checking '+propwrap.property_name+": "+str(val)+" (prev val: "+str(propwrap.prev_value)+")")
                if val != None:
                    addr = ow.prefix + propwrap.property_name
                    self.osc_sender.send(addr, [val])
                    if self.config.verbose:
                        print(' - OSC from property: {0} {1}'.format(addr, str(val)))

    def object_wrappers(self):
        if self._object_wrappers:
            if self.config.live_update:
                self._update_object_wrappers()
            return self._object_wrappers

        self._object_wrappers = self._get_relevant_object_wrappers()

        if self.config.verbose:
            for ow in self._object_wrappers:
                print('OSC object: {0} (prefix: {1})'.format(ow.obj.name, ow.prefix))
            for propwrap in ow.property_wrappers():
                print(' - ' + propwrap.property_name + ': ' +str(propwrap.get_current_value()))

        return self._object_wrappers

    def _get_relevant_object_wrappers(self):
        result = []
        for obj in self.scene.objects:
            objwrap = ObjectWrapper(obj, self.config)
            if objwrap.is_relevant():
                result.append(objwrap)
        return result

    def _update_object_wrappers(self):
        for obj in self.scene.objects:
            wrap = self._existing_wrapper(obj)
            if wrap:
                wrap.setup()
                continue

            objwrap = ObjectWrapper(obj, self.config)

            if objwrap.is_relevant():
                if not self._object_wrappers:
                    self._object_wrappers = []

                self._object_wrappers.append(objwrap)

    def _existing_wrapper(self, obj):
        if not self._object_wrappers:
            return None

        for existing in self._object_wrappers:
            if existing.obj == obj:
                return existing
        return None

class ObjectWrapper:
    def __init__(self, obj, config):
        self.obj = obj
        self.config = config
        self._prop_names = None
        self._prop_wrappers = None
        self.setup()

    def setup(self):
        self.prefix = self._get_prefix()

    def _get_prefix(self):
        prefix = ''
        o = self.obj
        while o:
            if o.name.startswith('/'):
                prefix = o.name + prefix
            o = o.parent
        return prefix

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
            if self.config.live_update:
                self._update_prop_wrappers()
            return self._prop_wrappers
        self._prop_wrappers = self._get_prop_wrappers()
        return self._prop_wrappers

    def _get_prop_wrappers(self):
        result = []
        for prop_name in self.prop_names():
            result.append(PropertyWrapper(self.obj, prop_name))
        return result

    def _update_prop_wrappers(self):
        for prop_name in self._get_relevant_property_names():
            if self._existing_wrapper(prop_name):
                continue

            if not self._prop_wrappers:
                self._prop_wrappers = []

            wrap = PropertyWrapper(self.obj, prop_name)
            self._prop_wrappers.append(wrap)

    def _existing_wrapper(self, prop_name):
        if not self._prop_wrappers:
            return None

        for existing in self._prop_wrappers:
            if existing.property_name == prop_name:
                return existing
        return None

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
        if changed != None:
            self.prev_value = changed
        return changed

#
# bl2030 add-on stuff
#

# This class is in charge of the blender UI config panel
class Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "2030"
    bl_idname = "SCENE_bl2030"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        config = context.scene.bl2030cfg

        layout.row().prop(config, "host")
        layout.row().prop(config, "port")
        layout.row().prop(config, "live_update")
        layout.row().prop(config, "verbose")
        #layout.row().label('Last Messages:\n'+config.last_messages)

# This class represents the bl2030 config data (that the UI Panel interacts with)
class Config(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Scene.bl2030cfg = bpy.props.PointerProperty(
      name="bl2030 Config",
      description="Scene-specific bl2030 settings",
      type=cls)

    # Add in the properties
    # cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable bl2030")
    cls.port = bpy.props.IntProperty(name="Port", soft_max=9999, soft_min=0, description="Port to send OSC messages to")
    cls.host = bpy.props.StringProperty(name="Host", default="127.0.0.1")
    cls.live_update = bpy.props.BoolProperty(name="live_update", default=False)
    cls.verbose = bpy.props.BoolProperty(name="verbose", default=False)
    # cls.last_messages = bpy.props.StringProperty(name="Last Messages", default="")

@persistent
def frameHandler(scene):
    Runner.instance_for(scene).update()

def register():
  bpy.utils.register_module(__name__)
  bpy.app.handlers.frame_change_pre.append(frameHandler)

def unregister():
  bpy.utils.unregister_module(__name__)
  bpy.app.handlers.frame_change_pre.remove(frameHandler)

if __name__ == "__main__":
  # register()
  pass

# setup()

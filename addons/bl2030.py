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
    _instances = {}

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

    def send_obj_props(self, object, recursive=False):
        sender = self.sender()
        # check for each property wrapper if the value changed,
        # if so; emit an OSC message
        ow = ObjectWrapper.instance_for(object)
        if recursive:
            ows = ow.offspring()
            ows.append(ow)
        else:
            ows = [ow]
        for ow in ows:
            for propwrap in ow.property_wrappers():
                val = propwrap.get_current_value()
                addr = ow.prefix + propwrap.property_name
                sender.send(addr, [val])
                if self.config.verbose:
                    print(' - OSC from property: {0} {1}'.format(addr, str(val)))

    def sender(self):
        if self.osc_sender.host() != self.config.host or self.osc_sender.port() != self.config.port:
            self.osc_sender.destroy()
            self.osc_sender = self._get_osc_sender()
        return self.osc_sender

    def _get_osc_sender(self):
        from osc_sender import OscSender
        osc_sender = OscSender({'host': self.config.host, 'port': self.config.port})
        osc_sender.setup()
        del OscSender
        return osc_sender

    def update(self):
        sender = self.sender()
        # check if we reached any of the markers,
        # if so, emit and OSC message
        cur_frame = self.scene.frame_current
        for marker in self.scene.timeline_markers:
            if marker.frame == cur_frame and marker.name.startswith('/'):
                sender.send(marker.name)
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
                    sender.send(addr, [val])
                    if self.config.verbose:
                        print(' - OSC from property: {0} {1}'.format(addr, str(val)))

    def object_wrappers(self):
        result = []
        for obj in self.scene.objects:
            objwrap = ObjectWrapper.instance_for(obj)
            if objwrap.is_relevant():
                result.append(objwrap)
        return result

class ObjectWrapper:
    _instances = {}

    def instance_for(obj):
        if obj in ObjectWrapper._instances:
            return ObjectWrapper._instances[obj]
        ow = ObjectWrapper(obj)
        ObjectWrapper._instances[obj] = ow
        return ow

    def __init__(self, obj):
        self.obj = obj
        self._prop_names = None
        self._prop_wrappers = None
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
        prop_names = []
        all_prop_names = self.obj.keys()
        for prop_name in all_prop_names:
            if prop_name.startswith('/'):
                prop_names.append(prop_name)
        return prop_names

    def property_wrappers(self):
        result = []
        for prop_name in self.prop_names():
            result.append(PropertyWrapper.instance_for(self.obj, prop_name))
        return result

    def offspring(self):
        result = []
        for child in self.obj.children:
            ow = ObjectWrapper.instance_for(child)
            result.append(ow)
            result.extend(ow.offspring())
        return result

class PropertyWrapper:
    _instances = {}

    def instance_for(obj, property_name):
        identifier = obj.name+"."+property_name
        if identifier in PropertyWrapper._instances:
            return PropertyWrapper._instances[identifier]
        ow = PropertyWrapper(obj, property_name)
        PropertyWrapper._instances[identifier] = ow
        return ow

    def __init__(self, obj, property_name):
        self.obj = obj
        self.property_name = property_name
        self.prev_value = self.get_current_value()

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

        layout.row().operator("object.bl2030sendobjprops", text="Send all object's properties")
        layout.row().operator("object.bl2030sendobjfamilyprops", text="Send all object and children's properties")
        layout.row().prop(config, "host")
        layout.row().prop(config, "port")
        # layout.row().prop(config, "live_update")
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
    # cls.live_update = bpy.props.BoolProperty(name="live_update", default=False)
    cls.verbose = bpy.props.BoolProperty(name="verbose", default=False)
    # cls.last_messages = bpy.props.StringProperty(name="Last Messages", default="")


class Bl2030ObjPropsSender(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bl2030sendobjprops"
    bl_label = "PointCloud"
    # bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.scene

    def execute(self, context):
        Runner.instance_for(context.scene).send_obj_props(context.object)
        return {'FINISHED'}

class Bl2030ObjFamilyPropsSender(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bl2030sendobjfamilyprops"
    bl_label = "PointCloud"
    # bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.scene

    def execute(self, context):
        Runner.instance_for(context.scene).send_obj_props(context.object, True)
        return {'FINISHED'}

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

bl_info = {
    "name": "ui-editor",
    "author": "Short Notion (Mark van de Korput)",
    "version": (0, 0, 1),
    "blender": (2, 75, 0),
    "location": "Import-Export > T-panel > Object Tools",
    "description": "Use blenders graph-editor to send OSC values",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"}

import logging
import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

class Runner:
    _instances = {}

    def instance_for(target):
        if target in Runner._instances:
            return Runner._instances[target]
        Runner._instances[target] = Runner(target)
        return Runner._instances[target]

    def __init__(self, scene):
        self.scene = scene
        # immediately run setup
        self.setup()

    def setup(self):
        # nothing to do at this point...
        pass

    def update(self):
        # loop-over-and-update all root-level objects
        for obj in self.scene.objects:
            if obj.type == 'MESH' and obj.parent == None and obj.uiEditorCfg.enabled == True:
                ObjectRunner.instance_for(obj).update()

class ObjectRunner:
    _instances = {}

    def instance_for(target):
        if target in ObjectRunner._instances:
            return ObjectRunner._instances[target]
        ObjectRunner._instances[target] = ObjectRunner(target)
        return ObjectRunner._instances[target]

    def __init__(self, obj):
        self.object = obj
        self.config = obj.uiEditorCfg
        self.dataCache = {}
        # immediately run setup
        self.setup()

    def setup(self):
        # retrieve/load OscSender instance
        from .osc_sender import OscSender
        self.osc_sender = OscSender.instance_for(self.config.host, self.config.port)
        del OscSender
        # make sure it's connected
        if(self.osc_sender.isConnected() != True):
            self.osc_sender.setup()

    def update(self):
        self.osc_sender.setVerbose(self.config.verbose)
        # self and all child objects (recursively)
        Processor(self.object, self.osc_sender, self.dataCache, verbose=self.config.verbose).process()

class Processor:
    def __init__(self, object, osc_sender, dataCache, scope=None, verbose=False):
        self.object = object
        self.osc_sender = osc_sender
        self.dataCache = dataCache
        self.scope = scope
        self.verbose = verbose

        # self.logger = logging.getLogger(__name__)
        # if verbose:
        #     self.logger.setLevel(logging.DEBUG)

    def process(self):
        data = self.data()

        # check if we got an existing record for this object
        existing = self.dataCache[data['id']] if data['id'] in self.dataCache else None

        # update cache record
        self.dataCache[data['id']] = data
        # send osc
        self._send_changes(data, existing)

        scope = data['id'] if self.scope == None else self.scope + '/' + data['id']

        for child in self.object.children:
            Processor(child, self.osc_sender, self.dataCache, scope=scope, verbose=self.verbose).process()

    def _send_changes(self, data, previousData):
        basePath = '/ui-editor/mesh/'
        obj_id = self.scope + '/' + data['id'] if self.scope else data['id']

        # Vectors (vec3)
        prop_names = ['position', 'rotation', 'scale']

        for prop_name in prop_names:
            # only send changed properties
            if previousData == None or data[prop_name] != previousData[prop_name]:
                self.osc_sender.send(basePath+prop_name, [
                                obj_id,
                                data[prop_name].x,
                                data[prop_name].y,
                                data[prop_name].z])

        # Vertices (array of Vectors/vec3)
        if previousData == None or data['vertices'] != previousData['vertices']:
            vertexParams = [obj_id]
            for vertex in data['vertices']:
                vertexParams.append(vertex.x)
                vertexParams.append(vertex.y)
                vertexParams.append(vertex.z)

            self.osc_sender.send(basePath+'vertices', vertexParams)

    def obj_id(self, include_scope=True):
        # remove optional ui type postfix
        _id = self.object.name.split('.')[0]

        # include scope if necessary
        if include_scope and self.scope != None:
            _id = self.scope + '/' + _id

        return _id

    def ui_type(self):
        parts = self.object.name.split('.')

        if len(parts) == 2:
            return parts[1]

        return ''

    def data(self):
        return {
            'id': self.object.name, #self.obj_id(),
            # 'type': self.ui_type(),
            'position': Vector(self.object.location),
            'rotation': Vector(self.object.rotation_euler),
            'scale': Vector(self.object.scale),
            'vertices': [Vector(v.co) for v in self.object.data.vertices]
        }

# This class is in charge of the blender UI config panel
class Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "UI-editor"
    bl_idname = "OBJECT_uiEditor"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        config = context.object.uiEditorCfg
        layout.row().prop(config, "enabled")
        if(config.enabled):
            layout.row().prop(config, "host")
            layout.row().prop(config, "port")
            layout.row().prop(config, "verbose")

# This class represents the bl2030 config data (used by the UI Panel)
class Config(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Object.uiEditorCfg = bpy.props.PointerProperty(
      name="UI-editor Config",
      description="Object-specific ui-editor settings",
      type=cls)

    # Add in the properties
    cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable ui-editor for this object")
    cls.port = bpy.props.IntProperty(name="Port", soft_max=9999, soft_min=0, default=8080, description="Port to send OSC messages to")
    cls.host = bpy.props.StringProperty(name="Host", default="127.0.0.1")
    # cls.live_update = bpy.props.BoolProperty(name="live_update", default=False)
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

# if __name__ == "__main__":
#   pass

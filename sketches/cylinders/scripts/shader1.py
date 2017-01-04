from .colorize import Colorize
import time

def apply(controller):
    owner = controller.owner
    mesh = owner.meshes[0]

    for mat in mesh.materials:
        shader = mat.getShader()
        if shader != None:
            if not shader.isValid():
                shader.setSource(VertexShader, FragmentShader, 1)
            colorobj = owner.scene.objects[owner['colorobj']] if 'colorobj' in owner else owner
            xyz = colorobj.localOrientation.to_euler()
            colors = (owner.localPosition.z, xyz.y, xyz.z)
            factors = (time.time() * 0.01, time.time() * 0.015, time.time() * 0.223)
            colors = Colorize.for_owner(owner).get_colors()
            shader.setUniform3f('customColor', *list(map(lambda x: x % 1, colors)))


VertexShader = """
    // varying vec4 color;
    varying vec4 texCoords;

    void main() // all vertex shaders define a main() function
    {
        // color = gl_Color;
        texCoords = gl_MultiTexCoord0;
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    }
"""

FragmentShader = """
    // varying vec4 color;
    varying vec4 texCoords;
    uniform vec3 customColor;

    void main()
    {
        gl_FragColor = vec4(customColor, 1.0-abs(texCoords.y-0.5)*1.7);
        // gl_FragColor = vec4(1.0, 0.0, 0.0, texCoords.x);
        // gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
"""

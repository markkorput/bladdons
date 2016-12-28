import bge

def apply(controller):
    mesh = controller.owner.meshes[0]

    for mat in mesh.materials:
        shader = mat.getShader()
        if shader != None:
            if not shader.isValid():
                shader.setSource(VertexShader, FragmentShader, 1)

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

    void main()
    {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0-abs(texCoords.y-0.5)*1.7);
        // gl_FragColor = vec4(1.0, 0.0, 0.0, texCoords.x);
        // gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
"""

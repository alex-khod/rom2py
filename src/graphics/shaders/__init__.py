from src.resources import Resources
import os
path = os.path.dirname(__file__)
from pyglet.graphics.shader import Shader, ShaderProgram

def get_terrain_shader():
    self = get_terrain_shader
    if not hasattr(self, "shader"):
        vertex_source = Resources.from_file(path, "terrain_vertex.glsl")
        geometry_source = Resources.from_file(path, "terrain_geometry.glsl")
        fragment_source = Resources.from_file(path, "terrain_fragment.glsl")
        vertex = Shader(vertex_source, "vertex")
        geometry = Shader(geometry_source, "geometry")
        fragment = Shader(fragment_source, "fragment")
        program = ShaderProgram(vertex, geometry, fragment)
        self.shader = program

    return self.shader

def get_sprite_shader():
    self = get_sprite_shader
    if not hasattr(self, "shader"):
        vertex_source = Resources.from_file(path, "sprite_vertex.glsl")
        fragment_source = Resources.from_file(path, "sprite_fragment.glsl")
        vertex = Shader(vertex_source, "vertex")
        fragment = Shader(fragment_source, "fragment")
        program = ShaderProgram(vertex, fragment)
        self.shader = program

    return self.shader







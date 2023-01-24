#version 330 core

uniform sampler2D texture0;
in vec2 tex_coord;
in float is_passable;
out vec4 frag_color;

void main()
{
    vec2 tc = tex_coord / textureSize(texture0, 0);
    const float BrightnessUp = 0.05;
    frag_color = texture(texture0, tc) * vec4(1.0, is_passable, is_passable, 1.0) + BrightnessUp;
}
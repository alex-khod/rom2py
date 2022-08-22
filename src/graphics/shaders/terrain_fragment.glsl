#version 330 core

layout(binding=0) uniform sampler2D texture0;
layout(binding=1) uniform sampler2D texture1;
in vec2 tex_coord;
in vec2 tex_coord2;
in float is_passable;
out vec4 frag_color;

void main()
{
    vec2 tc = tex_coord / textureSize(texture0, 0);
    vec2 tc2 = tex_coord2 / textureSize(texture1, 0) / 32;
    const float BrightnessUp = 0.0;
    float light = texture(texture1, tc2).r * 2;
    frag_color = texture(texture0, tc) * 2 * light * vec4(1.0, 1.0, 1.0, 1.0) + BrightnessUp;
}
#version 330 core

uniform sampler2D tilemap_texture;
uniform sampler2D lighting_texture;
in vec2 tex_coord;
in vec2 tex_coord2;
in float is_passable;
out vec4 frag_color;

void main()
{
    vec2 tc = tex_coord / textureSize(tilemap_texture, 0);
    vec2 tc2 = tex_coord2 / textureSize(lighting_texture, 0) / 32;
    float light = texture(lighting_texture, tc2).r * 2;
    frag_color = texture(tilemap_texture, tc) * 2 * light * vec4(1.0, 1.0, 1.0, 1.0);
}
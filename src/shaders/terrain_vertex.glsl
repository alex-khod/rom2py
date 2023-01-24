#version 330 core
in float tile_id;
in float tile_no;
in vec4 hate_map;

uniform vec2 map_size;

out VS_OUT {
    float tile_id;
    vec4 hate_map;
} vs_out;

void main()
{
    float x = 32.0 * float(uint(tile_no) % uint(map_size.y));
    float y = 32.0 * float(uint(tile_no) / uint(map_size.y));
    gl_Position = vec4(x, y, 0.0, 1.0);
    vs_out.tile_id = tile_id;
    vs_out.hate_map = hate_map;
}
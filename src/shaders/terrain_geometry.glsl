#version 330 core

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

in VS_OUT {
        float tile_id;
        vec4 hate_map;
} gs_in[];

out vec2 tex_coord;

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

void main() {
    const float TILE_SIZE = 32.0;

    float tile_id = gs_in[0].tile_id;
    float stripe_id = uint(tile_id) >> 4u;
    float row_id = uint(tile_id) & 15u;

    vec2 tx_offset = vec2(stripe_id * TILE_SIZE, row_id * TILE_SIZE);
    float nudge = 2.0;

    vec4 hate_map = gs_in[0].hate_map;
    vec4 tile_pos = gl_in[0].gl_Position;

    gl_Position = window.projection * window.view * (tile_pos + vec4(0, -hate_map[0], 0.0, 0.0));
    tex_coord = vec2(tx_offset.x + nudge, tx_offset.y + nudge);
    EmitVertex();

    gl_Position = window.projection * window.view * (tile_pos + vec4(32.0, -hate_map[1], 0.0, 0.0));
    tex_coord = vec2(tx_offset.x + TILE_SIZE - nudge, tx_offset.y + nudge);
    EmitVertex();

    gl_Position = window.projection * window.view * (tile_pos + vec4(0.0, -hate_map[3] + 32.0, 0.0, 0.0));
    tex_coord = vec2(tx_offset.x, tx_offset.y + TILE_SIZE - nudge);
    EmitVertex();

    gl_Position = window.projection * window.view * (tile_pos + vec4(32.0, -hate_map[2] + 32.0, 0.0, 0.0));
    tex_coord = vec2(tx_offset.x + TILE_SIZE - nudge, tx_offset.y + TILE_SIZE - nudge);
    EmitVertex();

    EndPrimitive();
}
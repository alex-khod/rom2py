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
out vec2 tex_coord2;
out float is_passable;

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

void main() {
    const float TILE_SIZE = 32.0;

    uint tile_id = uint(gs_in[0].tile_id);
    float column_id = tile_id >> 4u;
    float row_id = tile_id & 15u;
    //    column_id = [28..31] - rock tiles
    //    column_id = [32..48] - water tiles
    is_passable = float((column_id > 27.5) && (column_id < 49.5));
    // not
    is_passable = 1.0 - is_passable;

    vec2 tx_offset = vec2(column_id * TILE_SIZE, row_id * TILE_SIZE);
    float nudge = 2.0;

    vec4 hate_map = gs_in[0].hate_map;
    vec4 tile_pos = gl_in[0].gl_Position;

    gl_Position = window.projection * window.view * (tile_pos + vec4(0, -hate_map[0], 0.0, 0.0));
    tex_coord = vec2(tx_offset.x + nudge, tx_offset.y + nudge);
    tex_coord2 = tile_pos.xy;
    EmitVertex();

    gl_Position = window.projection * window.view * (tile_pos + vec4(TILE_SIZE, -hate_map[1], 0.0, 0.0));
    tex_coord = vec2(tx_offset.x + TILE_SIZE - nudge, tx_offset.y + nudge);
    tex_coord2 = tile_pos.xy + vec2(32.0, 0.0);
    EmitVertex();

    gl_Position = window.projection * window.view * (tile_pos + vec4(0.0, -hate_map[3] + TILE_SIZE, 0.0, 0.0));
    tex_coord = vec2(tx_offset.x, tx_offset.y + TILE_SIZE - nudge);
    tex_coord2 = tile_pos.xy + vec2(0.0, 32.0);
    EmitVertex();

    gl_Position = window.projection * window.view * (tile_pos + vec4(TILE_SIZE, -hate_map[2] + TILE_SIZE, 0.0, 0.0));
    tex_coord = vec2(tx_offset.x + TILE_SIZE - nudge, tx_offset.y + TILE_SIZE - nudge);
    tex_coord2 = tile_pos.xy + vec2(32.0, 32.0);
    EmitVertex();

    EndPrimitive();
}
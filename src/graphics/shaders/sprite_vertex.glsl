#version 150 core

in vec2 position;
in vec3 translate;
in vec3 tex_coords;
in vec3 pal_coords;
in vec2 scale;
in vec4 colors;

out VS_OUT{
    vec3 tex_coords;
    vec3 pal_coords;
    vec4 color;
} vs_out;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

mat4 m_scale = mat4(1.0);
mat4 m_translate = mat4(1.0);

void main()
{
    m_scale[0][0] = scale.x;
    m_scale[1][1] = scale.y;
    m_translate[3][0] = translate.x;
    m_translate[3][1] = translate.y;
    m_translate[3][2] = translate.z;

    gl_Position = window.projection * window.view * m_translate * m_scale * vec4(position, 0.0, 1.0);
    vs_out.tex_coords = tex_coords;
    vs_out.pal_coords = pal_coords;
    vs_out.color = colors;
}
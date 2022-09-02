#version 150 core

in VS_OUT{
    vec3 tex_coords;
//    'flat' modifier doesn't seem to do anything useful
    vec3 pal_coords;
    vec4 color;
} fs_in;


const float MODE_R = 0;
const float MODE_RG = 1.0;

//uniform vec3 palette[256];
uniform float mode;
uniform sampler2D sprite_texture;
uniform sampler2D palette_texture;

out vec4 frag_color;

void main()
{
    //    tex_coord points to sprite_texture which contains color_index
    //    in shape of as RGB's R value in range [0..1].
    //    multiply by 255 to denormalize it
    vec2 size = textureSize(sprite_texture, 0);
    vec2 uv = trunc(fs_in.tex_coords.xy * size) + vec2(0.5, 0.5);
    float color_index = texture(sprite_texture, uv / size).r * 255 + 0.5;

    //        float color_index = trunc(texture(sprite_texture, fs_in.tex_coords.xy).r * 255) + 0.5;
    //    calculate the actual color texel coordinates inside the palette texture
    vec2 color_uv = vec2(color_index, 0.5) / textureSize(palette_texture, 0);
    //    offset by pal_coords
    color_uv += fs_in.pal_coords.st;
    float alpha = float(color_index > 0.75);
    //    Now actually use the offset to get color
    frag_color = vec4(texture(palette_texture, color_uv).rgb * 1.5, alpha) * fs_in.color;
    if (frag_color.a < 0.5){
        discard;
    }
    //    frag_color = vec4(vec3(gl_FragCoord.z * 4), 1.0);
    //    (debug) Draw palette offset. Should output flat-shaded quad, probably red
    //    frag_color = vec4(fs_in.pal_coords, 1.0);
    //    frag_color = vec4(color_index/256, 0.0, 0.0, 1.0);
}

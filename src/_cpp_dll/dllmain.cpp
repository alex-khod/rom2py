// dllmain.cpp : Определяет точку входа для приложения DLL.
#include "pch.h"

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

typedef unsigned char uint8_t;
typedef unsigned int  uint32_t;


extern "C" __declspec(dllexport) void ROM256_to_color_indexes(uint8_t * data, uint8_t * output, uint32_t data_size, uint32_t w, uint32_t h)
{
    uint32_t x = 0;
    uint32_t y = 0;
    uint32_t offset = 0;
    while (offset < data_size)
    {
        uint8_t _byte = data[offset];
        uint8_t val = _byte & 0x3F;
        uint8_t code = _byte & 0xC0;
        offset += 1;

        if (code > 0) {
            (code == 0x40) ? y += val : x += val;
            continue;
        }

        for (int i = 0; i < val; i++) {
            y += x / w;
            x = x % w;            
            uint32_t _xy = y * w + x;

            output[_xy] = data[offset];
            offset += 1;
            x += 1;
        }
    }
}

extern "C" __declspec(dllexport) void ROM16A_to_color_indexes(uint8_t * data, uint8_t * output, uint32_t data_size, uint32_t w, uint32_t h)
{
    uint32_t x = 0;
    uint32_t y = 0;
    uint32_t offset = 0;    
    while (offset < data_size)
    {        
        uint8_t val = data[offset];
        uint8_t code = data[offset+1];
        offset += 2;

        if (code > 0) {
            (code == 0x40) ? y += val : x += val;
            continue;
        }

        for (uint32_t i = 0; i < val; i++) {
            y += x / w;
            x = x % w;            
            uint32_t _xy = y * w + x;
                                          
            uint32_t raw = data[offset] + (data[offset + 1] << 8);
            uint8_t idx = (raw >> 1) & 0xFF;
            uint8_t alpha = ((raw >> 9) & 0b1111) * 0x11;
            output[_xy * 2] = idx;
            output[_xy * 2 + 1] = alpha;
            offset += 2;
            x += 1;
        }
    }
}
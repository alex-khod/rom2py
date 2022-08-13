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

extern "C" __declspec(dllexport) void to_colors(char* data, char* output, int data_size, int w, int h, int x0, int y0, bool x_flip)
{
    int x = 0;
    int y = 0;
    int offset = 0;
    while (offset < data_size)
    {
        int _byte = data[offset];
        int val = _byte & 0x3f;
        int code = _byte & 0xc0;
        offset += 1;

        if (code > 0) {
            (code == 0x40) ? y += val : x += val;
            continue;
        }

        for (int i = 0; i < val; i++) {
            y += x / w;
            x = x % w;
            int target_x = x_flip ? w - 1 - x0 - x : x0 + x;
            output[(y0 + y) * w + target_x] = data[offset];
            offset += 1;
            x += 1;
        }
    }
}
#include <python2.7/Python.h>
#include <stdio.h>
#include <SDL/SDL.h>

typedef struct {
    int x, y;
    int w, h;
}GAME_Rect;

typedef struct
{
    PyObject_HEAD
    SDL_Overlay *cOverlay;
    GAME_Rect cRect;
} PyGameOverlay;

typedef struct
{
    unsigned char a;
    unsigned char y;
    unsigned char u;
    unsigned char v;
} YUVimg;

static PyObject* Overlay_Display (PyObject *self, PyObject *args)
{
    // Parse data params for frame
    PyGameOverlay* overlay;
    int l_yuv;
    int l_img;
    int y;
    int x;
    int size_to_read;
    Py_buffer yuv;
    YUVimg* img = 0;
    unsigned char* src_y = 0;
    unsigned char* src_u = 0;
    unsigned char* src_v = 0;
    unsigned char* dst_y = 0;
    unsigned char* dst_u = 0;
    unsigned char* dst_v = 0;
    SDL_Rect cRect;

    if (PyTuple_Size (args))
    {
        if (!PyArg_ParseTuple (args, "(Os*s#)", &overlay, &yuv, &img, &l_img))
        {
            return NULL;
        }
    }

    src_y = yuv.buf;
    src_u = yuv.buf;
    src_u += overlay->cOverlay->h * overlay->cOverlay->w;
    src_v = yuv.buf;
    src_v += overlay->cOverlay->h * overlay->cOverlay->w * 5 / 4;

    SDL_LockYUVOverlay (overlay->cOverlay);
    dst_y = overlay->cOverlay->pixels[0];
    dst_v = overlay->cOverlay->pixels[1];
    dst_u = overlay->cOverlay->pixels[2];

    if (!l_img)
    {
        for (y = 0; y < overlay->cOverlay->h; ++y)
        {
            memcpy (dst_y, src_y, overlay->cOverlay->w);
            src_y += overlay->cOverlay->w;
            dst_y += overlay->cOverlay->pitches[0];

            if (y & 1)
            {
                size_to_read = (overlay->cOverlay->w  * overlay->cOverlay->h / 4) * 2 / overlay->cOverlay->h;

                memcpy (dst_u, src_u, size_to_read);
                src_u += overlay->cOverlay->pitches[1];
                dst_u += overlay->cOverlay->pitches[1];

                memcpy (dst_v, src_v, size_to_read);
                src_v += overlay->cOverlay->pitches[2];
                dst_v += overlay->cOverlay->pitches[2];
            }
        }
    }
    else
    {
        for (y = 0; y < overlay->cOverlay->h; ++y)
        {
            for (x = 0; x < overlay->cOverlay->w; ++x)
            {
                if (img->a)
                {
                    *dst_y = img->y;
                    if ((y & 1) && (x & 1))
                    {
                        *dst_u = img->u;
                        *dst_v = img->v;

                        ++src_u;
                        ++dst_u;
                        ++src_v;
                        ++dst_v;
                    }
                }
                else
                {
                    *dst_y = *src_y;
                    //if (!(pos & 3)) // equals if (pos % 4 ==0)
                    if ((y & 1) && (x & 1))
                    {
                        *dst_u = *src_u;
                        *dst_v = *src_v;

                        ++src_u;
                        ++dst_u;
                        ++src_v;
                        ++dst_v;
                    }
                }
                ++src_y;
                ++dst_y;
                ++img;
            }
        }
    }

    SDL_UnlockYUVOverlay (overlay->cOverlay);
    PyBuffer_Release(&yuv);

    cRect.x = overlay->cRect.x;
    cRect.y = overlay->cRect.y;
    cRect.w = overlay->cRect.w;
    cRect.h = overlay->cRect.h;
    SDL_DisplayYUVOverlay(overlay->cOverlay, &cRect);

    Py_RETURN_NONE;
}

static PyObject *yuv2rgb(PyObject *self, PyObject *args) {
    Py_buffer      inBuf, outBuf;
    short          row, col, r, g, b, w, h, rd, gd, bd;
    unsigned char *rgbPtr, *yPtr, y;
    signed char   *uPtr, *vPtr, u, v;

    if(!PyArg_ParseTuple(args, "s*s*hh", &inBuf, &outBuf, &w, &h))
        return NULL;

    if(w & 31) w += 32 - (w & 31); // Round up width to multiple of 32
    if(h & 15) h += 16 - (h & 15); // Round up height to multiple of 16

    rgbPtr = outBuf.buf;
    yPtr   = inBuf.buf;
    uPtr   = (signed char *)&yPtr[w * h];
    vPtr   = &uPtr[(w * h) >> 2];
    w    >>= 1; // 2 columns processed per iteration

    for(row=0; row<h; row++) {
        for(col=0; col<w; col++) {
            // U, V (and RGB deltas) updated on even columns
            u          = uPtr[col] - 128;
            v          = vPtr[col] - 128;
            rd         =  (359 * v)             >> 8;
            gd         = ((183 * v) + (88 * u)) >> 8;
            bd         =  (454 * u)             >> 8;
            // Even column
            y          = *yPtr++;
            r          = y + rd;
            g          = y - gd;
            b          = y + bd;
            *rgbPtr++  = (r > 255) ? 255 : (r < 0) ? 0 : r;
            *rgbPtr++  = (g > 255) ? 255 : (g < 0) ? 0 : g;
            *rgbPtr++  = (b > 255) ? 255 : (b < 0) ? 0 : b;
            // Odd column
            y          = *yPtr++;
            r          = y + rd;
            g          = y - gd;
            b          = y + bd;
            *rgbPtr++  = (r > 255) ? 255 : (r < 0) ? 0 : r;
            *rgbPtr++  = (g > 255) ? 255 : (g < 0) ? 0 : g;
            *rgbPtr++  = (b > 255) ? 255 : (b < 0) ? 0 : b;
        }
        if(row & 1) {
            uPtr += w;
            vPtr += w;
        }
    }

    PyBuffer_Release(&inBuf);
    PyBuffer_Release(&outBuf);

    Py_INCREF(Py_None);
    return Py_None;
}


//########################### PYTHON
static PyMethodDef moduleMethods[] = {
    {"overlay_display", (PyCFunction) Overlay_Display, METH_VARARGS},
    {"yuv2rgb", yuv2rgb, METH_VARARGS},
    {NULL, NULL, 0}
};

PyMODINIT_FUNC initphotobooth(void)
{
    (void) Py_InitModule("photobooth", moduleMethods);
}


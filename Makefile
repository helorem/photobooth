# This is needed only for *compiling* the photobooth.so file (Python module).
# Not needed for just running the Python code with precompiled .so file.

all: photobooth.so

photobooth.so: photobooth.c
	gcc -fPIC -shared -o photobooth.so photobooth.c `pkg-config --cflags --libs python` `pkg-config --cflags --libs sdl` -I/usr/include/SDL

clean:
	find . -iname *.pyc -exec rm -f {} \;
	rm -f photobooth.so

install:
	sudo apt install -y python-pygame python-qrcode python-serial python-dev libsdl-dev

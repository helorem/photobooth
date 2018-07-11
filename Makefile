clean:
	find . -iname "*.pyc" -exec rm -f {} \;

install:
	sudo apt install -y python-pygame python-qrencode python-serial python-dev libsdl-dev

# Photobooth

Here is the software for the photobooth made by Cedric, Jerome-Charles and Romain.

## Run on desktop

To test the software without a photobooth, you can start it on your desktop.

In the configuration file, just set

```
"desktop_mode" : true
```

if you do so, the resolution will be set to 640x480
A fake camera and a fake serial will be used, which print action on the console instead of doing it.

## Make it work on raspberry

First, run

```
sudo raspi-config
```

to enable the camera and the overscan


In the file */boot/config.txt", set the following :

```
overscan_bottom=32
```

It will rajust the screen according to the photobooth.


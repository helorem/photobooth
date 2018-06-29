# Photobooth

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


# Ardexa Demo Application
Demo application for the Ardexa Platform using wxPython. Designed to run on a Raspberry Pi using the Official Touch Screen.

# Dependencies
Requires wxPython, our `read_dht` project and the [Ardexa Agent](https://app.ardexa.com)
```
sudo apt-get install python-wxgtk2.8
```

Once the Ardexa Agent is loaded, replace the default `ardexa.yaml` with the one supplied in this repo. Remember to update the `vhost` option to point to your organization.

# Launch the app
To manually launch the app from the command line
```
./ardexa.py
```

To launch the app from the Desktop, copy the script to the desktop
```
cp ardexa.py ~/Desktop
```
Then double click/tap the icon and select `Execute`.

To have the app launch on boot
```
cp ardexa.py ~/Desktop
echo “@/usr/bin/python /home/pi/Desktop/ardexa.py” >> ~/.config/lxsession/LXDE-pi/autostart
```

# Exit the app
Press `CTRL+Q` to exit the app. **NB** the app must have focus.

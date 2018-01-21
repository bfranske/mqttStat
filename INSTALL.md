# User Installation Instructions
_Note: These instructions are for a Debian based Linux distribution, adapt as required_

1. Ensure python3, git, and supporting packages are installed
    ```
    sudo apt update
    sudo apt install python3 python3-pip git
    sudo pip3 install --upgrade virtualenv
    ```
2.  Download the latest release copy of the software source.
    ```
    cd $HOME
    git clone https://github.com/bfranske/mqttstat.git
    ```
3. Make changes to the mqtt server address (defaults to localhost) and serial port (defaults to /dev/tty-tstat0) as required. These settings are currently found in the setup() function of the mqttStat/mqttStat/cmd_line/mqttStat.py file.

4. Create a user and group to run the daemon. Ensure the user has permissions for the serial port. Serial permissions are typically assigned to the dialout group on Debian based systems.
    ```
    sudo adduser --system mqttstat
    sudo addgroup mqttstat
    sudo adduser mqttstat dialout
    ```
5. Create a directory where the package will be installed and set the ownership and permissions for the user. Switch to the new user to finish the installation.
    ```
    sudo mkdir /opt/mqttStat
    sudo chown mqttstat:mqttstat /opt/mqttStat
    sudo su -s /bin/bash mqttstat
    ```
6. Sandbox the software and it's dependencies in a Python virtual environment and activate it so the software will be installed in this location.
    ```
    cd /opt/mqttStat
    python3 -m venv /opt/mqttStat
    source bin/activate
    ```
7. Install the software from the git cloned (or downloaded) directory.
    ```
    cd $HOME/mqttStat
    pip3 install .
    ```
8. Try running the daemon to ensure it will start and successfully communicate with the thermostat. Once it's running and reporting status back to your screen from the thermostat, stop the process (CTRL-C), deactivate the Python virtual environment, and exit the mqttstat user back to your regular user.
    ```
    mqttStat
    [CTRL-C]
    deactivate
    exit
    ```
9. Edit the init/mqttStat.service file with the installation path (e.g. /opt/mqttStat) and copy it to the system directory. If your system is using something other than systemd, you'll need to use a different file (and commands) than what is provided.
    ```
    cd $HOME/mqttStat
    nano init/mqttStat.service
    [update paths if needed]
    sudo cp init/mqttStat.service /etc/systemd/system/
    ```
10. Reload the systemd service database and attempt to start the mqttStat service. Use the status command to verify the service has started.
    ```
    sudo systemctl --system daemon-reload
    sudo systemctl start mqttStat
    sudo systemctl status mqttStat
    ```
11. If everything looks OK, enable the service to automatically start at system boot time.
    ```
    sudo systemctl enable mqttStat
    ```

# Developer Installation Instructions

_Note: These instructions are for a Debian based Linux distribution, adapt as required_

1. Ensure python3, git, and supporting packages are installed
    ```
    sudo apt update
    sudo apt install python3 python3-pip git
    sudo pip3 install --upgrade virtualenv
    ```
2.  Download the latest release copy of the software source.
    ```
    cd $HOME
    git clone https://github.com/bfranske/mqttstat.git
    ```
3. Make changes to the mqtt server address (defaults to localhost) and serial port (defaults to /dev/tty-tstat0) as required. These settings are currently found in the setup() function of the mqttStat/mqttStat/cmd_line/mqttStat.py file.

4. Create a user and group to run the daemon. Ensure the user has permissions for the serial port. Serial permissions are typically assigned to the dialout group on Debian based systems.
    ```
    sudo adduser --system mqttstat
    sudo addgroup mqttstat
    sudo adduser mqttstat dialout
    ```
5. Change the group owner of the directory holding the git repository to the daemon user. Ensure that user has execute permissions for files as required (scripts/mqttStat comes to mind).
    ```
    sudo chgrp -R mqttstat $HOME/mqttStat
    sudo chmod g+x $HOME/mqttStat/scripts/mqttStat
    ```
6. Sandbox the software and it's dependencies in a Python virtual environment and activate it.
    ```
    cd $HOME/mqttStat
    python3 -m venv venv
    source venv/bin/activate
    ```
7. Install the software from the git cloned (or downloaded) directory.
    ```
    cd $HOME/mqttStat
    pip3 install -e .
    ```
8. Try running the daemon as the mqttstat user to ensure it will start and successfully communicate with the thermostat. Once it's running and reporting status back to your screen from the thermostat, stop the process (CTRL-C), deactivate the Python virtual environment, and exit the mqttstat user back to your regular user.
    ```
    sudo su -s /bin/bash mqttstat
    mqttStat
    [CTRL-C]
    deactivate
    exit
    ```
9. Edit the init/mqttStat.service file with the installation path (e.g. working directory of home/youruser/mqttStat and ExecStart of  /home/youruser/mqttStat/venv/bin/mqttStat) and copy it to the system directory. If your system is using something other than systemd, you'll need to use a different file (and commands) than what is provided.
    ```
    cd $HOME/mqttStat
    nano init/mqttStat.service
    [update paths if needed]
    sudo cp init/mqttStat.service /etc/systemd/system/
    ```
10. Reload the systemd service database and attempt to start the mqttStat service. Use the status command to verify the service has started.
    ```
    sudo systemctl --system daemon-reload
    sudo systemctl start mqttStat
    sudo systemctl status mqttStat
    ```
11. If everything looks OK, enable the service to automatically start at system boot time.
    ```
    sudo systemctl enable mqttStat
    ```

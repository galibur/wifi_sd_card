# wifi_sd_card
# 1. set your operating system wifi configuration to automatically connect to the wifi sd network when available
# 2. start script with : python main.py
#		. script waits until wifi is available 
#		. script periodically tries to reconnect to camera when conection is lost
#		. script always downloads last locally available picture again from wifi sd card  on reconnection to check if last download was corrupted
#		. script can run in backround, e.g. on @reboot in crontab
#		. script runs with user privileges


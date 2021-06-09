# 2021-05-13 
# v0.1

# Wifi-SD-Card connector. 
# Downloads pictures from Wifi-SD Card in Digi-Cam.
# SD-Card IP: 192.168.4.1
# Example image URL: http://192.168.4.1/DCIM/105_PANA/P1050304.JPG

#import pyping
import os
import glob
import urllib
import time
import subprocess
from datetime import datetime
from PIL import Image
import PIL.ExifTags
import signal
import sys
import socket
import json

socket.setdefaulttimeout(15)

class WifiSD:
	def __init__(self):
		self.ip = False
		self.online = False
		self.last_picture_id = False
		self.picture_name_prefix = ""
		self.sd_picture_url = False
		self.local_picture_dir = False
		self.tmp_file = False
		self.min_file_size = False

		self.config_file = "main.cfg"
		self.load_config()

		self.get_last_picture_id()

	def load_config(self):
		print("load_config()")
		f = open(self.config_file)
		data = json.load(f)
		#for i in data['wifi_config']:
			#print("\n" + i)
		self.ip = data['wifi_config']['ip']
		self.last_picture_id = data['wifi_config']['picture_index_start']
		self.picture_name_prefix = data['wifi_config']['picture_name_prefix']
		self.sd_picture_url = data['wifi_config']['picture_url_protocol'] + "://" + self.ip + data['wifi_config']['picture_url']
		self.local_picture_dir = data['wifi_config']['local_picture_directory']
		self.tmp_file = self.local_picture_dir + "tmp.JPG"
		self.min_file_size = data['wifi_config']['min_picture_size']
	
	def get_date_string(self):
		from datetime import datetime

		now = datetime.now()

		current_time = now.strftime("%Y-%m-%d %H:%M:%S")
		return current_time


	

	def ping(self):	
		try:
			subprocess.check_output(["ping", "-c", "1", self.ip])

			if self.online == False:
				print("# " + self.get_date_string() + " : Camera ONLINE")
			
			self.online = True
		except subprocess.CalledProcessError:
			if self.online == True:
				print("# " + self.get_date_string() + " : Camera OFFLINE")
			
			self.online = False


	def get_last_picture_id(self):
		try:
			os.remove(self.tmp_file)
		except:
			''
		list_of_files = glob.glob(self.local_picture_dir + "*.JPG") # * means all if need specific format then *.csv
		if list_of_files:
			latest_file = max(list_of_files, key=os.path.getctime)
			if latest_file != "":
				latest_file = latest_file.split("/")[-1]
				last_id = latest_file.split(".")[0]
				last_id = int(last_id.split("P")[1])
				self.last_picture_id = last_id
				print("# " + self.get_date_string() + " : Last picture id: " + str(last_id))
				return
	 	print("# " + self.get_date_string() + " No pictures in " + self.local_picture_dir + " available! First default picture id is " + str(self.last_picture_id) + ".")
	

	def download_picture(self):
		self.ping()
		if self.online:	
			download_url  = self.sd_picture_url + str(self.last_picture_id) + ".JPG"
			local_file = self.local_picture_dir + "P" + str(self.last_picture_id) + ".JPG"
			#print("#\tDownload URL: " + download_url)
			#print("#\tLocal File: " + local_file)
			#print("# Looking for new pictures ...")
			try:
				urllib.urlretrieve(download_url, self.tmp_file)
			except:
				print("# " + self.get_date_string() + " : Download ERROR")
				return

			local_size = -1
			try:
				local_size = os.path.getsize(local_file)
			except:
				''

			tmp_size = os.path.getsize(self.tmp_file)
		
			#print("#\tlocal size: " + str(local_size))
			#print("#\ttmp size: " + str(tmp_size))

			
			if local_size < tmp_size:
				#print("local_size < tmp_size")
				if tmp_size > self.min_file_size:
					#print("tmp_size > 100KB")
					# local file was not fully downloaded last time -> move new tmp file to local file (overwrite)

					image = Image.open(self.tmp_file)
					exif_data = image._getexif()
					exif = {
						PIL.ExifTags.TAGS[k]:v
						for k, v in image._getexif().items()
						if k in PIL.ExifTags.TAGS
					}			

					date = exif['DateTimeOriginal'].split(" ")[0].replace(":", "-")
					time = exif['DateTimeOriginal'].split(" ")[1].replace(":", "-")
					exif_date = date + "_" + time

					dtg_local_file = self.local_picture_dir + exif_date + "_" + self.picture_name_prefix + str(self.last_picture_id) + ".JPG"

					print("# " + self.get_date_string() + " : NEW PICTURE downloaded: " + dtg_local_file + " (" + str(tmp_size/1000000) + " MB)")
					os.rename(self.tmp_file, dtg_local_file)
					self.last_picture_id = self.last_picture_id + 1
					self.download_picture()
					return
				else:
					#os.remove(tmp_file)
					''
			elif tmp_size == local_size:				
				self.last_picture_id = self.last_picture_id + 1
				print("# " + self.get_date_string() + " : INTEGRITY CHECK of last downloaded picture PASSED: " + local_file + " (" + str(tmp_size/1000000) + " MB)")
				self.download_picture()
				return

		else:
			#print("# OFFLINE: Download not available.")
			''

def signal_handler(sig, frame):
	now = datetime.now()
	current_time = now.strftime("%Y-%m-%d %H:%M:%S")

	print("# " + current_time + " : Program terminated by user (Strg + C).")
	sys.exit(0)


def main():


# check if wifi sd card / hotspot is online
	sd = WifiSD()	

	signal.signal(signal.SIGINT, signal_handler)

	while True:
		sd.download_picture()
		time.sleep(5)



# Main 
if __name__ == "__main__":

		main()


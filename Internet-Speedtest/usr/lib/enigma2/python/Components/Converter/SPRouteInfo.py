from Components.Converter.Converter import Converter
from Components.Element import cached
from os import popen

class SPRouteInfo(Converter, object):
	Info = 0
	Lan = 1
	Wifi = 2
	Vpn = 3
	Modem = 4

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == 'Info':
			self.type = self.Info
		elif type == 'Lan':
			self.type = self.Lan
		elif type == 'Wifi':
			self.type = self.Wifi
		elif type == 'Vpn':
			self.type = self.Vpn
		elif type == 'Modem':
			self.type = self.Modem

	@cached
	def getBoolean(self):
		info = False
		for line in open('/proc/net/route'):
			if self.type == self.Lan and line.split()[0] == 'eth0' and line.split()[3] == '0003':
				info = True
			elif self.type == self.Wifi and (line.split()[0] == 'wlan0' or line.split()[0] == 'ra0') and line.split()[3] == '0003':
				info = True
			elif self.type == self.Modem and line.split()[0] == 'ppp0' and line.split()[3] == '0003':
				info = True
		if self.type == self.Vpn:
			try:
				check_tun = popen("ip tuntap show").read().split()[0]
				if 'tun0:' in check_tun:
					info = True
			except IndexError:
				pass

		return info

	boolean = property(getBoolean)

	@cached
	def getText(self):
		info = ''
		for line in open('/proc/net/route'):
			if self.type == self.Info and line.split()[0] == 'eth0' and line.split()[3] == '0003':
				info = 'lan'
			elif self.type == self.Info and (line.split()[0] == 'wlan0' or line.split()[0] == 'ra0') and line.split()[3] == '0003':
				info = 'wifi'
			elif self.type == self.Info and line.split()[0] == 'ppp0' and line.split()[3] == '0003':
				info = '3g'
		if self.type == self.Vpn:
			try:
				check_tun = popen("ip tuntap show").read().split()[0]
				if 'tun0:' in check_tun:
					info = 'VPN'
			except IndexError:
				pass

		return info

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)

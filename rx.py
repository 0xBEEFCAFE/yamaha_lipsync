#!/usr/bin/python

import rxv
import requests
import xml.etree.ElementTree as ET
import sys
from rxv import ssdp

#https://github.com/wuub/rxv

class RXV2(rxv.RXV):
	def __init__(self):
		
		ctrl_url = "http://192.168.1.248:80/YamahaRemoteControl/ctrl"
		model_name = "RX-V779"
		rxv.RXV.__init__(self, ctrl_url, model_name)
		
		#r = ssdp.discover()[0] # Instead of rxv.find()
		#rxv.RXV.__init__(self, r.ctrl_url, r.model_name)
		
	def SetDelay(self, delay):
		cmd="""<YAMAHA_AV cmd="PUT"><System><Sound_Video><Lipsync><Manual><Analog><Val>%i</Val><Exp>0</Exp><Unit>ms</Unit></Analog><HDMI_OUT_1><Val>%i</Val><Exp>0</Exp><Unit>ms</Unit></HDMI_OUT_1></Manual></Lipsync></Sound_Video></System></YAMAHA_AV>""" % (delay, delay)
	
		self.RunCmd(cmd)
		
	def GetCurrentLipsyncDelay(self):
		cmd = """<YAMAHA_AV cmd="GET">
<System><Sound_Video><Lipsync><Current>GetParam</Current></Lipsync></Sound_Video></System>
</YAMAHA_AV>"""

		response = self.RunCmd(cmd)
		return int(response.find("System/Sound_Video/Lipsync/Current/Info/Total_Delay_Info/Val").text)
		
	def GetLipsyncMode(self):
		cmd = """<YAMAHA_AV cmd="GET">
<System><Sound_Video><Lipsync><Mode>GetParam</Mode></Lipsync></Sound_Video></System>
</YAMAHA_AV>"""
		
		response = self.RunCmd(cmd)
		return response.find("System/Sound_Video/Lipsync/Mode").text
		
	def RunCmd(self, cmd):
		res = requests.post(self.ctrl_url, data=cmd, headers={"Content-Type": "text/xml"})
		response = ET.XML(res.content)
		if response.get("RC") != "0":
			raise rxv.ReponseException(res.content)
		return response
		
rx = RXV2()
print "Connected to %s (answer 'x' to exit)." % rx.model_name
print "Current delay is %i ms" % rx.GetCurrentLipsyncDelay()
delay = ""
while delay.lower() != "x":
	delay = raw_input("Enter new Lipsync delay in ms: ")
	if delay.isdigit():
		d = int(delay)
		if 0 <= d <= 500:
			rx.SetDelay(d)
			print "Success! Lipsync delay set to %i ms" % rx.GetCurrentLipsyncDelay()
		else:
			print "Sorry, delay must only be a number between 0-500 ms."
	else:
		if delay.lower() != "x":
			print "Sorry, either enter a delay in ms or 'x' to exit."

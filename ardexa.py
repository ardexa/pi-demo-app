#!/usr/bin/python

# Written by Ardexa Pty Ltd for a demo for the Ardexa IoT
# Based on C++ code by Thomas Monjalon and Daniel Eloff
#
# Need the wxlibs: sudo apt-get install python-wxgtk2.8
#
# How it works
#	1.	The text control will append the string to the file "to_cloud_file"
#		So the Ardexa agent will need to 'tail' from this file
#	2.	The slider will read a number (temperature) from the file "temperature_file"
#		So the Ardex agent will need a 'run' to write to this file, based on the sensor value.
#		Suggest a task every 5 seconds. The same for humidity.
#	3.	The buttons simulate a door. It will write a "1" (open) or "0" (closed) to
#		the "door_file". So the Ardexa agent will need to 'tail' from this file
#  4.	To update the "from_cloud", write (don't append) to the file: 'from_cloud_file'
#		Don't write more than about 15 chars
#	5.	To update the LED, write "0", "1" or "2" to the file "LED_status_file"
#	6.	To update the picture area, put a new jpg file in /tmp/picture.
#		Preferred size is 300x150.

import wx
import os.path
import random

to_cloud_file = "/tmp/to_cloud"
temperature_file = "/tmp/temperature"
humidity_file = "/tmp/humidity"
door_file = "/tmp/door"
from_cloud_file = "/tmp/from_cloud"
LED_status_file = "/tmp/LED"
picture_file = "/tmp/picture.jpg"

# These are random entries for the "to cloud" text box
sentences = [   'Ardexa implements a full IoT platform', 
                'Ardexa sends all data via TLS security', 
                'Ardexa enables remote control',
                'Ardexa enables file transfers',
                'Ardexa uses full client certificates',
                'Ardexa implements command scheduling'
             ]


class LED(wx.Control):
	def __init__(self, parent, id=-1, colors=[wx.Colour(220, 10, 10), wx.Colour(250, 200, 0), wx.Colour(10, 220, 10)],pos=(-1,-1), style=wx.ALL):
		size = (17, 17)
		wx.Control.__init__(self, parent, id, pos, size, style)
		self.MinSize = size  
		self._colors = colors
		self._state = -1
		self.SetState(0)
		self.Bind(wx.EVT_PAINT, self.OnPaint, self)
        
	def SetState(self, i):
		if i < 0:
			raise ValueError, 'Cannot have a negative state value.'
		elif i >= len(self._colors):
			raise IndexError, 'There is no state with an index of %d.' % i
		elif i == self._state:
			return
        
		self._state = i
		base_color = self._colors[i]
		light_color = self.change_intensity(base_color, 1.15)
		shadow_color = self.change_intensity(base_color, 1.07)
		highlight_color = self.change_intensity(base_color, 1.25)
        
		ascii_led = '''
		000000-----000000      
		0000---------0000
		000-----------000
		00-----XXX----=00
		0----XX**XXX-===0
		0---X***XXXXX===0
		----X**XXXXXX====
		---X**XXXXXXXX===
		---XXXXXXXXXXX===
		---XXXXXXXXXXX===
		----XXXXXXXXX====
		0---XXXXXXXXX===0
		0---=XXXXXXX====0
		00=====XXX=====00
		000===========000
		0000=========0000
		000000=====000000
      '''.strip()
        
		xpm = ['17 17 5 1', # width height ncolors chars_per_pixel
			'0 c None', 
			'X c %s' % base_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii'),
			'- c %s' % light_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii'),
			'= c %s' % shadow_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii'),
			'* c %s' % highlight_color.GetAsString(wx.C2S_HTML_SYNTAX).encode('ascii')]
        
		xpm += [s.strip() for s in ascii_led.splitlines()]        
		self.bmp = wx.BitmapFromXPMData(xpm)
		self.Refresh()
        
	def GetState(self):
		return self._state
    
	State = property(GetState, SetState)
    
	def OnPaint(self, e):
		dc = wx.PaintDC(self)
		dc.DrawBitmap(self.bmp, 0, 0, True)
  

	def change_intensity(self,color, fac):
		rgb = [color.Red(), color.Green(), color.Blue()]
		for i, intensity in enumerate(rgb):
			rgb[i] = min(int(round(intensity*fac, 0)), 255)
		     
		return wx.Color(*rgb)  

class Ardexa(wx.Frame): 
   
	def __init__(self, parent, title): 
		super(Ardexa, self).__init__(parent, title = title, size = (480, 380)) 

		self.InitUI()
		self.Centre() 
		# Fullscreen
		self.ShowFullScreen(True)
		# Maximize
		#self.Show()
		#self.Maximize(True)
		self.last_index = -1

	def onKey(self, event):
		"""
		Check for CTRL+Q key press and exit if CTRL+Q is pressed
		"""
		key_code = event.GetKeyCode()
		# ESC
		#if key_code == wx.WXK_ESCAPE:
		# CRTL + Q
		if key_code == 17:
			self.Close()
		else:
			event.Skip()

	def InitUI(self): 
		# Define a panel and boxsizer
		panel = wx.Panel(self)
		self.Bind(wx.EVT_CHAR_HOOK, self.onKey)
		vbox = wx.BoxSizer(wx.VERTICAL)
	
		
		# 1st row widgets
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		to_cloud = wx.StaticText(panel, label = "Text to the Cloud\t\t")
		hbox1.Add(to_cloud, flag = wx.ALL, border = 5)
		self.text_ctrl1 = wx.TextCtrl(panel, style = wx.TE_PROCESS_ENTER)
		hbox1.Add(self.text_ctrl1, proportion=1, flag = wx.EXPAND|wx.ALL, border = 5)
		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=5)
		
		# 2nd row widgets
		vbox.Add((-1, 5))
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		from_cloud = wx.StaticText(panel, label = "Text from the Cloud\t")
		hbox2.Add(from_cloud, flag = wx.ALL, border = 5)
		self.text_ctrl2 = wx.TextCtrl(panel, value = "",style = wx.TE_READONLY)
		hbox2.Add(self.text_ctrl2, proportion=1, flag = wx.EXPAND|wx.ALL, border = 5)
		vbox.Add(hbox2, flag=wx.EXPAND|wx.ALL, border=5)

		# 3rd row widgets
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		front_door = wx.StaticText(panel, label = "Front Door\t\t\t")
		hbox3.Add(front_door, flag = wx.ALL, border = 5)
		self.button1 = wx.Button(panel,-1,"open")
		hbox3.Add(self.button1, flag = wx.ALL, border = 5)
		self.button2 = wx.Button(panel,-1,"close")
		hbox3.Add(self.button2, flag = wx.ALL, border = 5)
		vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=5)
		
		# 4th row widgets
		vbox.Add((-1, 5))
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		temp_static = wx.StaticText(panel, label = "Temperature Sensor\t\t")
		hbox4.Add(temp_static, flag = wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border = 5)
		self.slider1 = wx.Slider(panel, value = 10, minValue = -10, maxValue = 50,style = wx.SL_HORIZONTAL|wx.SL_LABELS) 
		hbox4.Add(self.slider1, proportion=1, flag = wx.EXPAND|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL, border = 25)
		no_text1 = wx.StaticText(panel, label = "     ")
		hbox4.Add(no_text1, flag = wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border = 5)
		vbox.Add(hbox4, flag=wx.EXPAND|wx.RIGHT, border=15)

		# 5th row widgets
		vbox.Add((-1, 5))
		hbox5 = wx.BoxSizer(wx.HORIZONTAL)
		hum_static = wx.StaticText(panel, label = "Humidity Sensor\t\t\t")
		hbox5.Add(hum_static, flag = wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border = 5)
		self.slider2 = wx.Slider(panel, value = 10, minValue = 0, maxValue = 100,style = wx.SL_HORIZONTAL|wx.SL_LABELS) 
		hbox5.Add(self.slider2, proportion=1, flag = wx.EXPAND|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL, border = 25)
		no_text2 = wx.StaticText(panel, label = "     ")
		hbox5.Add(no_text2, flag = wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border = 5)
		vbox.Add(hbox5, flag=wx.EXPAND|wx.RIGHT, border=15)

		# 6th row widgets
		vbox.Add((-1, 5))
		hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		img = wx.EmptyImage(120,121)
		self.image_ctrl1 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img))
		hbox6.Add(self.image_ctrl1, proportion=2, flag = wx.ALL|wx.ALIGN_CENTER, border = 5)
		self.LED1 = LED(panel)
		hbox6.Add(self.LED1, flag = wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER, border = 5)
		vbox.Add(hbox6, flag=wx.ALL|wx.ALIGN_CENTER, border=5)

		panel.SetSizer(vbox)
		
		# Bindings
		self.text_ctrl1.Bind(wx.EVT_TEXT_ENTER,self.OnEnterPressed)
		self.button1.Bind(wx.EVT_BUTTON, self.OnButtonClick)
		self.button2.Bind(wx.EVT_BUTTON, self.OnButtonClick)
		self.text_ctrl1.Bind(wx.EVT_LEFT_DOWN,self.OnTextMouse)

		# Make a call for the future
		wx.FutureCall(500, self.poll_task)

	def poll_task(self):
		# read the "from_cloud" file and update the text control box
		try:
			read_file = open(from_cloud_file,"r")
			for line in read_file:
				str_from_cloud = line

			self.text_ctrl2.SetValue(str_from_cloud.strip())
			read_file.close()
		except:
			pass

		# read the LED status file
		try:
			LED_file = open(LED_status_file,"r")
			LED_status = LED_file.read(1)
			self.LED1.SetState(int(LED_status))
			LED_file.close()
		except:
			pass
	
		# Update the image
		if (os.path.isfile(picture_file)):
			try:
				Img = wx.Image(picture_file, wx.BITMAP_TYPE_JPEG)
				self.image_ctrl1.SetBitmap(wx.BitmapFromImage(Img))
				self.Refresh()
			except: 	
				pass

		# Set the temperature slider
		try:
			read_file = open(temperature_file,"r")
			read_str = read_file.read()
			read_str = read_str.strip()
			# convert the string to a number
			read_int = int(float(read_str))
			if ((read_int >= 0) or (read_int < 101)):
				self.slider1.SetValue(read_int)
			read_file.close()
		except:
			pass		

		# Set the humidity slider
		try:
			read_file = open(humidity_file,"r")
			read_str = read_file.read()
			read_str = read_str.strip()
			# convert the string to a number
			read_int = int(float(read_str))
			if ((read_int >= 0) or (read_int < 101)):
				self.slider2.SetValue(read_int)
			read_file.close()
		except:
			pass		

		# Make the next future call
		wx.FutureCall(500, self.poll_task)
		
	def OnEnterPressed(self,event): 
		write_str = event.GetString() 

		# Clear the text control screen
		self.text_ctrl1.SetValue("")

		# write the string to the log file
		write_file = open(to_cloud_file,"a")
		write_file.write(write_str + "\n")
		write_file.close()
		
		
	def OnButtonClick(self, event):
		label = event.GetEventObject().GetLabel()
		# write the string to the log file
		write_file = open(door_file,"a")
		if (label == 'open'):
			write_file.write("1\n")
		elif (label == 'close'):
			write_file.write("0\n")
		write_file.close()

	def OnTextMouse(self,event):
		random_index = -1
		while random_index < 0 or random_index == self.last_index:
			random_index = random.randint(0,len(sentences)-1)
		sentence = sentences[random_index]
		self.last_index = random_index;
		print sentence
		self.text_ctrl1.SetValue(sentence)

		# write the string to the log file
		write_file = open(to_cloud_file,"a")
		write_file.write(sentence + "\n")
		write_file.close()

#######################################################################################

# End of funtions and classes. Start of main

app = wx.App() 
Ardexa(None, title = 'Ardexa IoT Demo') 
app.MainLoop()


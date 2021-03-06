#
# Trails
#
# Show draws horizontal trails from front to back that slowly fade
# 
# Background is controlled by Touch OSC
# 

import sheep
from random import randint, choice
from color import RGB, HSV
            
# Converts a 0-1536 color into rgb on a wheel by keeping one of the rgb channels off

def Wheel(color):
	color = color % 1536  # just in case color is out of bounds
	channel = color / 255
	value = color % 255
	
	if channel == 0:
		r = 255
		g = value
		b = 0
	elif channel == 1:
		r = 255 - value
		g = 255
		b = 0
	elif channel == 2:
		r = 0
		g = 255
		b = value
	elif channel == 3:
		r = 0
		g = 255 - value
		b = 255
	elif channel == 4:
		r = value
		g = 0
		b = 255
	else:
		r = 255
		g = 0
		b = 255 - value
	
	return RGB(r,g,b)

# Interpolates between colors. Fract = 1 is all color 2
def morph_color(color1, color2, fract):
	morph_h = color1.h + ((color2.h - color1.h) * fract)
	morph_s = color1.s + ((color2.s - color1.s) * fract)
	morph_v = color1.v + ((color2.v - color1.v) * fract)
	
	return HSV(morph_h, morph_s, morph_v)
	
class Fader(object):
	def __init__(self, sheep, cell, decay):
		self.sheep = sheep
		self.cell = cell
		self.decay = decay
		self.life = 1.0
	
	def draw_fader(self, fore_color, back_color):
		adj_color = morph_color(back_color, fore_color, self.life)
		self.sheep.set_cell(self.cell, adj_color)
	
	def age_fader(self):
		self.life -= self.decay
		if self.life > 0:
			return True	# Still alive
		else:
			return False	# Life less than zero -> Kill

class Path(object):
	def __init__(self, sheep, trajectory):
		self.sheep = sheep
		self.faders = []	# List that holds fader objects
		self.pos = 0
		self.decay = 1.0 / randint(2,6)	# Adjust
		self.trajectory = trajectory				
		self.length = len(self.trajectory)
		
		new_fader = Fader(self.sheep, self.trajectory[0], self.decay)
		self.faders.append(new_fader)
	
	def draw_path(self, foreground, background):
		for f in self.faders:
			f.draw_fader(foreground, background)
		for f in self.faders:
			if f.age_fader() == False:
				self.faders.remove(f)
	
	def path_alive(self):
		if len(self.faders) > 0:
			return True
		else:
			return False
			
	def move_path(self):
		if self.pos < (self.length - 1):
			self.pos += 1
			new_fader = Fader(self.sheep, self.trajectory[self.pos], self.decay)
			self.faders.append(new_fader)
			
class Trails(object):
	def __init__(self, sheep_sides):
		self.name = "Trails"
		self.sheep = sheep_sides.both
		self.paths = []	# List that holds paths objects
		self.max_paths = 3
		self.trajectories = (sheep.LOW, sheep.MEDIUM, sheep.HIGH)
		self.foreground = randint(0,1536)	# Path color
		self.background  = RGB(255, 255, 255) # Override with Touch OSC
		
		self.speed = 0.05
		
	def set_param(self, name, val):
		# name will be 'colorR', 'colorG', 'colorB'

		rgb255 = int(val * 0xff)
		if name == 'colorR':
			self.background.r = rgb255
		elif name == 'colorG':
			self.background.g = rgb255
		elif name == 'colorB':
			self.background.b = rgb255
							
	def next_frame(self):	
					
		while (True):
			
			while len(self.paths) < self.max_paths:
				new_path = Path(self.sheep, self.trajectories[randint(0,2)])
				self.paths.append(new_path)
			
			# Set background cells

			self.sheep.set_all_cells(self.background)						
			
			# Draw paths
				
			for p in self.paths:
				p.draw_path(Wheel(self.foreground), self.background)
				p.move_path()
			for p in self.paths:
				if p.path_alive() == False:
					self.paths.remove(p)
				
			# Cycle the foreground color
			
			self.foreground += 1
			if self.foreground > 1536:
				self.foreground -= 1536
			
			yield self.speed
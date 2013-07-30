#!/usr/bin/env python
#-*- coding: utf-8 -*-

""" Program to show bezier curves
"""


from __future__ import print_function

import copy
import pygame
import random

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

	def __str__(self):
		return "(" + str(self.x) + ", " + str(self.y) + ")"

	def __add__(self, other):
		return Point(self.x + other.x, self.y + other.y)

	def __neg__(self):
		return Point(-self.x, -self.y)

	def __sub__(self, other):
		return Point(self.x - other.x, self.y - other.y)

	def __mul__(self, val):
		return Point(self.x * val, self.y * val)

	def __rmul__(self, val):
		return Point(self.x * val, self.y * val)

	def __div__(self, val):
		return Point(self.x / val, self.y / val)


class BezCurve(object):
	def __init__(self, points = []):
		self.points = [points]

	def __str__(self):
		res = "points : " + str(len(self.points[0]))

		for p in self.points:
			res += "\n" + str(p)
		return res

	def get_segments(self, step):
		B = []
		for s in frange(0.0, 1.0, step):
			points = copy.deepcopy(self.points)
			for i in xrange(len(points[0]) - 1):
				points.append([])

				# shorcut of speed
				points_i = points[i]

				for p in xrange(len(points_i) - 1):
					new_point = points_i[p] + s * (points_i[p + 1] - points_i[p])

				#for p in xrange(len(points[i]) - 1):
				#	new_point = points[i][p] + s * (points[i][p + 1] - points[i][p])
					points[i + 1].append(new_point)
			B.append(points[len(points) - 1][0])

		#for _i in B:
		#	print str(_i)
		#print "\n"
		return B

class QuadCurve(object):
	def __init__(self, p0=Point(), p1=Point(), p2=Point()):
		self.P0 = p0
		self.P1 = p1
		self.P2 = p2

	def __str__(self):
		return "[" + str(self.P0) + ", "+ str(self.P1) + ", "+ str(self.P2) + "]"


	def get_segments(self, step):
		self.B = []

		for i in frange(0.0, 1.0, step):
			self.Q0 = self.P0 + i * (self.P1 - self.P0)
			self.Q1 = self.P1 + i * (self.P2 - self.P1)

			B = self.Q0 + i * (self.Q1 - self.Q0)
			self.B.append(B)

		return self.B
		
def frange(start, stop, step):
	v = start
	while v < stop:
		yield v
		v += step

class BezViewer(object):
	def __init__(self):
		self.zoom = 1.0 * 2 ** 6
		self.quadCurves = []

		self.running = True
		self.selected_point = None
		self.clock = pygame.time.Clock()



		pygame.init()
		self.window = pygame.display.set_mode((640, 480))
		self.screen = pygame.display.get_surface()

		# Font
		self.font = pygame.font.Font(None, 20)

		self.background = pygame.Surface(self.screen.get_size()).convert()
		self.background.fill((0, 0, 0))
		pygame.display.flip()
		

	def draw(self):
		self.clock.tick()
		self.screen.blit(self.background, (0,0))
		fps_label = self.font.render("FPS: " + str(self.clock.get_fps()), 1, (255,255,255))
		objects_count_label = self.font.render("Bezier Curves: " + str(len(self.quadCurves)), 1, (255,255,255))

		self.screen.blit(fps_label,(0,0))
		self.screen.blit(objects_count_label,(0,20))

		for c in self.quadCurves:
			for point in c.points[0]:
				p = point * self.zoom
				if point is self.selected_point:
					pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(p.x - 3, p.y - 3, 6, 6))
				else:
					pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(p.x - 3, p.y - 3, 6, 6))

			segments = c.get_segments(0.01)

			for i in range(len(segments) - 1):
				A = segments[i]
				B = segments[i + 1]

				A = A * self.zoom
				B = B * self.zoom

				pygame.draw.line(self.screen, (255, 255, 255), (A.x, A.y), (B.x, B.y))
				#time.sleep(0.05)
		pygame.display.flip()

	def mouse_hover(self, point, pos):
		z = self.zoom

		if point.x * z - 3 < pos[0] and point.x * z + 3 > pos[0] and point.y * z - 3 < pos[1] and point.y * z + 3 > pos[1]:
			print("Selected :" + str(point))
			return True
		return False

	def move_selected(self, pos):
		self.selected_point.x = pos[0] / self.zoom
		self.selected_point.y = pos[1] / self.zoom

	def run(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				if event.type == pygame.MOUSEMOTION:
					if self.selected_point is not None:
						self.move_selected(event.pos)
				if event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						# LMB
						self.selected_point = None
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						# LMB
						for bez in self.quadCurves:
							#for point in bez.P0, bez.P1, bez.P2:
							for point in bez.points[0]:
								if self.mouse_hover(point, event.pos):
									self.selected_point = point
					if event.button == 3:
						p = Point(event.pos[0] / self.zoom, event.pos[1] / self.zoom)
						self.quadCurves[0].points[0].append(p)
					if event.button == 5:
						# Wheel down
						self.zoom *= 2.0
					if event.button == 4:
						# Wheel up
						self.zoom /= 2.0
			# End events
			self.draw()
			

random.seed()

bezViewer = BezViewer()

#for i in xrange(1):
#	P0 = Point(random.randrange(0, 10), random.randrange(0, 10))
#	P1 = Point(random.randrange(0, 10), random.randrange(0, 10))
#	P2 = Point(random.randrange(0, 10), random.randrange(0, 10))
#
#	bez = QuadCurve(P0, P1, P2)
#	bezViewer.quadCurves.append(bez)

P0 = Point(2,2)
P1 = Point(1,1)
P2 = Point(2,1)
P3 = Point(3,2)

bezCurve = BezCurve([P0, P1, P2, P3])


bezViewer.quadCurves.append(bezCurve)


bezViewer.run()

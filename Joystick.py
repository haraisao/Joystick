#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
 Simple JoystickRtc with Python
 Copyright(C) 2019, Isao Hara, AIST
 License: MIT
'''

from __future__ import print_function
import sys

import pygame
from pygame.locals import *
import numpy


###################################################
#
class Joystick(object):
  def __init__(self):
    self.deadzone=1e-4
    self.button_press_callback=None
    self.button_release_callback=None
    self.axis_callback=None
    self.hat_callback=None
    self.loop_flag=True
    pygame.joystick.init()
  #
  #
  def init(self, n=0, deadzone=0.05, autorepeat_rate=0.0):
    self.joy_id = n
    self.deadzone = deadzone
    self.repeat_rate=autorepeat_rate
    self.joy = pygame.joystick.Joystick(n)
    self.joy.init()

    self.name = self.joy.get_name()
    self.n_buttons = self.joy.get_numbuttons()
    self.n_axes = self.joy.get_numaxes()
    self.n_hats = self.joy.get_numhats()
    self.show_info()


    self.repeat_axes = False
    self.repeat_hats = False
    self.repeat_buttons = False

    self.buttons = [ 0 for x in range(self.n_buttons)]
    self.axes = [0 for x in range(self.n_axes)]
    self.hats = [(0, 0) for x in range(self.n_hats)]


  #
  #
  def show_info(self):
    print( 'Joystick name: ' , self.name )
    print( 'Num of buttons : ' , self.n_buttons )
    print( 'Num of sticks  : ' , self.n_axes )
    print( 'Num of hats  : ' , self.n_hats )

  #######################################
  #
  def get_axes(self):
    for n in range(self.n_axes):
      v=self.joy.get_axis(n)
      if abs(v) < self.deadzone: self.axes[n] = 0
      else: self.axes[n] = v
    return self.axes

  #
  #
  def get_buttons(self):
    self.buttons = [self.joy.get_button(x) for x in range(self.n_buttons)]
    return self.buttons

  #
  #
  def get_hats(self):
    for n in range(self.n_hats):
      self.hats[n] = self.joy.get_hat(n)
    return self.hats

  #########################################
  #
  def is_axes_released(self):
    return ( numpy.max(self.axes) == 0  and numpy.min(self.axes) == 0 )

  #
  #
  def is_buttons_released(self):
    return (numpy.max(self.buttons) == 0)

  #
  #
  def is_hats_released(self):
    for n in range(self.n_hats):
      if self.hats[n] != (0,0) : return False
    return True

  #
  # Repeat events
  def start_repeat_event(self, etype):
    if self.repeat_rate > 0: 
        pygame.time.set_timer(etype, self.repeat_rate)
        return True
    return False

  def stop_repeat_event(self, etype):
    pygame.time.set_timer(etype, 0)
    return False
  
  #
  #
  def process_event(self):
    for e in pygame.event.get():
      ###   AXES
      if e.type == pygame.locals.JOYAXISMOTION:
        self.get_axes()
        if self.is_axes_released() : self.repeat_axes = self.stop_repeat_event(e.type)
        else:
          if self.axis_callback:  self.axis_callback(self)
          if not self.repeat_axes: self.repeat_axes=self.start_repeat_event(e.type)
      ### HATS
      elif e.type == pygame.locals.JOYHATMOTION:
        self.get_hats()
        if self.is_hats_released(): self.repeat_hats = self.stop_repeat_event(e.type)
        else:
          if self.hat_callback:  self.hat_callback(self)
          if not self.repeat_hats: self.repeat_hats = self.start_repeat_event(e.type)
      ### BUTTONS
      elif e.type == pygame.locals.JOYBUTTONDOWN: 
        self.get_buttons()
        if self.button_press_callback:  self.button_press_callback(self)
        if not self.repeat_buttons: self.repeat_buttons = self.start_repeat_event(e.type)
      elif e.type == pygame.locals.JOYBUTTONUP:
        self.get_buttons()
        if self.button_release_callback:  self.button_release_callback(self, e.button)
        if self.is_buttons_released(): self.repeat_buttons =self.stop_repeat_event(pygame.locals.JOYBUTTONDOWN)
      ### Unknown
      else:
        if e.type == 12: self.loop_flag = False
        print( e )

  #
  #
  def get_flag(self):
    return self.loop_flag
  #
  #
  def set_flag(self, v):
    self.loop_flag=v
    return self.loop_flag

#####################################
#  Callback functions...
def axes_func(joy):
  v = joy.axes[1] * 200
  lv = rv = -v

  tsp = joy.axes[2]
  if tsp < 0 :
    if rv > 0:
      rv += tsp*abs(rv)*2
    elif rv <0:
      rv -= tsp*abs(rv)*2
  elif tsp > 0 :
    if lv > 0:
      lv -= tsp*abs(lv)*2
    elif lv <0:
      lv += tsp*abs(lv)*2

  print ( int(lv), int(rv) )
  print("AXES", joy.axes)
#
#
def hat_func(joy):
  print(joy.hats)
#
#
def button_func(joy):
  print('down', joy.buttons)

###############################
#
def main(intval=0):
  joy = Joystick()
  joy.init(0, autorepeat_rate=intval)

  ### set Callback
  joy.axis_callback=axes_func
  joy.hat_callback=hat_func
  joy.button_press_callback=button_func
  
  ## Event Loop
  pygame.init()
  while joy.get_flag() :
    pygame.time.wait(30)
    joy.process_event()

if __name__ == '__main__':
  intval=0
  if len(sys.argv) > 1:
    intval=int(sys.argv[1])
  main(intval)

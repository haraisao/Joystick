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
    self.MIN_VAL=1e-4
    self.button_press_callback=None
    self.button_release_callback=None
    self.axis_callback=None
    self.hat_callback=None
    self.time_intval=0
    self.loop_flag=True
  #
  #
  def init(self, n=0):
    self.joy_id = n
    pygame.joystick.init()
    self.joy = pygame.joystick.Joystick(n)
    self.joy.init()

    self.name = self.joy.get_name()
    self.n_buttons = self.joy.get_numbuttons()
    self.n_axes = self.joy.get_numaxes()
    self.n_hats = self.joy.get_numhats()
    self.info()
    pygame.init()

    self.buttons = [ 0 for x in range(self.n_buttons)]
    self.axes = [0 for x in range(self.n_axes)]
    self.hats = [(0, 0) for x in range(self.n_hats)]

  #
  #
  def info(self):
    print( 'Joystick name: ' , self.name )
    print( 'Num of buttons : ' , self.n_buttons )
    print( 'Num of sticks  : ' , self.n_axes )
    print( 'Num of hats  : ' , self.n_hats )

  #
  #
  def get_axes(self):
    for n in range(self.n_axes):
      v=self.joy.get_axis(n)
      if abs(v) < self.MIN_VAL: self.axes[n] = 0
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

  #
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
  #
  def process_event(self):
    for e in pygame.event.get():

      if e.type == pygame.locals.JOYAXISMOTION:
        self.get_axes()
        if self.is_axes_released() :
          pygame.time.set_timer(pygame.locals.JOYAXISMOTION, 0)
        else:
          if self.axis_callback:  self.axis_callback(self)
          pygame.time.set_timer(pygame.locals.JOYAXISMOTION, self.time_intval)

      elif e.type == pygame.locals.JOYHATMOTION:
        self.get_hats()

        if self.is_hats_released(): 
          pygame.time.set_timer(pygame.locals.JOYHATMOTION, 0)
        else:
          if self.hat_callback:  self.hat_callback(self)
          pygame.time.set_timer(pygame.locals.JOYHATMOTION, self.time_intval)
        
      elif e.type == pygame.locals.JOYBUTTONDOWN: 
        self.get_buttons()
        if self.button_press_callback:  self.button_press_callback(self)

        pygame.time.set_timer(pygame.locals.JOYBUTTONDOWN,  self.time_intval)
        
      elif e.type == pygame.locals.JOYBUTTONUP:
        self.get_buttons()
        if self.button_release_callback:  self.button_release_callback(self, e.button)
        if self.is_buttons_released():
          pygame.time.set_timer(pygame.locals.JOYBUTTONDOWN, 0)

      else:
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

  #
  #
  def get_intval(self):
    return self.time_intval

  #
  #
  def set_intval(self, v):
    self.time_intval=v
    return self.time_intval


#####################################
#
def axes_func(joy):
  v = joy.axes[1] * 200
  lv = rv = -v

  tsp = joy.axes[3]
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

def hat_func(joy):
  print(joy.hats)

def button_func(joy):
  print('down', joy.buttons)

def release_btn(joy, btn):
  if btn == 0:
    joy.set_flag(False)
    print("=======END")

###############################
#
def main():
  joy = Joystick()
  joy.init()
  ### set Callback
  joy.axis_callback=axes_func
  joy.hat_callback=hat_func
  joy.button_press_callback=button_func
  joy.button_release_callback=release_btn
  
  ### Event Loop
  joy.time_intval=30

  while joy.get_flag() :
    pygame.time.wait(30)
    joy.process_event()

if __name__ == '__main__':
  main()

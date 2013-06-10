#!/usr/bin/python
import pygame
import sys
import serial
import os
import pygame.mixer
from time import time

RECONNECT_TIME=3
REPEAT_TIME=3

with open("map.txt", "r") as f:
     lines = f.readlines()

mapping = {}

letters = []

for line in lines:
     line = line.strip()
     if (line==""):
          continue
     num,letter = line.split("=")
     mapping[num] = letter
     letters.append(letter)

pygame.init()

pygame.mixer.init()

modes = pygame.display.list_modes()

size = width, height = modes[0]

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

letter_image = {}
letter_sound = {}

defaultimage = pygame.image.load("main.png")
letter_image["default"] = defaultimage

print "loading"
for letter in letters:
     l = pygame.image.load(letter+".png")
     letter_image[letter] = l

     sound = pygame.mixer.Sound(letter+".wav")
     letter_sound[letter] = sound

print "done"

white=255,255,255

screen.fill(white)

connected = False

try:
     s = serial.Serial(port="/dev/rfcomm0", baudrate=9600, timeout=5)
     connected = True
     print s.portstr 
except:
     print "connection error"
     



current = letter_image["default"]
current_rect =  current.get_rect()

current_letter="default"

last_time = time()

done = False

while not done:

     letter = ''

     print "lookup events"

     for event in pygame.event.get():
         if event.type == pygame.QUIT: sys.exit()

         if (event.type == pygame.KEYDOWN):
              print event
              if (event.key == pygame.K_ESCAPE):
                   done = True
              if ((event.key >= ord('a') and event.key<=ord('z')) or 
                  (event.key >= ord('A') and event.key<=ord('Z'))):
                   letter = chr(event.key).upper()
     


     print "done"

     w = 0
     if (connected):
          try:
               w = s.inWaiting()
	       print w		
          except:
               connected = False               
     else:
          now = time()
          delta = now - last_time;
          if (delta>RECONNECT_TIME):
               os.system("rfcomm release rfcomm0")
               ret = os.system("rfcomm connect rfcomm0")
               if (ret==0):
                    try:
                         s = serial.Serial(port="/dev/rfcomm0", baudrate=9600, timeout=5)
                         connected = True
                         print s.portstr 
                    except:
                         print "connection error"
                    
               last_time = time()

     if (w>0):
          try:
               data = s.readline()
	       x = s.inWaiting()
	       if (x>0):
		  s.read(x)
	       print data
               number= data.strip()
          except:
               connected = False
               number=""

          if mapping.has_key(number):
               letter = mapping[number]
          else:
               with open("unknown.txt", "a+") as f:
                    f.write(data)

     if (letter!='' and letter_image.has_key(letter)):
          now = time()
          delta = now - last_time;
          if (current_letter!=letter):

               print "scaling"

               orig = letter_image[letter]
               orig_rect = orig.get_rect()

               scalex = (width*1.0/orig_rect.width)
               scaley = (height*1.0/orig_rect.height)

               scale = min(scalex, scaley)

               print scale
               current = pygame.transform.scale(orig, (int(orig_rect.width*scale), int(orig_rect.height*scale)))
               current_rect = current.get_rect()
               current_letter = letter

               print letter

     if (current_letter!=letter or delta>REPEAT_TIME):
               if (letter_sound.has_key(letter)):
                    letter_sound[letter].play()

               last_time = time()
               
     
     sys.stdout.flush()

     screen.fill(white)

     pos = ((width-current_rect.width)/2, (height-current_rect.height)/2)

     screen.blit(current, pos)
     

     pygame.display.flip()


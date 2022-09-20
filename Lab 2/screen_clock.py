import time
from time import strftime, sleep
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789
import random
import webcolors
import os
from collections import defaultdict
from datetime import datetime
from urllib.request import urlretrieve
from urllib.parse import urljoin
from zipfile  import ZipFile
import pytz # pip install pytz

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# these setup the code for our buttons and the backlight and tell the pi to treat the GPIO pins as digitalIO vs analogIO
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


# get time from two zones
geonames_url = 'http://download.geonames.org/export/dump/'
basename = 'cities15000' # all cities with a population > 15000 or capitals
filename = basename + '.zip'
# get file
if not os.path.exists(filename):
    urlretrieve(urljoin(geonames_url, filename), filename)
# parse it
city2tz = defaultdict(set)
with ZipFile(filename) as zf, zf.open(basename + '.txt') as file:
    for line in file:
        fields = line.split(b'\t')
        if fields: # geoname table http://download.geonames.org/export/dump/
            name, asciiname, alternatenames = fields[1:4]
            timezone = fields[-2].decode('utf-8').strip()
            if timezone:
                for city in [name, asciiname] + alternatenames.split(b','):
                    city = city.decode('utf-8').strip()
                    if city:
                        city2tz[city].add(timezone)

# first city and color
fmt = '%Y-%m-%d %H:%M:%S %Z%z'
city1 = input('Type the first city and hit enter: ')
person1 = input('Type in current mood color and hit enter: ')
city_one_list = [i for i in city2tz[city1]]
city1_time = datetime.now(pytz.timezone(city_one_list[-1]))
city1_zone = "%s is in %s timezone" % (city1, city_one_list[-1])
city1_text = "Current time in %s is %s" % (city1, city1_time.strftime(fmt))

# second city and color
city2 = input('Type the second city and hit enter: ')
person2 = input('Type in current mood color and hit enter: ')
city_two_list = [i for i in city2tz[city2]]
city2_time = datetime.now(pytz.timezone(city_two_list[-1]))
city2_zone = "%s is in %s timezone" % (city2, city_two_list[-1])
city2_text = "Current time in %s is %s" % (city2, city2_time.strftime(fmt))

# Main loop:
t = 0
while True:
    # Draw a black filled box to clear the image.
    # draw.rectangle((0, 0, width, height), outline=0, fill=0)
    if buttonA.value and buttonB.value:
        backlight.value = False  # turn off backlight
    else:
        backlight.value = True  # turn on backlight
    if buttonB.value and not buttonA.value:  # just button A pressed
        if person1 != 'rainbow':
            draw.rectangle((0, 0, width, height), outline=0, fill=(color565(*list(webcolors.name_to_rgb(person1)))))
            # disp.fill(color565(*list(webcolors.name_to_rgb(person1)))) # set the screen to the users color
        else:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            t += 1
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            # Change color for background in every 1 seconds for reminder!
            if t%1 ==1 and t!=1:
                draw.rectangle((0, 0, width, height), outline=0, fill=(r,g,b))
                draw.text((5,5), city1_zone)
                draw.text((10,5), city1_text)

    if buttonA.value and not buttonB.value:  # just button B pressed
        # pass
        if person2 != 'rainbow':
            draw.rectangle((0, 0, width, height), outline=0, fill=(color565(*list(webcolors.name_to_rgb(person2)))))
            # disp.fill(color565(*list(webcolors.name_to_rgb(person2)))) # set the screen to the users color
        else:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            t += 1
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            # Change color for background in every 5 seconds for reminder!
            if t%1 ==1 and t!=1:
                draw.rectangle((0, 0, width, height), outline=0, fill=(r,g,b))
                draw.text((5,5), city2_zone, fill="#FFFF00")
                draw.text((10,5), city2_text, fill="#FFFF00")
        # disp.fill(color565(255, 255, 255))  # set the screen to white
    if not buttonA.value and not buttonB.value:  # none pressed
        disp.fill(color565(0, 255, 0))  # green


while True:
    # Draw a black filled box to clear the image.
    # draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # mins, secs = divmod(t, 60)
    # timer = '{:02d}:{:02d}'.format(mins, secs)
    # t += 1
    # r = random.randint(0,255)
    # g = random.randint(0,255)
    # b = random.randint(0,255)

    # # Change color for background in every 5 seconds for reminder!
    # if t%5 ==1 and t!=1:
    #     draw.rectangle((0, 0, width, height), outline=0, fill=(r,g,b))
    #     draw.text((5,5), '5 seconds')
    # #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py 
    # # cmd = "date"
    # # date_time = "Clock: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
    # date_time = "Clock: " + strftime("%m/%d/%Y %H:%M:%S")
    # y = top
    # # draw.text((x, y), date_time, font=font, fill="#FFFFFF")
    # y += font.getsize(date_time)[1]
    # draw.text((x, y), timer, font=font, fill="#FFFF00")

    
    # print(timer, end="\r")
    # time.sleep(1)
    

    





    # Display image.
    disp.image(image, rotation)
    time.sleep(1)

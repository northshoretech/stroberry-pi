#strobes an image to an LED device connected to the raspberry pi
import time
from argparse import ArgumentParser
from PIL import Image

#change the module being imported to match the device
#(or use a module that provides a test environment)
import devices.dev_adaled as LEDDevice

array_count, led_count = LEDDevice.numarrays, LEDDevice.numleds

#read and store arguments
parser = ArgumentParser()
parser.add_argument("imgfile", type=file, help="the image file to scan")
parser.add_argument("-t", "--time", type=int, default="1000", help="the number of milliseconds to display each array")
parser.add_argument("-f", "--flow", choices=('rtl', 'ltr', 'ttb', 'btt'), default="rtl", help="sets the direction that the image will flow on the board")
parser.add_argument("-m", "--maintain", action='store_true', help="whether to maintain aspect ratios if the image requires resizing")
parser.add_argument("-d", "--debug", action='store_true', help="enables debug output while the program is running")
args = parser.parse_args()

imgfile = args.imgfile
display_time, flow_direction, maintain_aspect_ratios = args.time, args.flow, args.maintain
debug = args.debug

#read image file into memory and resize if necessary to create RGB pixel data
#note: assumes (0,0) is upper left
#note: we aren't converting the pixel data using the image library
#   because each device has different representations to output color.
#   Color mode will come into effect during the actual device output
im = Image.open(imgfile)
imgwidth, imgheight = im.size[0], im.size[1]
if debug:
    print "Starting size is", imgwidth, imgheight
#if flow is horizontal, the array is a vertical column, so resize based on height
if (args.flow == 'rtl' or args.flow == 'ltr') and imgheight != led_count:
    width = int(imgwidth * (float(led_count) / float(imgheight))) if maintain_aspect_ratios else imgwidth
    im = im.resize((width, led_count))
#if flow is vertical, the array is a horizontal row, so resize based on width
elif (args.flow == 'ttb' or args.flow == 'btt') and imgwidth != led_count:
    height = int(imgheight * (float(led_count) / float(imgwidth))) if maintain_aspect_ratios else imgheight
    im = im.resize((led_count, height))
if debug:
    print "Final size is", im.size
imgwidth, imgheight = im.size[0], im.size[1]
pixel_data = im.load()

#create a configuration of LED values that mimic the board in size and orientation
# and build a mapping for the pixel data so that we can scan based on orientation and flow 
configuration = []
for i in range(array_count):
    configuration.insert(0, [(0,0,0)]*led_count)

scanner = {"rtl" : range(im.size[0])
    , "ltr" : range(im.size[0])[::-1]
    , "ttb" : range(im.size[1])[::-1]
    , "btt" : range(im.size[1])}


#MAIN EVENT
#1. initialize device
#2. start scanning over time and update the configuration with the current state of what the LEDs should be 
#3. output to device
#note:
#   first element in the configuration matches the array indicated by the first letter of the direction flow.
#   Each LED will be specified in RGB format, to be handled by the device output later.
#   Pure black is considered to be off
LEDDevice.initialize_device()
for i in scanner[flow_direction]:
    array = []
    for j in range(led_count):
        if flow_direction == 'rtl' or flow_direction == 'ltr':
            array.append(pixel_data[i,j])
        else:
            array.append(pixel_data[j,i])
    configuration.insert(0, array)
    if len(configuration) > array_count:
        configuration.pop()
    if debug:
        print configuration
    LEDDevice.output_to_device(configuration)
    time.sleep(display_time / 1000.0)

#loop or quit
#don't forget to teardown device

print("Done")


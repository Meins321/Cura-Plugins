#Name: Tweak At Z
#Info: Change printing parameters at a given height
#Help: TweakAtZ
#Depend: GCode
#Type: postprocess
#Param: targetZ(float:5.0) Z height to tweak at (mm)
#Param: speed(int:) New Speed (%)
#Param: flowrate(int:) New Flow Rate (%)
#Param: platformTemp(int:) New Bed Temp (deg C)
#Param: extruderOne(int:) New Extruder 1 Temp (deg C)
#Param: extruderTwo(int:) New Extruder 2 Temp (deg C)
#Param: extruderThree(int:) New Extruder 3 Temp (deg C)

## Written by Steven Morlock, smorloc@gmail.com
## Modified by Ricardo Gomez, ricardoga@otulook.com, to add Bed Temperature and make it work with Cura_13.06.04+
## Modified by Stefan Heule, Dim3nsioneer@gmx.ch, to add Flow Rate, restoration of initial values when returning to low Z, extended stage numbers, direct stage manipulation by GCODE-comments
## This script is licensed under the Creative Commons - Attribution - Share Alike (CC BY-SA) terms

# Uses -
# M220 S<factor in percent> - set speed factor override percentage
# M221 S<factor in percent> - set flow factor override percentage
# M104 S<temp> T<0-#toolheads> - set extruder <T> to target temperature <S>
# M140 S<temp> - set bed target temperature

version = 3.0

import re

def getValue(line, key, default = None):
	if not key in line or (';' in line and line.find(key) > line.find(';') and not ';TweakAtZ' in key):
		return default
	subPart = line[line.find(key) + len(key):] #allows for string lengths larger than 1
        if ';TweakAtZ' in key:
                m = re.search('^[0-3]', subPart)
        else:
                m = re.search('^[0-9]+\.?[0-9]*', subPart)
	if m == None:
		return default
                print 'm was None'
	try:
		return float(m.group(0))
	except:
		return default

with open(filename, "r") as f:
	lines = f.readlines()

old_speed = 100
old_flowrate = 100
old_platformTemp = -1
old_extruderOne = -1
old_extruderTwo = -1
old_extruderThree = -1
pres_ext = 0
z = 0
x = 0
y = 0
state = 0 #state 0: deactivated, state 1: activated, state 2: active, but below z, state 3: active, passed z
with open(filename, "w") as f:
	for line in lines:
		f.write(line)
                if getValue(line, ';TweakAtZ-state',None) is not None: #checks for state change comment
                        state = getValue(line, ';TweakAtZ-state', None)
                        #print 'found TweakAtZ-state comment, new value: ' + repr(state)
                if (getValue(line, 'T', None) is not None) and (getValue(line, 'M', None) is None): #looking for single T-command
                        pres_ext = getValue(line, 'T', pres_ext)
                if (getValue(line, 'M', None) == 190 or getValue(line, 'M',None) == 140) and state < 3: #looking for bed temp, stops after target z is passed
                        old_platformTemp = getValue(line, 'S', old_platformTemp)
                if (getValue(line, 'M', None) == 109 or getValue(line, 'M',None) == 104) and state < 3: #looking for extruder temp, stops after target z is passed
                        if getValue(line, 'T', pres_ext) == 0:
                                old_extruderOne = getValue(line, 'S', old_extruderOne)
                        elif getValue(line, 'T', pres_ext) == 1:
                                old_extruderTwo = getValue(line, 'S', old_extruderTwo)
                        elif getValue(line, 'T', pres_ext) == 2:
                                old_extruderThree = getValue(line, 'S', old_extruderThree)
		if getValue(line, 'G', None) == 1 or getValue(line, 'G', None) == 0:
			newZ = getValue(line, 'Z', z)
			x = getValue(line, 'X', x)
			y = getValue(line, 'Y', y)
			if newZ != z:
				z = newZ
				if z < targetZ and state == 1:
					state = 2
				if z >= targetZ and state == 2:
					state = 3
					f.write(";TweakAtZ V%1.1f: executed at %1.2f mm\n" % (version,targetZ))
					if speed is not None and speed != '':
						f.write("M220 S%f\n" % float(speed))
					if flowrate is not None and flowrate != '':
						f.write("M221 S%f\n" % float(flowrate))
					if platformTemp is not None and platformTemp != '':
						f.write("M140 S%f\n" % float(platformTemp))
					if extruderOne is not None and extruderOne != '':
						f.write("M104 S%f T0\n" % float(extruderOne))
					if extruderTwo is not None and extruderTwo != '':
						f.write("M104 S%f T1\n" % float(extruderTwo))
					if extruderThree is not None and extruderThree != '':
						f.write("M104 S%f T2\n" % float(extruderThree))					
                                if z < targetZ and state == 3: #re-activates the plugin if executed by pre-print G-command, resets settings
                                        state = 1
					f.write(";TweakAtZ V%1.1f: executed at %1.2f mm\n" % (version,targetZ))
					if speed is not None and speed != '':
						f.write("M220 S%f\n" % float(old_speed))
					if flowrate is not None and flowrate != '':
						f.write("M221 S%f\n" % float(old_flowrate))
					if platformTemp is not None and platformTemp != '':
						f.write("M140 S%f\n" % float(old_platformTemp))
					if extruderOne is not None and extruderOne != '':
						f.write("M104 S%f T0\n" % float(old_extruderOne))
					if extruderTwo is not None and extruderTwo != '':
						f.write("M104 S%f T1\n" % float(old_extruderTwo))
					if extruderThree is not None and extruderThree != '':
						f.write("M104 S%f T2\n" % float(old_extruderThree))					
				

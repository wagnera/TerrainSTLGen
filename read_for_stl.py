#!/usr/bin/env python
import struct
import numpy as np
import matplotlib.pyplot as P

header_file = open("data/n39_w108_1arc_v3.hdr", "r")
data_file = open("data/n39_w108_1arc_v3.bil","rb")
info={}
for H in header_file:
	(key,val) = H.split()
	info[key] = val
Nbytes=int(int(info['NBITS'])/8)

temp_data=list()
for i in data_file:
	temp_data.extend(i)
print("temp_data length: " + str(len(temp_data)))
data=list()
print('reading data...')
for i in range(int(len(temp_data)/Nbytes)):
	buf=bytes([temp_data[Nbytes*i],temp_data[Nbytes*i+1]])
	data.append(struct.unpack('<h',buf)[0])

#print(data)
NC=int(info['NCOLS'])
NR=int(info['NROWS'])
Xdim=float(info['XDIM'])
Ydim=float(info['YDIM'])
alt = np.zeros((NR,NC))
x = np.zeros((NR,NC))
y = np.zeros((NR,NC))
for j in range(NR):
	for i in range(NC):
		alt[NR-1-j,i]=data[i+j*NC]

P.contour(alt)
P.show()
np.savez('temp_data',x,y,alt)

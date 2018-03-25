#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as P
from stl import mesh

######### No necesary after combination
header_file = open("n37_w081_1arc_v2.hdr", "r")
data_file = open("n37_w081_1arc_v2.bil","r")
info={}
for H in header_file:
	(key,val) = H.split()
	info[key] = val
Nbytes=int(info['NBITS'])/8

NC=int(info['NCOLS'])
NR=int(info['NROWS'])
Xdim=float(info['XDIM'])
Ydim=float(info['YDIM'])
X_o=float(info['ULXMAP'])
Y_o=float(info['ULXMAP'])-1

data =np.load('temp_data.npz')
alt=data['arr_2']
##x=data['arr_0']
#y=data['arr_1']
#########

def create_faces(i,j,NR):
	a=list()
	current=j*NR+i
	surr=[current - NR,current - NR + 1,current + 1,current + NR + 1,current + NR,current + NR - 1,current - 1,current - NR -1]
	for k in range(len(surr)-1):
		a.append([current,surr[k],surr[k+1]])
	a.append([current,surr[7],surr[0]])
	return a

def downsample(array,NR,NC,factor):
	R=int(NR/factor)+1
	C=int(NC/factor)+1
	new_array=np.zeros((R,C))
	for j in range(NC):
		for i in range(NR):
			if i % factor == 0:
				if j % factor ==0:
					new_array[i/factor,j/factor]=array[i,j]
	return [new_array,R,C]

[alt,NR,NC]=downsample(alt,NR,NC,3)
scale=150.0 #length in mm
feature_scale=3
scale=scale/1000
min_alt=np.amin(alt)
max_alt=np.amax(alt)
height_scale=(max_alt-min_alt)/(30.0*NC*3)*scale/500
print(min_alt,max_alt,height_scale)
x=np.arange(0,scale+0.00001,scale/(NC-1))
y=np.arange(0,scale+0.00001,scale/(NR-1))
#create vertices:
vertices=list()
faces=list()
for j in range(NC):
	for i in range(NR):
		vertices.append([x[i],y[j],height_scale*(alt[i,j]-min_alt)])
		if i % 2 != 0:
			if j % 2 !=0:
				faces.extend(create_faces(i,j,NR))

vertices=np.array(vertices)
faces=np.array(faces)
print(faces)
print(vertices)

cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    for j in range(3):
    	cube.vectors[i][j] = vertices[f[j],:]

# Write the mesh to file "cube.stl"
cube.save('cube.stl')
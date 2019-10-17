#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as P
from stl import mesh

######### No necesary after combination
header_file = open("data/n37_w081_1arc_v3.hdr", "r")
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

print("Loading Data")
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
	print("Down Sampling")
	R=int(NR/factor)+1
	C=int(NC/factor)+1
	new_array=np.zeros((R,C))
	for j in range(NC):
		for i in range(NR):
			if i % factor == 0:
				if j % factor ==0:
					new_array[int(i/factor),int(j/factor)]=array[i,j]
	return [new_array,R,C]

[alt,NR,NC]=downsample(alt,NR,NC,4)

print("Generating Main Terrain Mesh")
scale=150.0 #length in mm
feature_scale=1
base_height = 3 #height of bottom in mm
scale=scale
min_alt=np.amin(alt)
max_alt=np.amax(alt)
height_scale=(max_alt-min_alt)/(30.0*NC*5)*scale/500
#print(min_alt,max_alt,height_scale)
x=np.arange(0,scale+0.00001,scale/(NC-1))
y=np.arange(0,scale+0.00001,scale/(NR-1))
#create vertices:
vertices=list()
edges = list()
faces=list()
for j in range(NC):
	for i in range(NR):
		vertices.append([x[i],y[j],height_scale*(alt[i,j]-min_alt) + base_height])
		"""if i == 0:
			edges.append([i,j])
		elif j == 0:
			edges.append([i,j])
		elif i == (NR - 1):
			edges.append([i,j])
		elif j == (NC - 1):
			edges.append([i,j])"""
		if i % 2 != 0:
			if j % 2 !=0:
				faces.extend(create_faces(i,j,NR))

print("Generating Sides")
edges = [[0,j] for j in range(NC)] + [[i, NC - 1] for i in range(1,NR)] + \
	[[NR - 1,j] for j in range(NC - 2, -1, -1)] + [[i, 0] for i in range(NR - 2,0,-1)]
vert_offset = len(vertices) - 1
for k, edge in enumerate(edges):
	i, j = edge
	vertices.append([x[i],y[j],0])
	if k == len(edges) - 1:
		faces.append([k + vert_offset,np.ravel_multi_index([i,j],(NR,NC),order='F'),np.ravel_multi_index(edges[0],(NR,NC),order='F')])
		faces.append([k + vert_offset,np.ravel_multi_index(edges[0],(NR,NC)),k + 1 + vert_offset])
	elif k < 1:
		pass#faces.append([k + vert_offset,np.ravel_multi_index([i,j],(NR,NC),order='F'),np.ravel_multi_index(edges[k+1],(NR,NC),order='F')])
		#faces.append([k + vert_offset,np.ravel_multi_index(edges[k+1],(NR,NC),order='F'),k + 1 + vert_offset])
	else:
		faces.append([k + vert_offset,np.ravel_multi_index([i,j],(NR,NC),order='F'),np.ravel_multi_index(edges[k+1],(NR,NC),order='F')])
		faces.append([k + vert_offset,np.ravel_multi_index(edges[k+1],(NR,NC),order='F'),k + 1 + vert_offset])

#Create bottom
faces.append([1 + vert_offset, NC + vert_offset, NC + NR + vert_offset])
faces.append([1 + vert_offset, NC + NR + vert_offset, NC*2 + NR + vert_offset])

vertices=np.array(vertices)
faces=np.array(faces)

print("Generating STL File")
cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    for j in range(3):
    	cube.vectors[i][j] = vertices[f[j],:]

# Write the mesh to file "cube.stl"
cube.save('Redstone.stl')
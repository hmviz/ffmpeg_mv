#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:43:04 2018


This script is part of motions.py to extract and visualize motions vectors

"""

import subprocess as sp
from numpy import sqrt,empty,unique, diff
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def getWH(video):
    '''
    This function returns the width and height of a video. It runs using ffprobe.
    The terminal command is of the format 'ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width video_file_name'
    This returns: 'streams_stream_0_width' and 'streams_stream_0_height' and the values are extracted accordingly.
    
    Meaning of the variables:
        video: video file
    '''
    command = ['ffprobe', '-v', 'error', '-of', 'flat=s=_', '-select_streams', 'v:0', '-show_entries', 'stream=height,width', video]
    subWH = sp.Popen(command, stdout=sp.PIPE)
    WH = subWH.communicate()[0].decode('utf-8')
    
    width = WH.replace('\n', ',').split(',')[0].split('=')[1]
    height = WH.replace('\n', ',').split(',')[1].split('=')[1]
    
    return int(width), int(height)

def get_motions(dataframe):
    ''' 
    This function takes the extracted data from FFmpeg as dataframe and extract the following columns of interest:
    
    - srcx: absolute source position, x, which corresponds to X in the code
    - srcy: absolute source position, y, which corresponds to Y in the code
    - dstx: absolute destination position, x, which corresponds to U in the code
    - dsty: absolute destination position, y, which corresponds to V in the code
    - framenum: frame number
    
    As FFmpeg ignores 'I-frames' in the extraction, framenum starts from 2 (index = 0), thus this program takes
    into account this fact while looping through the frames to re-destribute their respective motions.
    
    Note: dtype=object was using as this is a complex ndarray.
    '''
    
    df = dataframe
    data_vectors = empty([len(unique(df[df['srcx'].notnull()]['framenum'])), 2], dtype=object)
    frame_list = unique(df[df['srcx'].notnull()]['framenum'])
    count = 0
    
    for i in frame_list:
        if count <= len(frame_list):
            vectors = empty([len(df[df['srcx'].notnull() & (df['framenum'] == i)]['srcx']), 4])
            vectors[:,0] = df[df['srcx'].notnull() & (df['framenum'] == i) & (df['framenum'] == i)]['srcx']
            vectors[:,1] = df[df['srcy'].notnull() & (df['framenum'] == i) & (df['framenum'] == i)]['srcy']
            vectors[:,2] = df[df['dstx'].notnull() & (df['framenum'] == i) & (df['framenum'] == i)]['dstx']
            vectors[:,3] = df[df['dsty'].notnull() & (df['framenum'] == i) & (df['framenum'] == i)]['dsty']    
            data_vectors[:,0][count] = vectors
            data_vectors[:,1][count] = i
            count = count + 1
            
    return data_vectors


def show_quiver(X, Y, U, V, video, ffvf, ffvfp = 1):
    
    '''
    This function is used together with ffmpeg_quiver() to plot the extracted motion vectors as subplot with
    the respective video frame image passed through ffmpeg for validation purposes.
    
    The function plots the motion vectors using colorbar that changes based on the magniture 'M' of the arrows.
    
    Meaning of the variables:
        video: video file
        ffvf: ffmpeg validation frame 
        ffvfp: number of subsequent validation frames to print from ffvf. Default should be 1.
    '''
    # Arrows magnitude    
    M = sqrt(U*U + V*V)
    
    # Video dimensions
    width, height = getWH(video)
    
    # First subplot with the visualization of the extracted motions
    ax1 = plt.subplot(1, 2, 1)
    ax1.set_xlim([0, width])
    ax1.set_ylim([height, 0])
    asp = abs(diff(ax1.get_xlim())[0] / diff(ax1.get_ylim())[0]) # Aspect ratio, I added 'abs' as I reversed the axis orientation for the plot, as negative aspect would fail.
    ax1.set_aspect(asp)
    Q = plt.quiver(X, Y, U, V, M,cmap=plt.cm.jet)
    plt.colorbar(Q, cmap=plt.cm.jet, fraction=0.046, pad=0.04) # Here 'fraction' and 'pad' is to match colorbar height with that of the plot

    # Second subplot with corresponding ffmpeg frame with motions for validation
    ax2 = plt.subplot(1, 2, 2)
    ax2.set_xlim([0, width])
    ax2.set_ylim([height, 0])
    ax2.set_aspect(asp)     # Same aspect ratio with subplot 1
    ffmpeg_quiver(video, ffvf, ffvfp)


def ffmpeg_quiver(video, ffvf, ffvfp):
    '''
    This function displays a video frame as extracted from ffmpeg together with the motion vectors drawn into it.
    
    As one frame is extracted, this frame is read into python using matplotlib.image's mping function.
    The frame is deleted everytime a call for a new one is made. The sleep of 0.5 seconds is added to allow this operation.
    
    Explanation of ffmpeg command:
        'ffmpeg -flags2 +export_mvs -i video.mp4 -vf 'select=gte(n\,ffvf),codecview=mv=pf+bf+bb' -vframes 1 frame.png'
        Open video.mp4, skip first ffvf frames (n starts from 0), visualize motion vectors (all types), and writes exactly 1 frame into frame.png.
    
    Future improvements will include a direct image import from  in-memory buffer to reduce number of operations.
    '''
    
    rmcmd = "rm frame.png" # Command to remove any frame.png in the current directory
    sp.Popen(rmcmd, shell=True, stdout = sp.PIPE, stderr = sp.PIPE)
    command = "ffmpeg -flags2 +export_mvs -i %s -vf 'select=gte(n\,%d),codecview=mv=pf+bf+bb' -vframes %d frame.png" %(video, ffvf, ffvfp)
    sp.Popen(command, shell=True, stdout = sp.PIPE, stderr = sp.PIPE)
    sleep(0.5)
    img = mpimg.imread('frame.png')
    plt.imshow(img)
    plt.tight_layout() # This minimizes the overlap of subplots
    plt.show()


def main(data, element, video):
    '''
    This function takes the extracted motion vectors for visualization, depending on the frame of interest.
    
    The main inputs are:
        - The motion vectors as ndarray object
        - The frame number 'element'
        - The video file name that is in the same directory as the script
        
    The motion vectors are drawn from (X, Y) to (U, V). This coordinates corresponds to the center
    of each macroblock
    
    Note: 
        U, V are calculated twice, the second time is to normalize the arrows (in case we are interested in the direction).
        The magnitude however, will still be seen through the colorbar. The normalization makes visualization better.
        This second part can be unchecked anytime.
    '''
    
    X = data[element][0][:,0]
    Y = data[element][0][:,1]
    U = data[element][0][:,2] - X
    V = data[element][0][:,3] - Y
    
    # The following (U,V) can be commented in, if magnitude of the arrows should be visualized beyond colors.
    U = U / sqrt(U*U + V*V)
    V = V / sqrt(U*U + V*V)
    
    # Plotting motion vectors
    ffvf = data[element][1] # frame of interest
    show_quiver(X, Y, U, V, video, ffvf=ffvf)
    
    print('These motion vectors correspond to frame number', data[element][1])
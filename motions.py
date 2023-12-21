#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 14:52:23 2018



The motions.py extracts the motion vectors from a video file.
It uses FFmpeg and a modified binary written in C contained within FFmpeg's example folder.


*** DEPENDENCIES ***

This script depends on the following Python Packages:
- FFmpeg version 3.4 or higher
- The modified extract_mvs.c file in compiled form
- subprocess, to communicate with FFmpeg and the modified binary
- pandas, to handle the vectors in a contained data frame
- numpy, to speed up array manipulation
- matplotlib, for quiver and image import and display

"""

import sys
import subprocess as sp
import pandas as pd
from utils import main, get_motions


if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
# Video file to be analyzed: 
video = '450x192_24fps_stereo.mp4'

# This variable starts from 0 which normally corresponds to framenum 2
element = 10 

# This variable was aimed at storing video file name to compare if new file is to be analyzed.
# I did not finish the verification old file and new file. Requires Class. Can easily be done.
# But if video file name is changed, please clean all variables in the workspace.
oldvideo = video

cmd = ['./extract_mvs', video]

# Checking if motion vectors ndarray exists. 
# This is important to avoid re-extracting them for the purpose of visualization. 
# Thus speeds up the code after first reading.

try:
    data
    if oldvideo == video: # Clean workspace if you changed video file name. A fix with a class will be added in the future.
        main(data, element, video)
    else:
        a = sp.Popen(cmd, stdout=sp.PIPE)
        b = StringIO(a.communicate()[0].decode('utf-8'))
        df = pd.read_csv(b, sep=",")
        data = get_motions(df)
        main(data, element, video)
except:
    a = sp.Popen(cmd, stdout=sp.PIPE)
    b = StringIO(a.communicate()[0].decode('utf-8'))
    df = pd.read_csv(b, sep=",")
    data = get_motions(df)
    main(data, element, video)        






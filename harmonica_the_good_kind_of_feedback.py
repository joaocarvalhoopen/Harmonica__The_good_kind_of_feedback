################################################################################
# Program: Harmonica - The good kind of feedback.
# Autor:   Joao Carvalho
# Date:    2018/07/11
# License: MIT License
#
# Description: This program was started has a little program to test if
#              I could identify the different holes being played at the
#              same time in the diatonic 10 hole harmonica, more
#              communally called the Blues Harmonica. This is a major
#              problem when starting to play the harmonica, because it’s
#              difficult to learn the technique of playing a single
#              note. From the first testes the idea was to show it visually,
#              but this was only a little program for my home use. But then
#              instead of practicing the harmonica :-) , I started adding
#              features, optimizing for performance and removing some rough
#              edges, and it became a somewhat better little program.
#              Then I added the part of a simple kind of “Guitar Hero” for
#              the Harmonica, in which you can specify and read your own
#              tablature files. Now it continues to be a little simple
#              program but I hope that is of some use to others starting
#              to playng the harmonica.
#
# Operating systems: I tested the program on Windows and on Linux
#                    with Anaconda Python 3.6.
#
# Program execution dependencies: -Anaconda 3.6  (Python 3.6, Numpy, TKinker,
#                                                MatplotLib)
#                                 -PyAudio
#                                 -Pillow
#
#
# The MIT License (MIT)
#
# Copyright (c) 2018 Joao Carvalho
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################



###################################################################
###################################################################
#
# TODO List:
#
#  1 - Change the interface of the drawn harmonica to be inspired in
#      the interface of the Harmonica Tuner. To permit visualize the
#      amplitude of each note and the bending notes. We already have
#      a graph for the bending, but the FFT sample lenght has to be
#      longer, so it is more precise. Show the notes upper and lower
#      to the harmonica.
#
#  2 - Change the program to permit more musical notes other them the
#      10 holes of Blow notes and Draw notes. To implement this i will
#      need to re-write some part's of the code.
#
#  3 - Allow that all the program function with harmonica other that in
#      the Key of C (The more comon harmonica). C, B, E and all the
#      other types.
#
#  4 - Add a new file format with the ABC notation and make a conversion
#      button that converts tabular file notation into ABC file notation.
#      Use the Python lib music21.
#      Show a animation of the music score fret with the notes while
#      playing, with a mark on the region that is being played.
#
####################################################################
####################################################################


# memory profiler tool
#import memory_profiler
#from memory_profiler import profile
#from memory_profiler import memory_usage

# @profile    You have to put this tag over each function that you need to do the memory profile.
# -m memory_profiler   <----- parameters for the execution of the Python interpreter.

# mprof run <executable>
# mprof plot

# Code optimization, JIT compilation of the function marked with @JIT, the optimization is made with
# NUMBA (only works with the Anaconda distribution).
#from numba import jit

# Yout have to out the tag @jit in the line before of the function that you won't to JIT compile.
# You can only ptimize functions, not methods, but you can make a function of every user method
# and can pass to it the self reference pointer/address.
# @jit

# Used for reading the images in jpg for the GUI, it loads the inicial harmonica image of the first page.
from PIL import Image as Image_PIL , ImageTk as ImageTk_PIL

import time
import numpy as np
import audio_utils
from harmonica_notes_and_holes import get_external_list_holes, get_external_orde_notes_name_list, get_external_orde_notes_freq_list
import music_file_parser as mfp

########################################
# Adds the global variable defined in the other file to this file.
list_holes = get_external_list_holes()


# Used in the method find of a note for the canvas, calculated in the animate.
ordered_notes_names_list = get_external_orde_notes_name_list()
ordered_notes_freq_list  = get_external_orde_notes_freq_list()

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename as askopenfilename_tk
from tkinter.messagebox import showerror as showerror_tk

maxFFT = 0 
mic = None

max_silent_begin_value = 0
max_silent_begin_counts = 10
max_silent_value = 0.0


LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

list_blow_holes_bucket_index = []
list_draw_holes_bucket_index = []

# In the bucket index of the FFT the following 2 global variables indicates the inferior and superior limits
# of the FFT buckets that have to be considered,
# Usado na função animcate()
min_note_index_to_consider = 0
max_note_index_to_consider = 0

# Writen in the function animation and readed in the function draw_harmonica()
global_max_freq         = 0.0
global_max_bucket_index = 0
global_max_nearest_note = '.'

#############
# Music currently playing.
global_curr_music_score = None

###################
# Notes animation on the canvas.
#     With the following structure:
#
#  .counter = 0    # Increments the loop of the GUI update. Int64
#
#
index_counter               = 0
index_curr_anim_state       = 1
# Animation states:
s_stop = 3
# NOTA: This stop has to be coordinated with one that is inside of the update,
#       the exist 2  because i have to make the JIT compile inside the module
#       and can't and I can't access to global variables to define them globally.
#       It's because of performance issues and because of lack of design in this program!
#       Bacause this program is just a simple hack!
index_down_offset           = 2
index_curr_start_note_index = 3
index_curr_end_note_index   = 4

#                   [counter, curr_anim_state, index_down_offset, curr_start_note_index, curr_end_note_index ]
global_notes_anim = [int(0), s_stop, int(0), 0, 1 ]

# Speed of the folling notes/holes of the tablature.
global_music_velocity = 2.0

# Global vars for the labels, to permit changing text of the Label.
global_label_filename = None
global_label_title    = None
global_label_key      = None

# Repeat mode  global variable for when it reaches the end of a music in the state playing,
# it clear's the 2 variables and start again from the beginning again. Non stopping.
global_repeat_on_off = False

# Canvas of the harmonica drawing and folling notes.
g_canvas = None


#@jit
def index2Freq(i, samples, nFFT):
    return i * (samples / nFFT / 2.0)

#@jit
def freq2Index(freq, samples, nFFT):
    return int(freq / (samples / nFFT / 2.0))


# this function is only executed once in the begginning to determine ehich are the FFT buckets
# for each frequency/note. We also include a small variable delta range for each note.
def calculate_note_bucket_index(list_type = 'blow'):
    global list_holes
    list_holes_bucket_index = []

    len_FFT = audio_utils.get_len_FFT()
    # DEBUG: DEBUG ALTERAR CORRIGIR!!!!
    # len_FFT = 8840

    index = 1
    for hole_data in  list_holes:
        if list_type == 'blow' and hole_data[4] == 'D':
            index += 1
            continue
        elif list_type == 'draw' and hole_data[4] == 'B':
            index += 1
            continue
        hole_bucket_index = freq2Index(freq=hole_data[1], samples=44100, nFFT=len_FFT)
        hole_data.append(hole_bucket_index)

        delta_buraco =  hole_data[5]

        # if delta_buraco >= 3:
        #     list_holes_bucket_index.append(hole_bucket_index - 3)
        # if delta_buraco >= 2:
        #     list_holes_bucket_index.append(hole_bucket_index - 2)
        # if delta_buraco >= 1:
        #     list_holes_bucket_index.append(hole_bucket_index - 1)
        # if delta_buraco >= 0:
        #     list_holes_bucket_index.append(hole_bucket_index)
        # if delta_buraco >= 1:
        #     list_holes_bucket_index.append(hole_bucket_index + 1)
        # if delta_buraco >= 2:
        #     list_holes_bucket_index.append(hole_bucket_index + 2)
        # if delta_buraco >= 3:
        #     list_holes_bucket_index.append(hole_bucket_index + 3)

        for delta_buraco_index in range(-delta_buraco, delta_buraco + 1):
            list_holes_bucket_index.append(hole_bucket_index + delta_buraco_index)

        index += 1

    return list_holes_bucket_index



# In the past this code was JIT compilled, now it doesn't have to be JIT compilled.
#@jit
def calc_note_bucket_that_are_on_blow_and_draw(global_list_holes,
                                               abs_fft,
                                               list_holes_bucket_index,
                                               max_bucket_value,
                                               ratio_max_silent,
                                               hole_type
                                               ):

    # This is what selects only the FFT buckets of musical notes. After this point,
    # only this buckets are processed. Filtering the sinal, and incrise significantly
    # the performance of the algorithm.
    bucket_value_ratio = abs_fft[list_holes_bucket_index] / max_bucket_value

    #print("bucket_value_ratio" + str(bucket_value_ratio))

    # Threashold on all holes bucktes (index-1, index, index+1)
    # Using NumPy vectorised instructions.
    holes_played_times_3_elemts = np.where(np.logical_and(np.greater(bucket_value_ratio, 0.5), # 0.4),
                                                          np.greater(bucket_value_ratio, ratio_max_silent)),
                                           1,
                                           0)

    # NOTE: I think that the following two instructions do the some thing, and help the GC to clean
    #       this objects faster.
    #del bucket_value_ratio
    bucket_value_ratio = None



    # Note: We detect wich is the bucket with the greatest amplitude, of them all. The amplitude peak bucket.
    #       So that we can filter/remove the notes that can appear in the other side of the harmonica,
    #       corresponding to the harmonics of the original note. And the harmonic has many harmonics,
    #       like the name says!

    # Detect the peak bucket index.
    max_bucket_note_index = np.argmax(abs_fft[list_holes_bucket_index], axis=0)


    #print("holes_played_times_3_elemts: " + str(holes_played_times_3_elemts))

    # # Average of 3 consecutive elements.
    # holes_played = np.convolve([1., 1., 1.], holes_played_times_3_elemts) / 3;
    # holes_played = np.where(holes_played > 0.3, 1, 0)

    note_with_more_amplitude = -1
    list_holes_played = []
    current_hole_index = 0
    current_hole_index_3_elem = 0
    current_delta = 0
    for _ in range(0, len(holes_played_times_3_elemts)):

       # print("Hole_type: " + hole_type +
       #       " current_hole_index: " + str(current_hole_index) +
       #       " current_hole_index_3_elem: " + str(current_hole_index_3_elem) +
       #       " current_delta: " +  str(current_delta) )
        if holes_played_times_3_elemts[current_hole_index_3_elem] > 0.9:
            current_played_note = current_hole_index + 1
            list_holes_played.append(current_played_note)
            if (max_bucket_note_index == current_hole_index_3_elem):
                note_with_more_amplitude = current_played_note

        delta_do_buraco = 0
        if hole_type == 'blow':
            delta_do_buraco = global_list_holes[current_hole_index][5]
        elif hole_type == 'draw':
            delta_do_buraco = global_list_holes[current_hole_index + 10 ][5]
        # print("delta_do_buraco: " + str(delta_do_buraco))

        current_hole_index_3_elem += 1

        if current_delta == (delta_do_buraco * 2 ):   #  + 1 - 1):
            current_delta = 0
            current_hole_index += 1
        else:
            current_delta += 1

    # NOTE: I think that the following 2 instructions do the something. And help the GC.
    #del holes_played_times_3_elemts
    holes_played_times_3_elemts = None

    #print("holes_played: ", str(list_holes_played))

    return list_holes_played, note_with_more_amplitude


def find_holes_played_based_on_the_bucket_index_value(abs_fft, max_silent_value, max_bucket_value):
    global list_holes
    global list_blow_holes_bucket_index
    global list_draw_holes_bucket_index

    # See's if it has already calculated the corresponding bucket index.
    if len(list_blow_holes_bucket_index) == 0:
        list_blow_holes_bucket_index = calculate_note_bucket_index(list_type = 'blow')
        list_draw_holes_bucket_index = calculate_note_bucket_index(list_type = 'draw')

   # print("list_blow_holes_bucket_index: " )
   # print(list_blow_holes_bucket_index)
   # print("list_draw_holes_bucket_index: " )
   # print(list_draw_holes_bucket_index)

    list_blow_holes = []
    list_draw_holes = []

    # Only obatins the buckets values of the sepecific notes indexes.
    # bucket_value = abs_fft[hole_bucket_index]
    # bucket_value_ratio =  bucket_value / max_bucket_value
    if max_bucket_value > max_silent_value:
        # Don't count the value below the max_silent_value.
        ratio_max_silent = max_silent_value / max_bucket_value

        # Nota: A lista de holes_played e list_blow_holes e list_draw_holes é limpa dentro da funcao seguinte.

        list_blow_holes, \
        blow_note_with_more_amplitude = calc_note_bucket_that_are_on_blow_and_draw(list_holes,
                                                                     abs_fft,
                                                                     list_blow_holes_bucket_index,
                                                                     max_bucket_value,
                                                                     ratio_max_silent,
                                                                     hole_type = 'blow')


        list_blow_holes = list(set(list_blow_holes))
        list_blow_holes.sort()


        list_draw_holes, \
        draw_note_with_more_amplitude = calc_note_bucket_that_are_on_blow_and_draw(list_holes,
                                                                     abs_fft,
                                                                     list_draw_holes_bucket_index,
                                                                     max_bucket_value,
                                                                     ratio_max_silent,
                                                                     hole_type = 'draw')


        list_draw_holes = list(set(list_draw_holes))
        list_draw_holes.sort()


       # print("list_blow_holes: ", str(list_blow_holes))
       # print("list_draw_holes: ", str(list_draw_holes))

    return (list_blow_holes, list_draw_holes )


#@jit
def find_canvas_nearest_note_str(global_max_freq,
                                 ordered_notes_names_list,
                                 ordered_notes_freq_list):

    # global ordered_notes_names_list
    # global ordered_notes_freq_list

    # We validate if it is in a valid interval.
    if (global_max_freq > ordered_notes_freq_list[-3] or  # -2 jc
       global_max_freq < ordered_notes_freq_list[1]):
        return '.'

    # With this we determine the medium point, that is also the nearest
    # point point to a note. It has obligatorially an lower note and an
    # upper note.
    min_freq_delta = 1000000.0
    min_freq_delta_index = 0
    for freq_cur_index in range(0, len(ordered_notes_freq_list)):
        freq = ordered_notes_freq_list[freq_cur_index]
        cur_delta_freq = abs(global_max_freq - freq)
        if cur_delta_freq <= min_freq_delta:
            min_freq_delta       = cur_delta_freq
            min_freq_delta_index = freq_cur_index
        else:
            break

    # Put's one note lower (midle - 1) and other note higher (midle + 1)
    midle_freq_index  = min_freq_delta_index
    lower_freq_index  = midle_freq_index - 1
    higher_freq_index = midle_freq_index + 1

    lower_freq  = ordered_notes_freq_list[lower_freq_index]
    midle_freq  = ordered_notes_freq_list[midle_freq_index]  # Nearest note freq.
    higher_freq = ordered_notes_freq_list[higher_freq_index]

    lower_name  = ordered_notes_names_list[lower_freq_index]
    midle_name  = ordered_notes_names_list[midle_freq_index]
    higher_name = ordered_notes_names_list[higher_freq_index]

    perc_lower_midle  = 0.0
    perc_midle_higher = 0.0
    if global_max_freq <= lower_freq:
        # Calcula a distancia da nota lower a nota media.
        delta_2_consecutive_notes = abs(midle_freq - lower_freq)
        delta_lower_note = abs(global_max_freq - midle_freq)
        if delta_lower_note < 0.001:
            delta_lower_note = 0.001
        perc_lower_midle = delta_lower_note / delta_2_consecutive_notes
        perc_lower_midle = 1 - perc_lower_midle

        # The distance from the medium note and to the higher note is 0.0.
        # In reality this only means that this contribution is zero,
        # for the accumulated value of the sum , starting in the lower note.
        perc_midle_higher = 0.0
    else:
        # The distance from the lower note to the medium note is 1.0 .
        perc_lower_midle = 1.0

        # Calculates the distance from the medium note to the higher note.
        delta_2_consecutive_notes = abs(higher_freq - midle_freq)
        delta_higher_note = abs(global_max_freq - higher_freq)
        if delta_higher_note < 0.001:
            delta_higher_note = 0.001
        perc_midle_higher = delta_higher_note / delta_2_consecutive_notes
        perc_midle_higher = 1 - perc_midle_higher

    order_of_3_notes = ( global_max_freq,
                        (lower_name, perc_lower_midle),
                        (midle_name),
                        (higher_name, perc_midle_higher))


    # print('global_max_freq: ' +  str(global_max_freq))
    #
    # print("lower_freq: "  + str(lower_freq)  + ' ' + lower_name + ' ' + str(perc_lower_midle))
    # print("midle_freq: "  + str(midle_freq)  + ' ' + midle_name )
    # print("higher_freq: " + str(higher_freq) + ' ' + higher_name + ' ' + str(perc_midle_higher))
    # print(" ")

    return order_of_3_notes

global_max_graph_limit = 1.0	

# Animate the graph, and processes the audio to determine witch are the holes
# that are being played in each moment. The ring buffer / rolling buffer and
# the FFT is calculated inside the callback function of PyAudio.
# The drawing and animations of the harmonica ares made inside the loop of TK
# canvas update. There are 3 independent and loops that aren't synchronized.
# But it work relatively well because if a buffer is not full the user only
# lost one update, and there are several each second. This is a rare event.
def animate(i):
    global maxFFT
    global mic

    global a

    global current_holes_blow_on
    global current_holes_draw_on

    global max_silent_begin_value
    global max_silent_begin_counts
    global max_silent_value

    global min_note_index_to_consider
    global max_note_index_to_consider

    # This function fills this two variables so that, then the cicle of the drawing of
    # the canvas (harmonica) can read them.
    global global_max_freq
    global global_max_bucket_index
    global global_max_nearest_note
    global global_max_graph_limit
	
    # # DDEBUG
    # usage = memory_profiler.memory_usage()
    # print("Begin: " +  str(usage))

    # # DDEBUG
    # usage = memory_profiler.memory_usage()
    # print("End: " +  str(usage))

    if not mic.data is None and not mic.fft is None:
        if min_note_index_to_consider == 0:
            len_FFT_bla = audio_utils.get_len_FFT()
            min_note_index_to_consider = freq2Index(freq=150, samples=44100, nFFT=len_FFT_bla)

        # Removes the DC component from the sinal and the @£§&%*! noise of low frequency
        # from the fan of my Laptop PC:
        local_copy_FFT  = mic.fft.copy()
        local_copy_fftx = mic.fftx.copy()

        local_copy_FFT[0: min_note_index_to_consider + 1 ] = 0.0

        #############
        # Plot da FFT
        a.clear()

        a.plot(local_copy_fftx, local_copy_FFT)
        #new_ylim = (0.0, 1.0)
		#new_ylim = (0.0, 1000000.0)  # Coloquei mais um zero agora está num milhão.
        new_ylim = (0.0, global_max_graph_limit)
        a.set_ylim(new_ylim)

        ##################
        # The index of the upper limite of the buckets that are going to be considered for
        # the determination of the holes.
        # max_note_index_to_consider = 110
        if max_note_index_to_consider == 0:
            len_FFT_bla = audio_utils.get_len_FFT()
            max_note_index_to_consider = freq2Index(freq=2300, samples=44100, nFFT=len_FFT_bla)

        # Determines the index of the peak amplitude note.
        max_index = np.argmax(local_copy_FFT[0:max_note_index_to_consider], axis=0)

        # Determine the ordenated indexes of the notes with more amplitude/intencity.
        # lista_notas_mais_fortes_indices = np.argpartition(mic.fft[0:max_note_index_to_consider], -4)[-4:]

        # print(lista_notas_mais_fortes_indices)

        if max_silent_begin_counts > 0:
            max_silent_begin_value += local_copy_FFT[max_index]
            max_silent_begin_counts -= 1
            max_silent_value = max_silent_begin_value / (10.0 - max_silent_begin_counts)
            # Security margin.
            max_silent_value *= 1.10  # +15%

        max_value = mic.fft[max_index]
        if global_max_graph_limit < max_value:
            global_max_graph_limit = max_value
        current_holes_blow_on, current_holes_draw_on = \
            find_holes_played_based_on_the_bucket_index_value(local_copy_FFT[0:max_note_index_to_consider],
                                                          max_silent_value,
                                                              max_bucket_value=max_value  )

        len_FFT_bla = audio_utils.get_len_FFT()
        max_freq = index2Freq(i=max_index, samples=44100, nFFT=len_FFT_bla ) # nFFT=4096)

        max_note_freq_index = freq2Index(freq = max_freq, samples=44100, nFFT=len_FFT_bla)

        # Fills this 2 global variables so they can be reeded in the function that draws the harmonica.
        global_max_freq         = max_freq
        global_max_bucket_index = max_note_freq_index

        global ordered_notes_names_list
        global ordered_notes_freq_list

        global_max_nearest_note  = find_canvas_nearest_note_str(global_max_freq,
                                                                ordered_notes_names_list,
                                                                ordered_notes_freq_list)

        #######################
        ### The following print line is verry important for debugging!!!
        ### In case of debugging uncommnet!
        #######################
        # print("max_freq: " + str(max_freq ) + " Hz" + " bucket_index: " + str(max_index) + " max_note_index:  " + str(max_note_freq_index))

        # Help the GC to clean the memory of NumPy local_copy_FFT buffer.
        local_copy_FFT  = None
        local_copy_fftx = None


# Function that is used in the initialization of the drawing canvas. Only called once!
def draw_harmonica_init(canvas,
                        global_max_freq = 0.0,
                        global_max_bucket_index = 0,
                        global_max_nearest_note = '?',
                        global_music_velocity = 1.0,
                        list_blow = [],
                        list_draw = [] ):


    x_offset = 3 + 85
    y_offset = 200
    x_hole_offset = 47

    x_offset_max_freq_text = 175 + 85
    y_offset_max_freq_text = 300

    x_offset_max_bucket_index_text = 175 + 85
    y_offset_max_bucket_index_text = 320

    x_offset_max_nearest_note_text = 175 + 85
    y_offset_max_nearest_note_text = 340

    # Freq. range graph.
    x_delta_note_range =  80
    x_offset_note_range_rect = 170
    y_offset_note_range_rect = 360
    x_offset_note_range_text = 170
    y_offset_note_range_text = 380



    # Writes the global_repeat_on_off in the canvas.
    repeat_on_off_text = ''
    if global_repeat_on_off == True:
        repeat_on_off_text = 'Repeat'
    canvas.id_texto_repeat_on_off = canvas.create_text(460, 10, text=repeat_on_off_text,  fill='black')

    # Writes the global_music_velocity in the canvas.
    music_velocity_text = 'Speed: {0:0.2f}'.format(global_music_velocity)
    canvas.id_texto_music_velocity = canvas.create_text(40, 10, text=music_velocity_text,  fill='black')


    # Writes the frequency.
    max_freq_text = 'Peak frequency {0:0.0f}Hz'.format(global_max_freq)
    canvas.id_texto_peak_frequency = canvas.create_text(x_offset_max_freq_text, y_offset_max_freq_text, text=max_freq_text, fill='black')

    # Writes the bucket index.
    max_bucket_index_text = 'Bucket index {0:d} '.format(global_max_bucket_index)
    canvas.id_texto_bucket_index = canvas.create_text(x_offset_max_bucket_index_text, y_offset_max_bucket_index_text, text=max_bucket_index_text, fill='black')

    # Writes the nearest note.
    max_nearest_note_text = 'Nearest note {0} '.format(global_max_nearest_note)
    canvas.id_texto_nearest_note = canvas.create_text(x_offset_max_nearest_note_text, y_offset_max_nearest_note_text, text=max_nearest_note_text, fill='black')


    # Draw's the harmonica, main body.
    canvas.create_rectangle(x_offset + 0, y_offset + 0, x_offset + 350 - 3, y_offset + 20, width=2, outline='black')
    # Draw's the upper part.
    canvas.create_rectangle(x_offset + 30, y_offset - 10, x_offset + 350 - 3 - 30, y_offset, width=2, outline='black')
    # Draw's the lower part.
    canvas.create_rectangle(x_offset + 30, y_offset + 20 , x_offset + 350 - 3 - 30, y_offset + 20 + 10, width=2, outline='black')


    # Draw's the holes.
    canvas.id_rectangulos_list      = []
    canvas.id_rectangulos_text_list = []

    x_delta_begin       = x_offset + x_hole_offset + 0
    x_delta_end         = x_delta_begin + 18
    y_offset_begin      = y_offset + 3
    y_offset_end        = y_offset + 17
    y_offset_text_begin = y_offset + 9

    for hole in range(1, 11):
        color_hole = 'black'
        color_text = 'white'

        id_rectangulo = canvas.create_rectangle( x_delta_begin, y_offset_begin, x_delta_end, y_offset_end, width=2, fill=color_hole) # outline='black')
        # Saves the ID's so that later it can change the canvas objects data.
        canvas.id_rectangulos_list.append(id_rectangulo)
        x_delta_begin_text = x_delta_begin
        if hole != 10:
            x_delta_begin_text += 9
        else:
            x_delta_begin_text += 8

        id_rectangulos_text = canvas.create_text(x_delta_begin_text, y_offset_text_begin, text=str(hole), fill=color_text)
        canvas.id_rectangulos_text_list.append(id_rectangulos_text)
        x_delta_begin = x_delta_end + 8
        x_delta_end   = x_delta_begin + 18

    # Draw freq. range graph.
    # Draw 1º post.
    x_rect_with = 4
    canvas.create_rectangle(x_offset_note_range_rect + 0,
                            y_offset_note_range_rect + 0,
                            x_offset_note_range_rect + x_rect_with,
                            y_offset_note_range_rect + 20,
                            width=1, fill='black')

    # Draw 2º post.
    canvas.create_rectangle(x_offset_note_range_rect + 0 + x_delta_note_range,
                            y_offset_note_range_rect + 0,
                            x_offset_note_range_rect + x_rect_with + x_delta_note_range,
                            y_offset_note_range_rect + 20,
                            width=1, fill='black')

    # Draw 3º post.
    canvas.create_rectangle(x_offset_note_range_rect + 0 + (x_delta_note_range*2) ,
                            y_offset_note_range_rect + 0,
                            x_offset_note_range_rect + x_rect_with + (x_delta_note_range*2),
                            y_offset_note_range_rect + 20,
                            width=1, fill='black')




    x_range_perc = 0.3
    x_range_total_delta =  x_delta_note_range * 2
    x_mov_range_delta_position = int( x_range_total_delta * x_range_perc)

    # Draw moving post.
    id_mov_range_rect = \
        canvas.create_rectangle(x_offset_note_range_rect + 0 + x_mov_range_delta_position,
                                y_offset_note_range_rect + 0,
                                x_offset_note_range_rect + 0 + 4 + x_mov_range_delta_position,
                                y_offset_note_range_rect + 20,
                                width=1, fill='blue')
    # Saves the ID in the canvas variable.
    canvas.id_mov_range_rect = id_mov_range_rect
    canvas.x_delta_note_range = x_delta_note_range
    canvas.x_offset_note_range_rect = x_offset_note_range_rect
    canvas.y_offset_note_range_rect = y_offset_note_range_rect


# Change state of animation of folling notes of music to STOP.
def canvas_note_anim_state_STOP():
    global global_notes_anim

    # Animation states:
    #s_prev_play = 0
    #s_playing   = 1
    s_prev_stop = 2
    #s_stop      = 3
    #s_paused    = 4

    index_state = 1
    global_notes_anim[index_state] = s_prev_stop


def canvas_note_anim_state_PLAY():
    global global_notes_anim

    if global_notes_anim == None:
        return

    # Animation states:
    s_prev_play = 0
    #s_playing   = 1
    #s_prev_stop = 2
    # s_stop      = 3
    #s_paused    = 4

    index_state = 1
    global_notes_anim[index_state] = s_prev_play


# @jit
def draw_anim_notes_state_reset_variabels(canvas,
                                      global_notes_anim,
                                      index_curr_start_note_index,
                                      index_curr_end_note_index,
                                      index_down_offset,
                                      index_state):

    # Deletes all notes objects folling in the Canvas.
    if len(global_notes_anim) > index_curr_end_note_index + 1:
        # print('global_notes_anim: ' + str(global_notes_anim))
        notes_canvas_obj = global_notes_anim[-1]
        for prev_id in notes_canvas_obj:
            canvas.delete(prev_id)
        notes_canvas_obj.clear()

    # curr_start_note_index
    global_notes_anim[index_curr_start_note_index] = 0  # 0
    # curr_end_note_index
    global_notes_anim[index_curr_end_note_index] = 1  # 1
    # curr_down_offset
    global_notes_anim[index_down_offset] = 0
    return


# @jit
def draw_folling_notes( canvas,
                        global_curr_music_score,
                        global_notes_anim,
                        global_music_velocity,
                        global_repeat_on_off):


    x_begin = 134
    y_begin = 10
    y_when_the_notes_desapier = 170

    x_hole_size     = 20
    x_delta_bt_hole = 6
    #music_velocity  = 3 # 1.0     1.5 0.75



    # Animation states:
    s_prev_play = 0
    s_playing   = 1
    s_prev_stop = 2
    s_stop      = 3
    s_paused    = 4

    list_states_str = ['s_prev_play',
                       's_playing',
                       's_prev_stop',
                       's_stop',
                       's_paused']

    index_counter               = 0
    index_state                 = 1
    index_down_offset           = 2
    index_curr_start_note_index = 3
    index_curr_end_note_index   = 4

    g_counter = global_notes_anim[index_counter]
    curr_anim_state = global_notes_anim[index_state]
 #   print("curr_anim_state: ", list_states_str[curr_anim_state])
    if curr_anim_state == s_stop:
        # print("inside s_stop")



        return
    if curr_anim_state == s_prev_stop:
 #       print("inside s_prev_stop")

         # Remove all the notes objects that are folling in the canvas.
        draw_anim_notes_state_reset_variabels(canvas,
                                              global_notes_anim,
                                              index_curr_start_note_index,
                                              index_curr_end_note_index,
                                              index_down_offset,
                                              index_state)

        # Change the state to the s_stop.
        global_notes_anim[index_state] = s_stop
        return

    elif curr_anim_state == s_prev_play:
 #       print("inside s_prev_play")
        # Create all objects.

        # canvas,
        # global_curr_music_score,

        if global_curr_music_score[1] == 'ERRO':
            global_notes_anim[index_state] = s_prev_stop
            return

        # Change state to s_playing.
        global_notes_anim[index_state] = s_playing

    elif curr_anim_state == s_playing:
 #      print("inside s_playing")

        # Updates the position of all objets that correspond to the holes
        # of the notes that are following.


        # If the music_score has errors it doesn't play (the notes don't follow).
        if global_curr_music_score[0] == 'ERRO':
            global_notes_anim[index_state] = s_prev_stop
            return
        # Put's the ovals and deletes them.
        notes_list            = global_curr_music_score[4]
        curr_start_note_index = global_notes_anim[index_curr_start_note_index] # 0
        curr_start_note_index = int(curr_start_note_index)
        curr_end_note_index   = global_notes_anim[index_curr_end_note_index]   # 1
        curr_end_note_index   = int(curr_end_note_index)
        curr_down_offset      = global_notes_anim[index_down_offset]
        # TODO: Start the index from the current position thar hasn't desapeared.

        # Put's the list in the global variable.
        if len(global_notes_anim) == index_curr_end_note_index + 1:
            notes_canvas_obj = []
            global_notes_anim.append(notes_canvas_obj)
        else:
            notes_canvas_obj = global_notes_anim[-1]
            for prev_id in notes_canvas_obj:
                canvas.delete(prev_id)
            notes_canvas_obj.clear()
        l_index_note = 0
        l_flag_no_more_notes = False
        if len(notes_list) < (curr_start_note_index + 1):
            l_flag_no_more_notes = True
        for note in notes_list[curr_start_note_index : curr_end_note_index]:

            # print('note: ' + str(note))
            delta_num_notes = curr_end_note_index - curr_start_note_index

            # list_holes = (note_name, int(hole_final), tab_const_note_duration, blow_draw, bending_type)
            note_name         = note[0]
            note_hole         = note[1]
            note_duration     = note[2]
            note_blow_draw    = note[3]
            note_bending_type = note[4]

            # x_hole_size = 20
            # x_delta_bt_hole = 18

            if note_blow_draw == 'B':
                # Blow
                color_oval = 'yellow'
                color_text = 'black'
            else:
                # Draw
                color_oval = 'magenta'
                color_text = 'white'

            if note_hole != 0:
                id_n = canvas.create_oval(x_begin + (x_hole_size + x_delta_bt_hole) * (note_hole - 1 ),                  # x0
                                          y_begin + curr_down_offset - 20 * (l_index_note + curr_start_note_index),      # y0
                                          x_begin + (x_hole_size + x_delta_bt_hole) * (note_hole - 1 ) + x_hole_size ,   # x1
                                          y_begin + curr_down_offset + 20 - 20 * (l_index_note + curr_start_note_index), # y1
                                          fill=color_oval)

                id_n_text = canvas.create_text( x_begin + 10 + (x_hole_size + x_delta_bt_hole) * (note_hole - 1 ),                 # x0
                                                y_begin + 10 + curr_down_offset - 20 * (l_index_note + curr_start_note_index),
                                                text=note_name,
                                                fill=color_text)

                notes_canvas_obj.append(id_n)
                notes_canvas_obj.append(id_n_text)

            l_index_note += 1


        # To change the velocity of the folling notes the  next 3 values have to be multiplied by a
        # float to rise or lower the velocity (1.0).
        global_notes_anim[index_curr_end_note_index] += (0.05 * global_music_velocity)
        if global_notes_anim[index_down_offset] > y_when_the_notes_desapier:
            global_notes_anim[index_curr_start_note_index] += (0.05 * global_music_velocity)
        global_notes_anim[index_down_offset] += (1 * global_music_velocity)

        if (l_flag_no_more_notes == True):
            if global_repeat_on_off == False:
                # Passa para o estado stop.
                global_notes_anim[index_state] = s_prev_stop
            else:
                # Repeat_on_off = True
                # Clear's all the variables of the playing state and continues in the same state
                # of playing, the only difference is that the musical notes (holes), sill start
                # to appear from the upper part of the canvas again from the zero position.

                # Deletes all note objects that are following in the canvas.
                draw_anim_notes_state_reset_variabels(canvas,
                                                      global_notes_anim,
                                                      index_curr_start_note_index,
                                                      index_curr_end_note_index,
                                                      index_down_offset,
                                                      index_state)

    elif curr_anim_state == s_paused:
 #       print("insinde s_paused")
        pass


#@jit
def draw_harmonica_update(canvas,
                          global_max_freq = 0.0,
                          global_max_bucket_index = 0,
                          global_max_nearest_note = '.',
                          global_curr_music_score = None,
                          global_notes_anim = None,
                          global_music_velocity = 1.0,
                          global_repeat_on_off = False,
                          list_blow = [],
                          list_draw = [] ):


    # Moving range freq. graph.
    #global_max_nearest_note = '.'
    # lower_name  = '.'
    midle_name = '.'      # Important: This is the nearest note!
    # higher_name = '.'
    perc_lower_midle  = 0.0
    perc_midle_higher = 0.0

    if global_max_nearest_note != None and global_max_nearest_note != '.':
        #global_max_freq   = global_max_nearest_note[0]

        lower_name  = global_max_nearest_note[1][0]
        midle_name  = global_max_nearest_note[2]
        higher_name = global_max_nearest_note[3][0]
        perc_lower_midle  = global_max_nearest_note[1][1]
        perc_midle_higher = global_max_nearest_note[3][1]


    #
    # Important: This is the structure of the variable that we receive.
    #
    # order_of_3_notes = ( global_max_freq,
    #                     (lower_name, perc_lower_midle),
    #                     (midle_name),
    #                     (higher_name, perc_midle_higher))


    # Writes the global_repeat_on_off in the canvas.
    repeat_on_off_text = ''
    if global_repeat_on_off == True:
        repeat_on_off_text = 'Repeat'
    canvas.itemconfigure(canvas.id_texto_repeat_on_off, text=repeat_on_off_text)

    # Writes the global_music_velocity in the canvas.
    music_velocity_text = 'Speed: {0:0.2f}'.format(global_music_velocity)
    canvas.itemconfigure(canvas.id_texto_music_velocity, text=music_velocity_text)

    # Updates the canvas frequency.
    max_freq_text = 'Peak freq {0:0.0f}Hz'.format(global_max_freq)
    canvas.itemconfigure(canvas.id_texto_peak_frequency, text=max_freq_text)

    # Updates the canvas bucket index.
    max_bucket_index_text = 'Bucket index {0:d} '.format(global_max_bucket_index)
    canvas.itemconfigure(canvas.id_texto_bucket_index, text=max_bucket_index_text)

    # Updates the canvas nearest note.
    #max_nearest_note_text = 'Nearest note {0} '.format(global_max_nearest_note)
    max_nearest_note_text = 'Nearest note {} '.format(midle_name)
    canvas.itemconfigure(canvas.id_texto_nearest_note, text=max_nearest_note_text)

    # Draw's the animation of the notes folling.
    if     global_curr_music_score != None \
       and global_notes_anim != None \
       and global_curr_music_score[0] != 'ERROR':

     #  print('Before entering the function, draw_folling_notes() .')

        draw_folling_notes( canvas,
                            global_curr_music_score,
                            global_notes_anim,
                            global_music_velocity,
                            global_repeat_on_off)

     #   print('After exiting the function, draw_folling_notes() .')
     #   print('')

    # Updates the holes color, based on the hole sbeing played.
    for hole in range(1, 11):
        color_hole = 'black'
        color_text = 'white'
        if hole in list_blow:
            color_hole = 'yellow'
            color_text = 'black'
        elif hole in list_draw:
            color_hole = 'magenta'
            color_text = 'white'

        # Get's the canvas object (hole of the harmonica) from the ID then we are going to alter it's color.
        list_number = hole - 1
        canvas.itemconfigure(canvas.id_rectangulos_list[list_number], fill=color_hole)
        # Get's the text object of the hole, and writes it with a contrast color depending on the
        # holes color. Blow or Draw.
        canvas.itemconfigure(canvas.id_rectangulos_text_list[list_number], fill=color_text)

        # The drawn objects are in a Z-stack, that means that the latter drawed object is normally upper
        # in the stack and that the first draw are lower in the stack.
        # With the next instructions we rise in the Z-Stack the position of the holes and the text number
        # of the holes upper position, to the front screen of the Z-Stack.
        canvas.tag_raise(canvas.id_rectangulos_list[list_number])
        canvas.tag_raise(canvas.id_rectangulos_text_list[list_number])

    # Moving range freq. graph.
    x_mov_range_delta_position = int( canvas.x_delta_note_range * perc_lower_midle + \
                                      canvas.x_delta_note_range * perc_midle_higher )

    # If it has a diference lower then 10% from the frequency position it changes  it changes the
    # color of the light (moving bar of the frequency) to yellow.
    color_mov_range = 'blue'
    if 0.90 <= perc_lower_midle <= 1.1 and -0.1 <= perc_midle_higher <= 0.10:
        color_mov_range = 'yellow'

    # Redraw moving range graph post.
    canvas.coords(canvas.id_mov_range_rect,
                    (canvas.x_offset_note_range_rect + 0 + x_mov_range_delta_position,
                     canvas.y_offset_note_range_rect + 0,
                     canvas.x_offset_note_range_rect + 0 + 4 + x_mov_range_delta_position,
                     canvas.y_offset_note_range_rect + 20))
    canvas.itemconfigure(canvas.id_mov_range_rect,
                         fill=color_mov_range)


current_holes_blow_on = []
current_holes_draw_on = []

def update_loop():
    global current_holes_blow_on
    global current_holes_draw_on
    global g_canvas

    global global_max_freq
    global global_max_bucket_index
    global global_max_nearest_note
    global global_curr_music_score
    global global_notes_anim
    global global_music_velocity
    global global_repeat_on_off

    draw_harmonica_update(g_canvas,
                          global_max_freq,
                          global_max_bucket_index,
                          global_max_nearest_note,
                          global_curr_music_score,
                          global_notes_anim,
                          global_music_velocity,
                          global_repeat_on_off,
                          current_holes_blow_on,
                          current_holes_draw_on)

    # print("len: "+ str(current_holes_blow_on))


def event_on_root_main_windows_close( ):
    global mic
    global ani
    global g_is_running

    print(" - enter event on root main window close.")
    ani.event_source.stop()
    g_is_running = False
    mic.close()
    print(" - exit event on root main window close.")
    exit(0)


class HarmonicaOneNoteApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #####################
        # Register the event function callback on the window Close.
        self.protocol("WM_DELETE_WINDOW", event_on_root_main_windows_close)

        # To change the icon.
        #tk.Tk.iconbitmap(self, default="icon_name.ico")
        tk.Tk.wm_title(self, "Harmonica - The good kind of feedback!")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for my_frame in (FrontPage, MainPage):
            frame = my_frame(container, self)
            self.frames[my_frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(FrontPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


        
class FrontPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Let's start to play harmonica...", font=LARGE_FONT)
        label.pack(side=tk.TOP, pady=10,padx=10)

        button3 = ttk.Button(self, text="Learn to play single notes",
                            command=lambda: controller.show_frame(MainPage))
        button3.pack(side=tk.TOP)


        # IMPORTANTE: The following 2 lines depend on the Lib Pillow.
        # Imagem inicial da harmonica.
        image = Image_PIL.open("imagem_harmonica_v001_400_300.jpg")
        photo = ImageTk_PIL.PhotoImage(image)

        label_image = ttk.Label(self, image=photo)
        label_image.image = photo  # keep a reference!
        label_image.pack(side=tk.TOP, pady=90, padx=50)

def event_butt_load_music():
    # print('\n event_butt_load_music()')
    global global_curr_music_score
    canvas_note_anim_state_STOP()

    fname = askopenfilename_tk(filetypes=(("Harmonica simple tablature files", "*.tab"),
                                       ("Harmonica complex score/tablature files", "*.har"),
                                       ("All files", "*.*")))
    if fname:
        try:
            # print('fname: ' + fname)
            global_curr_music_score = mfp.parser_tab_simple_music_file(fname)

            if global_curr_music_score != None and global_curr_music_score[0] != 'ERRO':
                global global_label_filename
                fname_text = 'Filename: ' + fname
                global_label_filename.config(text=fname_text)
                global global_label_title
                title = 'Title: ' + global_curr_music_score[2]
                global_label_title.config(text=title)
                global global_label_key
                key = 'Key: ' + global_curr_music_score[3]
                global_label_key.config(text=key)
            else:
                if global_curr_music_score != None:
                    showerror_tk("Open Music File", global_curr_music_score[1])

        except:
            showerror_tk("Open Music File", "Failed to read file\n'%s'" % fname)
        return


def event_butt_stop():
    # print('\n event_butt_stop()')
    canvas_note_anim_state_STOP()

def event_butt_play():
    # print('\n event_butt_play()')
    canvas_note_anim_state_PLAY()

def event_butt_velocity_plus():
    # print('\n event_butt_velocity_plus()')
    global global_music_velocity
    if global_music_velocity < 4.91:
        global_music_velocity += 0.1

def event_butt_velocity_minus():
    # print('\n event_butt_velocity_minus()')
    global global_music_velocity
    if 0.51 < global_music_velocity:
        global_music_velocity -= 0.1

def event_butt_repeat_on_off():
    # print('\n event_butt_velocity_minus()')
    global global_repeat_on_off
    if global_repeat_on_off == False:
        global_repeat_on_off = True
    else:
        global_repeat_on_off = False



class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Learn to play single notes!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="See a nice harmonica",
                            command=lambda: controller.show_frame(FrontPage))
        button1.pack(pady=10,padx=10)


        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=5,padx=5)


        butt_load_music = ttk.Button(frame_buttons, text="Load music",
                            command=event_butt_load_music )
        butt_load_music.pack(side=tk.LEFT, pady=5,padx=10)

        butt_stop = ttk.Button(frame_buttons, text="Stop",
                            command=event_butt_stop )
        butt_stop.pack(side=tk.LEFT, pady=5,padx=10)

        butt_play = ttk.Button(frame_buttons, text="Play",
                            command=event_butt_play )
        butt_play.pack(side=tk.LEFT, pady=5,padx=10)

        butt_velocity_plus = ttk.Button(frame_buttons, text="-",
                            command=event_butt_velocity_minus )
        butt_velocity_plus.pack(side=tk.LEFT, pady=5,padx=10)

        butt_velocity_minus = ttk.Button(frame_buttons, text="+",
                            command=event_butt_velocity_plus )
        butt_velocity_minus.pack(side=tk.LEFT, pady=5,padx=10)

        butt_repeat_on_off = ttk.Button(frame_buttons, text="Repeat ON/OFF",
                            command=event_butt_repeat_on_off )
        butt_repeat_on_off.pack(side=tk.LEFT, pady=5,padx=10)



        frame_lables = tk.Frame(self)
        frame_lables.pack(pady=2,padx=2)

        global global_label_filename
        label_filename = tk.Label(frame_lables, text="Filename: ", font=LARGE_FONT)
        label_filename.pack(side=tk.BOTTOM, pady=2,padx=2)
        global_label_filename = label_filename

        global global_label_title
        label_title = tk.Label(frame_lables, text="Title:", font=LARGE_FONT)
        label_title.pack(pady=2, padx=2)
        global_label_title = label_title

        global global_label_key
        label_key = tk.Label(frame_lables, text="key: ", font=LARGE_FONT)
        label_key.pack( pady=2, padx=2)
        global_label_key = label_key

        harmonica_canvas = tk.Canvas(self, width=500, height=400)
        harmonica_canvas.pack(side=tk.LEFT, pady=10,padx=10)

        # Cria uma variavel global com a canvas.
        global g_canvas
        g_canvas = harmonica_canvas

        global global_music_velocity

        # Draw the harmonica.
        draw_harmonica_init( harmonica_canvas, global_music_velocity )


        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        #canvas.show()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10,padx=10)

        global maxFFT
        global mic

        maxFFT=0
        device_mic = 0 # 0, 1
        mic = audio_utils.AudioUtils(device=device_mic,rate=44100,updatesPerSecond=20)
        mic.stream_start()


if __name__ == "__main__":
    app = HarmonicaOneNoteApp()
    ani = animation.FuncAnimation(f, animate, interval=200) # interval=1000)

    app.wait_visibility(app)

    g_is_running = True
    while g_is_running:
        app.update()
        app.update_idletasks()
        update_loop()
        global_notes_anim[index_counter] += 1
        time.sleep(0.05)
    print(" - TK exited.")

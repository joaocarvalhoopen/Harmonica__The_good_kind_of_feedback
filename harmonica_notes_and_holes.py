

# Harmonica notes and holes.


dic_notes = {
'E3': 164.81,
'F3': 174.61,
'F#3': 185.00,
'G3': 196.00,
'G#3': 207.65,
'A3': 220.00,
'A#3': 233.08,
'B3': 246.94,
'C4': 261.63,
'C#4': 277.18,
'D4': 293.66,
'D#4': 311.13,
'E4': 329.63,
'F4': 349.23,
'F#4': 369.99,
'G4': 392.00,
'G#4': 415.30,
'A4': 440.00,
'A#4': 466.16,
'B4': 493.88,
'C5': 523.25,
'C#5': 554.37,
'D5': 587.33,
'D#5': 622.25,
'E5': 659.25,
'F5': 698.46,
'F#5': 739.99,
'G5': 783.99,
'G#5': 830.61,
'A5': 880.00,
'A#5': 932.33,
'B5': 987.77,
'C6': 1046.50,
'C#6': 1108.73,
'D6': 1174.66,
'D#6': 1244.51,
'E6': 1318.51,
'F6': 1396.91,
'F#6': 1479.98,
'G6': 1567.98,
'G#6': 1661.22,
'A6': 1760.00,
'A#6': 1864.66,
'B6': 1975.53,
'C7': 2093.00,
'C#7': 2217.46,
'D7' : 2349.32}


def get_external_dic_notes():
    global dic_notes
    return dic_notes



# This is for an harmonica in the key of C.


# Hole	1	2	3	4	5	6	7	8	9	10
# Blow	C	E	G	C	E	G	C	E	G	C
# Draw	D	G	B	D	F	A	B	D	F	A

#           (hole, freq, note, Blow/Draw, delta, bucket_index)    # The bucket index is calculated at the begining.
list_holes = [[1,  261.0,  'C', 'C4', 'B', 1],  # Blow
              [2,  329.0,  'E', 'E4', 'B', 1],
              [3,  392.0,  'G', 'G4', 'B', 1],  # This note repeats in the harmonica. (blow/draw)
              [4,  523.0,  'C', 'C5', 'B', 1],
              [5,  659.0,  'E', 'E5', 'B', 1],
              [6,  784.0,  'G', 'G5', 'B', 1],
              [7,  1046.0, 'C', 'C6', 'B', 2], # 1
              [8,  1319.0, 'E', 'E6', 'B', 2], # 1
              [9,  1568.0, 'G', 'G6', 'B', 3], # 2
              [10, 2093.0, 'C', 'C7', 'B', 4], # 3 2


              [1,  293.0,  'D', 'D4', 'D', 1], # 0  # Draw
              [2,  392.0,  'G', 'G4', 'D', 1], # 0   # This note repeats in the harmonica. (blow/draw)
              [3,  494.0,  'B', 'B4', 'D', 1],
              [4,  587.0,  'D', 'D5', 'D', 1],
              [5,  698.0,  'F', 'F5', 'D', 1],
              [6,  880.0,  'A', 'A5', 'D', 1],
              [7,  988.0,  'B', 'B5', 'D', 1],
              [8,  1174.0, 'D', 'D6', 'D', 1],
              [9,  1397.0, 'F', 'F6', 'D', 1],
              [10, 1760.0, 'A', 'A6', 'D', 2 ] ]


def get_external_list_holes():
    global list_holes
    return list_holes


# This data is used to determine wich musical note is nearest the peak that apears at each moment in the microphone.

ordered_notes_name_list  = ['E3',
                            'F3',
                            'F#3',
                            'G3',
                            'G#3',
                            'A3',
                            'A#3',
                            'B3',
                            'C4',
                            'C#4',
                            'D4',
                            'D#4',
                            'E4',
                            'F4',
                            'F#4',
                            'G4',
                            'G#4',
                            'A4',
                            'A#4',
                            'B4',
                            'C5',
                            'C#5',
                            'D5',
                            'D#5',
                            'E5',
                            'F5',
                            'F#5',
                            'G5',
                            'G#5',
                            'A5',
                            'A#5',
                            'B5',
                            'C6',
                            'C#6',
                            'D6',
                            'D#6',
                            'E6',
                            'F6',
                            'F#6',
                            'G6',
                            'G#6',
                            'A6',
                            'A#6',
                            'B6',
                            'C7',
                            'C#7'
                            'D7' ]


def get_external_orde_notes_name_list():
    global ordered_notes_name_list
    return ordered_notes_name_list


ordered_notes_freq_list = [ 164.81,
                            174.61,
                            185.00,
                            196.00,
                            207.65,
                            220.00,
                            233.08,
                            246.94,
                            261.63,
                            277.18,
                            293.66,
                            311.13,
                            329.63,
                            349.23,
                            369.99,
                            392.00,
                            415.30,
                            440.00,
                            466.16,
                            493.88,
                            523.25,
                            554.37,
                            587.33,
                            622.25,
                            659.25,
                            698.46,
                            739.99,
                            783.99,
                            830.61,
                            880.00,
                            932.33,
                            987.77,
                            1046.50,
                            1108.73,
                            1174.66,
                            1244.51,
                            1318.51,
                            1396.91,
                            1479.98,
                            1567.98,
                            1661.22,
                            1760.00,
                            1864.66,
                            1975.53,
                            2093.00,
                            2217.46,
                            2349.32 ]


def get_external_orde_notes_freq_list():
    global ordered_notes_freq_list
    return ordered_notes_freq_list


#
# Filename: music_file_parser.py
#
# Description: There are 2 music file types. One is simple tablature the other is complex but more powerfull.
#              The tablature one has the extension '.tab' and the complex one has the extension '.har'.
#              The music files can be in any directory, but currently they are in 'music_for_harmonica'.
#
#              TODO: Explain the 2  file formats!
#
#

import re

tab_const_note_duration = 1

def parser_tab_simple_music_file(filename):
    """    Input: Only the name of the file_path.

           Structure of the return.

           list_holes = ( note_name, int(hole_final), tab_const_note_duration, blow_draw, bending_type )
           music_score = ('.tab', filename, title, key, list_holes )
           return music_score
    """

    #filename_path = get_music_directory() + filename
    filename_path = filename

    data_lines = []
    # Open the file for reading but closes automatically the file, even in the case of exception!
    with open(filename_path, "r") as file:
        data_lines = file.readlines()

    if len(data_lines) <= 3:
        return ('ERRO', 'Error parsing file, the must be at least 3 lines in the file!' )

    # TODO: Check if the last [1] of the following lines doesn't give an ERROR in the case it doesn't exist a string
    #       after the ':' in the file ".tab" .

    # Reads the title and the key of the harmonica.
    # Note: We are presumming that the order of the file is always the same!
    title = data_lines[0].split(':')[1]
    key   = data_lines[1].split(':')[1]
    list_holes = []
    # print(data_lines)
    line_num = 2
    for line in data_lines[2:]:
        # print(line)

        # It has a comment simbol, and it ignores lines started with it so that we can have lyrics in the tab files.
        if line.startswith('#'):
            line_num += 1
            continue

        # Ignores the lines that only have white spaces or tabs.
        line_tmp = line.lstrip()
        if line_tmp == '\n' or line_tmp == '\r\n' or line_tmp == '':
            # Note: In this point we can have 2 different types of symbol for ending a line in the file.
            # One for Windows and other for Linux, '\r\n' and '\n', there is one lib that is dependent of the OS
            # to obtain wich of this line terminators is the correct for our OS!
            # I ignore also the empty lines.
            line_num += 1
            continue

        # Remove ending line caracter '\r\n' or '\n'.
        if line.endswith('\r\n'):
            line = line[:-2]
        elif line.endswith('\n'):
            line = line[:-1]
        line= line.rstrip()
        line = line.lstrip()
        # Remove the duplicate spaces between the holes in the tablature for
        # every line.
        line = re.sub(' +', ' ', line)
        line = re.sub('\t+', ' ', line)
        # All notes/holes_are separated by a space.
        file_list_holes = line.split(' ')
        for hole in file_list_holes:
            note_name = hole
            blow_draw = 'B'
            if hole.startswith('-'):
                blow_draw = 'D'
                hole = hole[1:]

            # Here we should validate if the hole can have the bending corresponding to one specific Key
            # ( Note: This part at the momento i don't have certain if it changes with the key, I think that it can be
            # constant for the hole in every key. That is the note changes but not the position!)
            bending_type = 0 # No bendings!

            if hole.endswith("'''"):
                bending_type = 3
                hole = hole[:-3]
            elif hole.endswith("''"):
                bending_type = 2
                hole = hole[:-2]
            elif hole.endswith("'"):
                bending_type = 1
                hole = hole[:-1]

            hole_final = 1
            #print('line_num: ' + str(line_num) + ' hole: ' + hole + ' note_name: ' + note_name)
            if hole in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'):
                hole_final = hole
            else:
                return ('ERRO', 'Error at line "{}" "{}" the tab hole must be a num between 0 and 10 !'.format(line_num, note_name))

            list_holes.append( ( note_name, int(hole_final), tab_const_note_duration, blow_draw, bending_type ) )
        line_num += 1

    music_score = ( '.tab', filename, title, key, list_holes )
    return music_score


def parser_har_complex_music_file(filename):
    data_lines = []
    # Open the file for reading but closes automatically the file, even in the case of exception!
    with open(filename, "r") as file:
        data_lines = file.readlines()


    # TODO: Implement!

    music_score = ()
    return music_score


if __name__ == "__main__":
    # filename = 'ode_to_joy_by_beethoven.tab'
    filename = 'music_10.tab'
    filepath = './/music_for_hamonica//' + filename
    music_score = parser_tab_simple_music_file(filepath)
    print(music_score)





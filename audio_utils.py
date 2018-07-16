# This file is a highlly modifed version of the file SWHear.py
# from https://github.com/swharden/Python-GUI-examples
# http://www.SWHarden.com

# The License for this file is MIT License, for the original and for all my modifications.

# This was only used to make a profile of the object used in memory.
# import memory_profiler

# Optimization of the code, compilling it in JIT with NUMBA (only works with the Anaconda distribution).
# But right now it's not being used because it's not nedded.
#from numba import jit
# We have to put the tag @jit in the line before the function that we whan't to optimize, only works with functions.
# @jit

import pyaudio
import time
import numpy as np
import threading

# import harmonica_notes_and_holes
from harmonica_notes_and_holes import get_external_list_holes, get_external_orde_notes_name_list, get_external_orde_notes_freq_list

# Global variable that is defined in the main source file.
# list_holes = harmonica_notes_and_holes.get_external_list_holes()
list_holes = get_external_list_holes()

# We are going to join 4 buffer de 2205 and only then we calculate the FFT, in the hope that by making the
# input buffer longer (more samples) we can have a FFT with more points and  make a smaller bucket size,
# int he hope that the lower differences in frequencies of the lower notes can be weel separated between Blow
# and Draw. And not miss-mached. We are going to have 4 buckets for each bucket.
flag_FFT_buffer_part_num = 0

len_FFT = 0

def get_len_FFT():
    global len_FFT
    return len_FFT


#@jit
def realtime_processa_buffers_de_rolling_FFT( self, flag_FFT_buffer_part_num ):
    if flag_FFT_buffer_part_num == 0:
        #print("data_buffer_0")

        # Free the memory of the previous buffer, I think that NumPy has optimizations for detecting this instruction,
        # not sure.
        self.data_buffer_0 = None
        # Fill's the first part of the buffer (buffer_1).
        self.data_buffer_0 = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        flag_FFT_buffer_part_num += 1

        # We have to initialize the buffers in the first time, while the program is running the buffer has
        # always the some size and call the FFT with the same number of points.
        if self.data_buffer_1 is None:
            len_buffer_0 = len(self.data_buffer_0)
            self.data_buffer_1 = np.zeros(len_buffer_0, dtype=np.int16)
            self.data_buffer_2 = np.zeros(len_buffer_0, dtype=np.int16)
            self.data_buffer_3 = np.zeros(len_buffer_0, dtype=np.int16)

        self.data = np.concatenate([self.data_buffer_1,
                                    self.data_buffer_2,
                                    self.data_buffer_3,
                                    self.data_buffer_0])

    elif flag_FFT_buffer_part_num == 1:
        #print("data_buffer_1")

        # Free's the memory of the previous buffer.
        self.data_buffer_1 = None
        self.data_buffer_1 = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        flag_FFT_buffer_part_num += 1

        self.data = np.concatenate([self.data_buffer_2,
                                    self.data_buffer_3,
                                    self.data_buffer_0,
                                    self.data_buffer_1])

    elif flag_FFT_buffer_part_num == 2:
        #print("data_buffer_2")

        # Free's the memory of the previous buffer.
        self.data_buffer_2 = None
        self.data_buffer_2 = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        flag_FFT_buffer_part_num += 1

        self.data = np.concatenate([self.data_buffer_3,
                                    self.data_buffer_0,
                                    self.data_buffer_1,
                                    self.data_buffer_2])


    elif flag_FFT_buffer_part_num == 3:
        #print("data_buffer_3")

        # Free's the memory of the previous buffer.
        self.data_buffer_3 = None
        self.data_buffer_3 = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        flag_FFT_buffer_part_num = 0

        # Joins the 4 buffers in one buffer (ex: thee 2205 sample join to become 4405--> 8810 values---> 13230 values),
        # Isn't a power of two but is the best we can do.
        # Don't forget that the power of Two FFT's are have a faster execution, because of the buterfly algorithm.
        self.data = np.concatenate([self.data_buffer_0,
                                    self.data_buffer_1,
                                    self.data_buffer_2,
                                    self.data_buffer_3])
        # Delete the buffers tnat are not used..
        # del self.data_buffer_0
        # del self.data_buffer_1
        # del self.data_buffer_2
        # del self.data_buffer_3

        # self.data_buffer_0 = None
        # self.data_buffer_1 = None
        # self.data_buffer_2 = None
        # self.data_buffer_3 = None

    return flag_FFT_buffer_part_num

#@jit
def getFFT(data, rate):
    # returns FFTfreq and FFT, half.

    # print("len(data): " + str(len(data)) + " --- " + " rate: " + str(rate) )
    len_data = len(data)
    data = data * np.hamming(len_data)
    fft = np.fft.rfft(data)
    fft = np.abs(fft)

    ret_len_FFT = len(fft)

    freq = np.fft.rfftfreq(len_data, 1.0 / rate)
    return ( freq[:int(len(freq) / 2)], fft[:int(ret_len_FFT / 2)], ret_len_FFT )


class AudioUtils():
    """
     Read the data from microphone.

     Arguments:
        
        device: Blanck to detect automatically the sound card device,
                or give a number to specify a specific sound card.

        rate - The sample rate, but it defaults do the value for the device.
        
        updatesPerSecond - the number of buffers obtained from the device per second.
    """

    def __init__(self,device=None,rate=None,updatesPerSecond=10):
        self.p=pyaudio.PyAudio()
        self.chunk=4096 # This value can change by the device, in my case is 2205 samples.
        self.updatesPerSecond=updatesPerSecond
        self.chunksRead=0
        self.device=device
        self.rate=rate


    ### SYSTEM TESTS

    def valid_low_rate(self,device):
        """set the rate to the lowest supported audio rate."""
        for testrate in [44100]:
            if self.valid_test(device,testrate):
                return testrate
        print("...something is wrong, can't use the device, maybe you have more devices that device 0 (zero)",device)
        return None

    def valid_test(self,device,rate=44100):
        """given a device ID and a rate, return TRUE/False if it's valid."""
        try:
            self.info=self.p.get_device_info_by_index(device)
            if not self.info["maxInputChannels"]>0:
                return False
            stream=self.p.open(format=pyaudio.paInt16,channels=1,
               input_device_index=device,frames_per_buffer=self.chunk,
               rate=int(self.info["defaultSampleRate"]),input=True)
            stream.close()
            return True
        except:
            return False

    def valid_input_devices(self):
        """
        See which devices can be opened for microphone input.
        call this when no PyAudio object is loaded.
        """
        mics=[]
        for device in range(self.p.get_device_count()):
            if self.valid_test(device):
                mics.append(device)
        if len(mics)==0:
            print("no microphone devices found!")
        else:
            print("found %d microphone devices: %s"%(len(mics),mics))
        return mics

    ### SETUP AND SHUTDOWN

    def initiate(self):
        """run this after changing settings (like rate) before recording"""
        if self.device is None:
            self.device=self.valid_input_devices()[0] # pick the first one
        if self.rate is None:
            self.rate=self.valid_low_rate(self.device)
        self.chunk = int(self.rate/self.updatesPerSecond) # hold one tenth of a second in memory
        if not self.valid_test(self.device,self.rate):
            print("guessing a valid microphone device/rate...")
            self.device=self.valid_input_devices()[0] #pick the first one
            self.rate=self.valid_low_rate(self.device)
        self.datax=np.arange(self.chunk)/float(self.rate)
        msg='recording from "%s" '%self.info["name"]
        msg+='(device %d) '%self.device
        msg+='at %d Hz'%self.rate
        print(msg)

    def close(self):
        """gently detach from things."""
        print(" - sending stream termination command...")
        self.keepRecording=False #the threads should self-close
        while(self.t.isAlive()): #wait for all threads to close
            time.sleep(.1)
        self.stream.stop_stream()
        self.p.terminate()

    ### STREAM HANDLING

    def stream_readchunk(self):
        """reads some audio and re-launches itself"""
        global flag_FFT_buffer_part_num

        ##############
        # Rolling buffer.....
        #####

        data_buffer_initial = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        len_buffer = len(data_buffer_initial)
        step = len_buffer
        len_buffer_rolling = len_buffer * 4
        #len_buffer_rolling = len_buffer * 8
        #len_buffer_rolling = len_buffer * 32

        # Inicializes the rolling buffer.
        self.data = np.zeros(len_buffer_rolling, 'f')

        try:

            # # DDEBUG
            # usage = memory_profiler.memory_usage()
            # print("Begin: " +  str(usage))

          # # # DDEBUG
          # # usage = memory_profiler.memory_usage()
          # # print("End: " +  str(usage))

            while(self.keepRecording == True):

                #flag_FFT_buffer_part_num = realtime_processa_buffers_de_rolling_FFT(self, flag_FFT_buffer_part_num)

                #print("self.rate: " + str(self.rate))

                ######################################
                ######################################

                ###########
                # Rolling buffer.....
                #####

                # Rolles the rolling buffer.
                self.data = np.roll(self.data, -step)
                self.data[-step:] = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)

                ######################################
                ######################################

                # The sample buffer data that comes from the sound card is always copied, but the FFT
                # only calculates half the number of times the buffer is copied. Altough it contains
                # all the data.
                # Note: Currently it calculates all the times because we are using a rolling buffer
                #       it has a higher performance. And I think that we can even use a deeper rolling
                #       buffer and a FFT with more data points. That would give us more precision in
                #       the graph that we show for the bending of notes.
                #
                if (flag_FFT_buffer_part_num == 0 or
                   flag_FFT_buffer_part_num == 2):
                    # Calc FFT.
                    self.fftx, self.fft, ret_lenFFT = getFFT(self.data, self.rate)

                    global len_FFT
                    len_FFT = ret_lenFFT

                self.chunksRead+=1
                time.sleep(0.0001)

        except Exception as E:
            print(" - an exception ocorred!")
            self.keepRecording=False

        self.stream.close()
        self.p.terminate()
        print(" - stream STOPPED")
        self.chunksRead+=1


    def stream_thread_new(self):
        self.t=threading.Thread(target=self.stream_readchunk)
        self.t.start()


    def stream_start(self):
        """adds data to self.data until termination signal"""
        self.initiate()
        print(" - starting audio stream")
        self.keepRecording=True # set this to False later to terminate stream
        self.data=None # will fill up with threaded recording data
        self.fft=None
        self.data_buffer_0 = None
        self.data_buffer_1 = None
        self.data_buffer_2 = None
        self.data_buffer_3 = None

        self.stream=self.p.open(format=pyaudio.paInt16,channels=1,
                      rate=self.rate,input=True,frames_per_buffer=self.chunk)
        self.stream_thread_new()

# if __name__== "__main__":
#     mic=AudioUtils(updatesPerSecond=10)
#     mic.stream_start() # Starts a new loop inside a new thread.
#     lastRead=mic.chunksRead
#     while True:
#         while lastRead==mic.chunksRead:
#             time.sleep(.01)
#         print(mic.chunksRead,len(mic.data))
#         lastRead=mic.chunksRead

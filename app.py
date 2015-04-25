import pyaudio, libardrone, time, wave, math, struct

CHUNK = 1024
WIDTH = 2
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 500000
WAVE_FILE = "temp.wav"
FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()
# drone = libardrone.ARDrone()

all=[]

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                frames_per_buffer=CHUNK)

print("* recording")

# # Have drone takeoff
# drone.takeoff()
# time.sleap(1.5)

def control_drone(value):
    pass


for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    try:
        data = stream.read(CHUNK)
    except:
        continue
    all.append(data)

    if len(all)>1:
        data = ''.join(all)
        wf = wave.open(WAVE_FILE, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()
        w = wave.open(WAVE_FILE, 'rb')
        summ = 0
        value = 1
        delta = 1
        amps = [ ]
        for i in xrange(0, w.getnframes()):
            data = struct.unpack('<h', w.readframes(1))
            summ += (data[0]*data[0]) / 2
            if (i != 0 and (i % 1470) == 0):
                value = int(math.sqrt(summ / 1470.0) / 10)
                amps.append(value - delta)
                summ = 0
                tarW=str(amps[0]*1.0/delta/100)
                #ser.write(tarW)
                print(tarW)
                delta = value
        all=[]


print("* done")


stream.stop_stream()
stream.close()

p.terminate()

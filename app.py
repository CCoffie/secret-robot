import pyaudio, time, wave, math, struct, zerorpc, ps_drone

CHUNK = 1024
WIDTH = 2
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 500000
WAVE_FILE = "temp.wav"
FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                frames_per_buffer=CHUNK)

print("* recording")


# Have drone takeoff
drone = ps_drone.Drone()       # Initializes the PS-Drone-API
drone.startup()                # Connects to the drone and starts subprocesses
drone.reset()

drone.setConfig("control:altitude_max","3000")
drone.setConfig("control:altitude_min","150")


def get_altitude():
    return drone.NavData()


print(get_altitude())
drone.takeoff()                # Drone starts
time.sleep(2.5)                # Gives the drone time to start
print(get_altitude())

time.sleep(1.5)

maxNormal=1
prevVals=[0,255]
prev=0

def audio_value(value):
    global maxNormal
    global prev
    global prevVals
    value = float(value)
    maxNormal = float(maxNormal)
    if value > maxNormal:
		maxNormal = value
    normalized = value / maxNormal * 100 # Change here for different values
    normalized = int(normalized)
    prevVals.append(normalized)
    while len(prevVals)>=100:
    	prevVals=prevVals[1:]
    	if sum(prevVals)*1.0/len(prevVals)<=10:
    		minNormal=1
    		maxNormal=1
    norm = (normalized + prev) / 2
    prev = normalized
    return norm

def control_drone(value):
    soundValue = audio_value(value)
    if soundValue <= 0:
        soundValue = 1
    # Control the quadcopter now
    maxAltitude = 3000
    targetAltitude = ( maxAltitude * soundValue ) / 100
    print(targetAltitude)

    currentAltitude = get_altitude()

    if targetAltitude < currentAltitude:
        drone.moveUp()
    elif targetAltitude > currentAltitude:
        drone.moveDown()
    else:
        drone.hover()

# Get sound from MIC
all=[]
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
                control_drone(tarW)
                delta = value
        all=[]


print("* done")


stream.stop_stream()
stream.close()

p.terminate()

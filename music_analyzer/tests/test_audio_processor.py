import pyaudio
import wave

# 录制音频测试
def record_audio(filename, record_seconds=3):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)
    
    print("开始录音...")
    frames = []
    
    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("录音结束")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # 保存录音
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# 播放音频测试
def play_audio(filename):
    chunk = 1024
    
    wf = wave.open(filename, 'rb')
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    
    data = wf.readframes(chunk)
    
    print("开始播放...")
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("播放结束")

# 测试
if __name__ == "__main__":
    filename = "test.wav"
    record_audio(filename)
    play_audio(filename)
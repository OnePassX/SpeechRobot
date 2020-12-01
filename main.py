
# -*- coding: utf-8 -*-#
# -------------------------------
# Name:SpeechRobot
# Author:Json.Xu
# Date:2020.12.01
# 用python3实现自己的语音对话机器人
# -------------------------------
 
from aip import AipSpeech
import requests
import json
import speech_recognition as sr
import win32com.client
import pyttsx3
import pyaudio
import numpy as np
from tqdm import tqdm
import wave
import time
 
# 初始化语音
speaker = win32com.client.Dispatch("SAPI.SpVoice")


# 1、语音生成音频文件,录音并以当前时间戳保存到voices文件中
# Use SpeechRecognition to record 使用语音识别录制
# 注意：录制设备杂音要求很低
def my_record(rate=16000):
    r = sr.Recognizer()
    m=sr.Microphone(sample_rate=rate)
    with m as source:
        r.energy_threshold=4000#初始化声音阈值
        r.dynamic_energy_threshold=True#自动调整声音阈值
        r.pause_threshold=0.5#最长暂停时间
        r.operation_timeout=8#设置录音超时时间
        print("please say something")
        audio=r.listen(source)

    #写入文件
    with open("myvoices.wav", "wb") as f:
        f.write(audio.get_wav_data())

# 第二种录音方式
# 使用pyaudio库进行录音
# 可使用声音阈值的大小进行判断录音，也可以固定时长进行录音。
def record_audio():
    t=0
    sum=0
    save_count=0
    save_buffer=[]
    time_flag=0
    flag_num=0
    CHUNK=1024#内部缓存块的大小
    FORMAT=pyaudio.paInt16
    CHANNELS=1
    RATE=16000#取样频率
    LEVEL=1000#保存声音的阈值
    COUNT_NUM=20#
    SAVE_LENGTH=8#声音的最小记录长度

    p=pyaudio.PyAudio()
    stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    #保存音频
    wf=wave.open("myvoices.wav",'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    """
    #根据人声开始录音
    while True:
        string_audio_data=stream.read(CHUNK)
        audio_data=np.fromstring(string_audio_data,dtype=np.short)
        large_sample_count=np.sum(audio_data>LEVEL)
        #print(large_sample_count)
        temp=np.max(audio_data)
        #print("temp:",temp)
        
        if temp>1500 and t==0:
            t=1
            print("检测到声音，开始录音，计时5秒")
            begin=time.time()
        if t==1:
            if np.max(audio_data)<1000:
                sum+=1
                print(sum)
            end=time.time()
            if end-begin>5:
                time_flag=1
            if large_sample_count>COUNT_NUM:
                save_count=SAVE_LENGTH
            else:
                save_count-=1
            
            if save_count<0:
                save_count=0

            if save_count>0:
                save_buffer.append(string_audio_data)
            else:
                if len(save_buffer)>0 or time_flag:

                    wf.writeframes(''.encode().join(save_buffer))
                    print("Done")  
                    wf.close()  
                    return 0
    """
                    
        
        
    print("please say something")
    for i in tqdm(range(0,int(RATE/CHUNK*4))):
        data=stream.read(CHUNK)
        wf.writeframes(data)
    
    print("Done")  
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()    

# 2、音频文件转文字：采用百度的语音识别python-SDK
# 导入我们需要的模块名，然后将音频文件发送给出去，返回文字。
# 百度语音识别API配置参数
APP_ID = '22967625'
API_KEY = 'WkCMHynhEpiNDDtUZ2D8M2lK'
SECRET_KEY = 'Q0QQGM2gyBLDGtgsyUjkOjAtyriHCBSY'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
path = 'myvoices.wav'
 
 
# 将语音转文本STT
def listen():
    # 读取录音文件
    with open(path, 'rb') as fp:
        voices = fp.read()
    try:
        # 参数dev_pid：1536普通话(支持简单的英文识别)、1537普通话(纯中文识别)、1737英语、1637粤语、1837四川话、1936普通话远场
        result = client.asr(voices, 'wav', 16000, {'dev_pid': 1537, })
        # result = CLIENT.asr(get_file_content(path), 'wav', 16000, {'lan': 'zh', })
        print(result)
        # print(result['result'][0])
        # print(result)
        result_text = result["result"][0]
        print("you said: " + result_text)
        return result_text
    except KeyError:
        print("KeyError")
        speaker.Speak("我没有听清楚，请再说一遍...")
 
 
# 3、与机器人对话：调用的是图灵机器人
# 图灵机器人的API_KEY、API_URL
turing_api_key = "c6af0c42888e42d88db279f44e13e3bd"
api_url = "http://openapi.tuling123.com/openapi/api/v2"  # 图灵机器人api网址
headers = {'Content-Type': 'application/json;charset=UTF-8'}
 
 
# 图灵机器人回复
def Turing(text_words=""):
    req = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": text_words
            },
 
            "selfInfo": {
                "location": {
                    "city": "深圳",
                    "province": "广东",
                    "street": "龙华"
                }
            }
        },
        "userInfo": {
            "apiKey": turing_api_key,  # 你的图灵机器人apiKey
            "userId": "Nieson"  # 用户唯一标识(随便填, 非密钥)
        }
    }
 
    req["perception"]["inputText"]["text"] = text_words
    response = requests.request("post", api_url, json=req, headers=headers)
    response_dict = json.loads(response.text)
    print(response_dict)
 
    result = response_dict["results"][0]["values"]["text"]
    print("AI Robot said: " + result)
    return result
 

# 使用pyttsx3 进行语音播放，
def Speak2(string):
    engine=pyttsx3.init()
    rate=engine.getProperty('rate')
    engine.setProperty('rate',rate-50)
    voice=engine.getProperty('voices')
    engine.setProperty('voice',voice[0].id)
    engine.say(string)
    engine.runAndWait()
  
# 语音合成，输出机器人的回答
#while True:
    #my_record()
    #record_audio()
    #request = listen()
    #response = Turing(request)
    #speaker.Speak(response)
    #Speak2(response)
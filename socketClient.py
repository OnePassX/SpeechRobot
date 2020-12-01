import EdgeServer
import sys,os
import time
import json
import main
import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")

with open('config.json') as f:
    jsonData=json.load(f)

clientSocket=EdgeServer.SocketServer()

client=clientSocket.CreateTCPClient(jsonData["setting"]["ip"],jsonData["setting"]["port"])

if __name__=="__main__":
    while True:
        try:
            recv=client.recv(1024)
            if recv!=b'':
                result=recv.decode()
                print(result)
                if result=="3$":
                    #main.my_record()
                    main.record_audio()
                    request=main.listen()
                    client.send("text".encode())
                    time.sleep(1)
                    request_msg="request_"+request
                    print(request_msg)
                    client.send(request_msg.encode())
                    response=main.Turing(request)
                    response_msg="response_"+response
                    print(response_msg)
                    client.send(response_msg.encode())
                    speaker.Speak(response)
        except:
            print("error")
            client=clientSocket.CreateTCPClient(jsonData["setting"]["ip"],jsonData["setting"]["port"])
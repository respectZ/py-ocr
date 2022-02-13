import os
import base64
import threading
import requests
import json
import time
import threading
import keyboard
import pyscreenshot as PyScreenshot
from googletrans import Translator
from tkinter import *

from ctypes import windll, Structure, c_long, byref
import ctypes

hotkey = {
    "area": "f2",
    "translate": "f3"
}
url = "https://content-vision.googleapis.com/v1/images:annotate?alt=json&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM"
dataJSON = {
    "requests": [
        {
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ],
            "image": {
                "content": ""
            }
        }
    ]
}
pos = []
settings = {}
opened = 1

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}

def addPos():
    global pos
    global txt

    if len(pos) == 0:
        txt.set("Press F2 to capture 2nd area position")
        res = queryMousePosition()
        pos.append(res["x"])
        pos.append(res["y"])
    elif len(pos) == 2:
        txt.set("Area set! Press F3 to capture & translate.")
        res = queryMousePosition()
        pos.append(res["x"])
        pos.append(res["y"])
        print(pos)

def OCR():
    global pos
    global dataJSON
    global txt
    
    if len(pos) == 4:
        # grab screenshot
        ss = PyScreenshot.grab(bbox=pos)
        ss.save("./temp.png", format="PNG")

        # reopen as b64
        with open("./temp.png", "rb") as f:
            imgbytes = base64.b64encode(f.read())
        
        # set datajson
        dataJSON["requests"][0]["image"]["content"] = imgbytes.decode(encoding="utf-8")

        # post ocr google
        res = requests.post(url=url, json=dataJSON, headers=header)

        # get
        text = res.json()["responses"][0]["fullTextAnnotation"]["text"].replace("\n", "")
        
        # whitelist
        if os.path.isfile("./whitelist.json"):
            with open("./whitelist.json", "r", encoding="utf-8") as f:
                for i in json.load(f)["whitelist"]:
                    text.replace(i["name"], i["translate"])

        # translate
        translator = Translator()
        tr = translator.translate(text)

        # wrap text
        tr.text = wrapText(tr.text, 50)

        # update
        txt.set(tr.text)

def on_close():
    global opened

    opened = 0
    App.destroy()
    exit()

def customLoop():
    global opened

    while 1:
        try:
            Label1.configure(font=("Arial", FontSize.get()))
            settings["fontsize"] = FontSize.get()
        except:
            pass

        saveConfig()
        
        time.sleep(0.1)

        if not(opened):
            break

def saveConfig():
    if os.path.isfile("./settings.json"):
        with open("./settings.json", "w") as f:
            json.dump(settings, f, indent=4)

def loadConfig():
    global settings

    if os.path.isfile("./settings.json"):
        with open("./settings.json", "r") as f:
            settings = json.load(f)

def wrapText(string, threshold):
    splitted = []
    spaces = []
    while string:
        flag = 0
        for i in range(len(string)):
            if string[i] == " ":
                spaces.append(i)

            if i+1 >= threshold:
                splitted.append(string[0:spaces[-1]])
                string = string[spaces[-1]+1:]
                flag = 1
                break
        if not(flag):
            splitted.append(string)
            string = ""
    return '\n'.join(splitted)

header = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98.0.1108.43\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-clientdetails": "appVersion=5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F98.0.4758.80%20Safari%2F537.36&platform=Win32&userAgent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F98.0.4758.80%20Safari%2F537.36",
    "x-goog-encode-response-if-executable": "base64",
    "x-javascript-user-agent": "apix/3.0.0 google-api-javascript-client/1.1.0",
    "x-origin": "https://explorer.apis.google.com",
    "x-referer": "https://explorer.apis.google.com",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://content-vision.googleapis.com/static/proxy.html?usegapi=1&jsh=m%3B%2F_%2Fscs%2Fapps-static%2F_%2Fjs%2Fk%3Doz.gapi.en.TenOR_lLL28.O%2Fam%3DAQ%2Fd%3D1%2Frs%3DAGLTcCMCcuroc7gdKSyRrVMzYC23sHf_SA%2Fm%3D__features__",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

if __name__ == "__main__":
    loadConfig()
    # dpi scaling windows fix for screenshot
    awareness = ctypes.c_int()
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    App = Tk(className="py-ocr")
    App['background'] = "#ffffff"
    App.attributes('-topmost', True)

    txt = StringVar()
    txt.set("Press F2 to capture 1st area position")
    FontSize = IntVar()
    FontSize.set(settings["fontsize"])

    FontSizeLabel = Label(App, text="Font Size: ", anchor="n", justify="left")
    # FontSizeLabel.grid(row=0, column=0, sticky=W, pady=2)
    FontSizeLabel.pack(side='left')

    FontSizeEntry = Entry(App, bd=5, textvariable=FontSize, justify="left")
    # FontSizeEntry.grid(row=0, column=1, sticky=W, pady=2)
    FontSizeEntry.pack(side='left')

    Label1 = Label(App, textvariable=txt, anchor="n", font=("Arial", FontSize.get()), justify="left")
    # Label1.grid(row=1, column=0, sticky=W, pady=2)
    Label1.pack()


    keyboard.add_hotkey(hotkey["area"], addPos)
    keyboard.add_hotkey(hotkey["translate"], OCR)

    t1 = threading.Thread(target=customLoop)
    t1.daemon = True
    t1.start()

    App.protocol("WM_DELETE_WINDOW", on_close)

    App.mainloop()
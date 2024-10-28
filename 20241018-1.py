import os
import cv2
import dlib
import time
import pickle
import serial
import threading
import numpy as np
import tkinter as tk
import simpleaudio as sa
import _modules_play_sound as mps

from tkinter import Label, Frame
from PIL import Image, ImageTk
from time import strftime

# global variables
python_state = 0             # 紀錄程式的bt_song state machine，只關SW，FW不動時，再開SW這個值要設1
python_car_state = 0         # 紀錄程式的bt_car state machine
support_rf_id = 1            # 支援RF-ID功能，未支援時設0
support_song_bt = 1          # 支援Song BT傳輸，未支援時設0
support_car_bt = 1           # 支援Car BT傳輸，未支援時設0
bt_connect_time = 5          # 設定BT初始化所需時間
cnt_frame_times = 8          # 計算每次人臉辧識的間隔時間，10=間隔1秒，20=間隔2秒，預設=40。
cnt_play_song_times = 6      # 計算每次播放笑話的時間，由cnt_frame_times來計數
cnt_play_car_times = 12      # 計算每次車子行走的時間，由cnt_frame_times來計數
class_num = [1, 2, 3, 1, 2,  # 依學號順序設置教室號碼
             3, 1, 1, 1, 2,
             2, 2, 1, 2, 3,
             2, 1, 3, 1, 3,
             2, 3, 3, 3, 1,
             3, 3, 1, 2, 3]

# 載入已保存的學員臉部特徵和名字
pickle_file1 = 'staff_descriptors.pickle'
pickle_file2 = 'staff_candidate.pickle'

with open(pickle_file1, 'rb') as f1:
    descriptors = pickle.load(f1)  # 載入學員基準特徵矩陣 (numpy 陣列)

with open(pickle_file2, 'rb') as f2:
    candidate = pickle.load(f2)  # 載入學員姓名列表

# 載入 dlib 的人臉檢測和特徵提取模型
predictor_path = "shape_predictor_68_face_landmarks.dat"
recogmodel_path = "dlib_face_recognition_resnet_model_v1.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(recogmodel_path)

# 創建主視窗
root = tk.Tk()
root.title("新竹職訓中心 -- 考生帶位服務系統")
root.resizable(False, False)  # 禁止調整視窗大小
root.attributes('-toolwindow', True)  # 隱藏放大、縮小按鈕，但保留關閉按鈕
# 設置視窗大小與位置
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 820
window_height = 500
position_right = int(screen_width / 2 - window_width / 2)
position_down = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

# 設置 root 的 grid 權重
root.grid_rowconfigure(0, weight=1)  # 第一行 (row 0)
root.grid_columnconfigure(0, weight=1)  # 第一列 (left_frame)
root.grid_columnconfigure(1, minsize=160)  # 第二列 (right_frame)

# 左側Frame (用來放攝像頭影像)，邊框設定
left_frame = Frame(root)
left_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

# 右側Frame (用來放其他label)，邊框設定
right_frame = Frame(root)
right_frame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

# 創建一個Label來顯示攝像頭影像 (放在左側的Frame內)
camera_label = Label(left_frame)
camera_label.pack(expand=True)

# 姓名
desc_label1 = Label(right_frame, text="姓名")
desc_label1.pack(pady=5)
name_label = Label(right_frame, text="")
name_label.pack(pady=0)

# 教室
desc_label2 = Label(right_frame, text="教室")
desc_label2.pack(pady=5)
class_label = Label(right_frame, text="")
class_label.pack(pady=0)

# 特徵值
desc_label3 = Label(right_frame, text="特徵值")
desc_label3.pack(pady=5)
eigen_label = Label(right_frame)
eigen_label.pack(pady=0)

# UI隔間用，無意義
desc_label4 = Label(right_frame, text="")
desc_label4.pack(pady=70)

# 時間
desc_label5 = Label(right_frame, text="時間")
desc_label5.pack(pady=5)
time_label = Label(right_frame)
time_label.pack(pady=0)

# UI variables
root_color = '#F7F7F7'
left_frame_color = '#FFDFBA'
right_frame_color = '#FFFFBA'
label_color_1 = '#BAFFC9'
label_color_2 = '#BAE1FF'
label_fg_color_1 = '#3B5998'
label_fg_color_2 = '#FB2E01'
label_fg_color_3 = '#555555'
font_type_1 = 'Arial'
font_size = 15
label_width = 10

# 設定背景顏色
root.configure(bg=root_color)
left_frame.configure(bd=2, relief="groove", bg=left_frame_color)
right_frame.configure(bd=2, relief="groove", bg=right_frame_color)

# 設置標籤前景顏色
desc_label1.config(bg=right_frame_color, font=(font_type_1, font_size), fg=label_fg_color_3)
desc_label2.config(bg=right_frame_color, font=(font_type_1, font_size), fg=label_fg_color_3)
desc_label3.config(bg=right_frame_color, font=(font_type_1, font_size), fg=label_fg_color_3)
desc_label4.config(bg=right_frame_color, font=(font_type_1, font_size), fg=label_fg_color_3)
desc_label5.config(bg=right_frame_color, font=(font_type_1, font_size), fg=label_fg_color_3)

# 修改 right_frame 內 Label 顏色
name_label.config(bg=label_color_1, font=(font_type_1, font_size), fg=label_fg_color_1, width=label_width)
name_label.config(borderwidth=1, relief="solid", padx=5, pady=5)
class_label.config(bg=label_color_1, font=(font_type_1, font_size), fg=label_fg_color_1, width=label_width)
class_label.config(borderwidth=1, relief="solid", padx=5, pady=5)
eigen_label.config(bg=label_color_1, font=(font_type_1, font_size), fg=label_fg_color_1, width=label_width)
eigen_label.config(borderwidth=1, relief="solid", padx=5, pady=5)
time_label.config(bg=label_color_2, font=(font_type_1, font_size), fg=label_fg_color_2, width=label_width)
time_label.config(borderwidth=1, relief="solid", padx=5, pady=5)

# Support RF-ID
if support_rf_id == 1:
    serial_port = 'COM4'                        # 根據不同PC，需修改串口名稱
    baud_rate = 9600
    timeout = 1
    rfid_receive_data = 'NULL'                  # 記錄RFID Arduino傳來的資料
    ser = serial.Serial(serial_port, baud_rate, timeout=timeout)  # 初始化串口


# Support BT
if support_song_bt == 1:
    bt_port = 'COM10'                           # 根據不同PC，需修改串口名稱
    bt_baud_rate = 9600
    bt_receive_data = 'NULL'                    # 記錄Arduino BT傳來的資料
    bt_serial = serial.Serial(bt_port, bt_baud_rate)  # 初始化串口
    time.sleep(bt_connect_time)                 # 等待連接建立

# Support Car BT
if support_car_bt == 1:
    bt_car_port = 'COM9'                        # 根據不同PC，需修改串口名稱
    bt_car_baud_rate = 9600
    bt_car_receive_data = 'NULL'                # 記錄Car BT傳來的資料
    bt_car_serial = serial.Serial(bt_car_port, bt_car_baud_rate)  # 初始化串口
    time.sleep(bt_connect_time)                 # 等待連接建立


# 接收RF-ID資料 (在獨立的執行緒中運行)
def receive_data():
    if support_rf_id == 1:
        global rfid_receive_data
        while True:
            if ser.in_waiting > 0:                                          # 檢查是否有資料要接收
                rfid_receive_data = ser.readline().decode('utf-8').strip()  # 讀取來自串口的資料
                if (rfid_receive_data != "RFID reader is ready!"):
                    name_label.config(text=rfid_receive_data)
                    class_label.config(text='')
                    eigen_label.config(text='')
                    mps.play_greeting(rfid_receive_data)                    # 隨機播放同學們給諸位老師的問候語
                rfid_receive_data = ''


# 接收BT資料 (在獨立的執行緒中運行)
def receive_song_bt_data():
    if support_song_bt == 1:
        global bt_receive_data
        global python_state
        while True:
            if bt_serial.in_waiting > 0:  # 檢查是否有資料可讀取
                bt_receive_data = bt_serial.readline().decode('utf-8').strip()
                print(bt_receive_data)
                python_state = mps.deal_with_bt_string(python_state, bt_receive_data)
                bt_receive_data = ''


def receive_car_bt_data():
    if support_car_bt == 1:
        global bt_car_receive_data
        global python_car_state
        while True:
            if bt_car_serial.in_waiting > 0:  # 檢查是否有資料可讀取
                bt_car_receive_data = bt_car_serial.readline().decode('utf-8').strip()
                print(bt_car_receive_data)
                python_car_state = mps.deal_with_bt_car_string(python_car_state, bt_car_receive_data)
                bt_car_receive_data = ''


# 啟動接收資料的執行緒
def start_receiving():
    if support_rf_id == 1:
        receive_thread = threading.Thread(target=receive_data)
        receive_thread.daemon = True  # 設置為守護執行緒，主程式退出時自動結束
        receive_thread.start()

    if support_song_bt == 1:
        receive_bt_thread = threading.Thread(target=receive_song_bt_data)
        receive_bt_thread.daemon = True  # 設置為守護執行緒，主程式退出時自動結束
        receive_bt_thread.start()

    if support_car_bt == 1:
        receive_bt_car_thread = threading.Thread(target=receive_car_bt_data)
        receive_bt_car_thread.daemon = True  # 設置為守護執行緒，主程式退出時自動結束
        receive_bt_car_thread.start()


def compare_face(image_path):
    global python_state
    global python_car_state
    dest_index = 0                          # 初始化Car目的地
    wave_name = ''                          # 初始化聲音檔名
    img = dlib.load_rgb_image(image_path)   # 加載拍攝的圖像
    faces = detector(img, 1)                # 使用 dlib 偵測臉部

    if len(faces) == 0:
        print("未檢測到任何臉部")
        name_label.config(text='')
        class_label.config(text='')
        eigen_label.config(text='')
        return

    # 提取第一個臉的特徵
    for face in faces:
        shape = predictor(img, face)
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        face_descriptor_np = np.array(face_descriptor)

        # 與學員資料中的特徵進行比對
        distances = np.linalg.norm(descriptors - face_descriptor_np, axis=1)
        min_distance = np.min(distances)
        min_index = np.argmin(distances)

        # 設定一個閾值，當距離小於閾值時認為是相似臉(閾值範圍0.4~0.6，愈小愈準)。
        threshold = 0.43

        # 當RF-ID動作且有收到字串時，人臉辦識功能需跳掉
        if support_rf_id == 1:
            global rfid_receive_data
            if rfid_receive_data != '':
                name_label.config(text=rfid_receive_data)
                class_label.config(text='')
                eigen_label.config(text='')
                break

        if min_distance < threshold:
            print(f"識別成功 : {candidate[min_index]} {round(min_distance, 4)}")
            name_label.config(text=candidate[min_index])
            class_label.config(text=class_num[min_index])
            eigen_label.config(text=round(min_distance, 3))
            dest_index = class_num[min_index]
            wave_name = ".\\wav\\" + str(candidate[min_index]) + ".wav"
            break
        else:
            name_label.config(text="非本職訓學員")
            class_label.config(text="請洽櫃臺")
            eigen_label.config(text=round(min_distance, 3))
            dest_index = 4
            wave_name = ".\\wav\\非本職訓學員.wav"

    # 更新 GUI 使改變立即顯示
    name_label.update_idletasks()
    class_label.update_idletasks()
    eigen_label.update_idletasks()

    # 播放提示聲音
    if os.path.isfile(wave_name):
        wave_obj = sa.WaveObject.from_wave_file(wave_name)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        time.sleep(1)

        if support_song_bt == 1 and python_state == 1:
            bt_serial.write(mps.get_bt_song_cmd(python_state).encode())
            python_state = 2

        if support_car_bt == 1 and python_car_state == 0:
            bt_car_serial.write(mps.get_bt_car_cmd(5).encode())
            bt_car_serial.write(mps.get_bt_car_cmd(dest_index).encode())
            python_car_state = 1
    else:
        print(f"檔案 {wave_name} 不存在，無法播放音頻。")


# 更新時間的函數
def update_time():
    current_time = strftime('%H:%M:%S')  # 格式化時間為 "時:分:秒"
    time_label.config(text=current_time)  # 更新 Label 文字
    time_label.after(1000, update_time)  # 每隔 1 秒(1000 毫秒)更新一次


# 開啟攝像頭
cap = cv2.VideoCapture(0)


def update_frame():
    global cnt_frame_times
    global cnt_play_song_times
    global cnt_play_car_times
    global python_state
    global python_car_state
    enable_recog = 0
    cnt_frame_times += 1
    ret, frame = cap.read()

    if ret:
        frame = cv2.flip(frame, 1)             # 鏡頭左右反轉，使畫面和人物移動方向一致
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # 將 frame 從 OpenCV 的 BGR 轉換為 RGB
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.config(image=imgtk)

    # 每 5 秒自動辦識一次
    if cnt_frame_times == 50:
        cnt_frame_times = 0
        enable_recog = 1

        if support_song_bt == 1:
            if python_state == 2:
                cnt_play_song_times -= 1
                name_label.config(text="帶位中...")
                class_label.config(text="")
                eigen_label.config(text="")
                # 強制帶位完畢，恢復人臉辦識
                if cnt_play_song_times == 0:
                    cnt_play_song_times = 6
                    python_state = 1
                else:
                    enable_recog = 0
            elif python_state == 0:
                name_label.config(text="")
                class_label.config(text="")
                eigen_label.config(text="")

        if support_car_bt == 1:
            if python_car_state == 1:
                cnt_play_car_times -= 1
                name_label.config(text="帶位中...")
                class_label.config(text="")
                eigen_label.config(text="")
                # 強制帶位完畢，恢復人臉辦識
                if cnt_play_car_times == 0:
                    cnt_play_car_times = 15
                    python_car_state = 0
                else:
                    enable_recog = 0
            else:
                name_label.config(text="")
                class_label.config(text="")
                eigen_label.config(text="")

        # 開始人臉辦識
        if enable_recog == 1:
            cv2.imwrite("captured_image.jpg", frame)
            compare_face("captured_image.jpg")
    # 每 2 秒傳訊息給BT
    elif support_song_bt == 1 and python_state == 0 and cnt_frame_times == 20:
        bt_serial.write(mps.get_bt_song_cmd(python_state).encode())
    # 每100毫秒更新一次影像
    root.after(100, update_frame)


# 啟動接收UART功能
start_receiving()

# 啟動時間更新
update_time()

# 開始更新攝像頭畫面
update_frame()

# 開始 Tkinter 主循環
root.mainloop()

# 釋放攝像頭
cap.release()

import random
import win32com.client as wincl

# global variables
pre_selected_idx = 0        # 前一次選中的問候語
pre_selected_song = 0       # 前一次選中的歌曲(笑話)
mp3_num = 0                 # mp3語音檔總數
car_dest_str = ""           # 小車目地字串

# 鄔執行長問候語
greeting_wu = [ '祝您早上精神好',
                '您愈來愈漂亮啦',
                '同學來喝咖啡今天有煮咖啡',
                '美女早安見你又是心情開朗的一天',
                '愛犬JOJO又帥又聰明養的好',
                '我煮咖啡給大家喝',
                '狗狗很乖不會咬人',
                '各位同學早安',
                '這裡有一隻聰明的狗狗',
                '今天是美好的一天來一杯咖啡吧',
                '同學大家早上好',
                '狗狗很可愛',
                '咖啡煮好囉',
                '狗狗來打招呼了哦',
                '早安',
                '午安',
                '大家早上好',
                '外面有咖啡可以自行取用',
                '大家到外面喝杯咖啡',
                '我相信各位同學都是很有創意',
                '咖啡已經煮好了記得去拿唷',
                '祝您有個美好的一天',
                '大家早安',
                '認真的女人最美麗',
                '感恩下午茶吃飽喝飽讚',
                '同學們好',
                '喝咖啡囉',
                '積極推動各項職業訓練計畫',
                '開發符合市場需求的高品質課程',
                '熱騰騰的咖啡出爐囉',
                '今天的您也依舊美麗',
              ]

# 蘇有老師問候語
greeting_su = [ '今天有新八卦嗎',
                '黃金又漲啦',
                '同學懂不懂',
                '講清楚說明白',
                '有哥無嘴天尊唱聖歌啦',
                '主唱練團啦來個K哥之王揪團啦',
                '沒有老師會這樣教的真的',
                '又到換氣的時間了',
                '做好筆記帶好小抄',
                '買買買黄金買起來',
                '買黄金放長期穩的啦',
                '該買黃金了吧',
                '恩很棒',
                '老師你教的很簡單但我還是跟的很吃力',
                '老師說正則表達式不是那麼簡單',
                '記得基地一班全部同學love you啾咪',
                '時間不多了同學要好好學',
                '股票不要買',
                '太棒了',
                '好好聽課老師保證你會考到的',
                '來信無嘴天尊教吧',
                '白銀也漲了',
                '來信我的教吧',
                '相信老師買黃金就對了',
                '小抄帶了嗎',
                '跟老師學保證讓你考到',
                '有一天會想起好像有位姓蘇的老師說過',
                '沒有老師會這樣講的真的',
                '天吶太多要教的了',
                '當你看到有人把圖做得很美你就要把圖做成他那個樣子',
                '老師這個我不會有沒有更簡單的方法',
                '今天早餐吃摩斯嗎',
                '莫忘自駕雲遊四海美景或美女呦',
                '能執行就是好程式',
                '哎呀太棒了',
                '您又胖了',
                '教的PYTHON還回去了',
                '深耕多元職訓教育',
                '培養企業所需的專業專才',
                '記得吃早餐呀',
                '午餐又是麥當勞嗎',
              ]

# 曾裕民老師問候語
greeting_tzeng = [  '早餐吃飽了沒',
                    'Arduino好好玩',
                    '程式我會給大家',
                    '這一題我很快講一下',
                    '務實認真教學老師好',
                    '不同語言融會貫通找粽子頭',
                    'Arduino沒什麼就這樣',
                    '我們自己寫不用參考的範例',
                    '我們自己來就好',
                    'Arduino很棒',
                    '早上好',
                    'C++的語法就這樣',
                    'inventor2很簡單',
                    '是史上無敵大帥哥你好帥',
                    '同學們可以自己玩一玩',
                    '為什麼WiFi模組這麼差',
                    '同學們可以自己玩一玩',
                    '同學起床洗把臉',
                    '今天講笑話了嗎',
                    '這很簡單你們都會了吧',
                    '這個不好用跟我來',
                    'Arduino就這樣',
                    '來試試看親手做做看比較有感覺',
                    '我是建議不要寫成這樣子',
                    '這兩種語法都行啦',
                    '時不時的冷笑話很用心',
                    '三種語言一次滿足',
                    'Arduino真是軟硬兼施的東西',
                    '手腦並用',
                    '提升民眾技能水準及競爭力',
                    '擴大就業和轉業的機會',
                    '要接3.3伏特別接錯了',
                    '我電阻接錯LED燒壞拉',
                 ]

# 林勁均老師問候語
greeting_lin = [ '手機還在嗎',
                 '中午素食要吃啥',
                 '哈囉同學',
                 '同學給點反應',
                 '中二魂合體魔貫光殺砲發射',
                 '林老師笑一個開啟今天行程',
                 '哈囉同學給個回應',
                 '可以去洗手間清醒一下',
                 '我很中二嗎',
                 '怎麼都沒聲音呢',
                 '同學們早上好',
                 '等一下開會喔',
                 '同學看我這邊',
                 '同學可以嗎',
                 '對不起我又中二了',
                 '早上好',
                 '各位同學大家早',
                 '認真負責分享教學也不忘對同學內心建設強化',
                 '中二太帥了',
                 '可以去洗手間清醒一下',
                 '實現教學與就業無縫接軌',
                 '大家好安靜起來火影跑伸展一下',
                 '各位同學有睡好嗎',
                 '同學們仔細看這一步很重要',
                 '魔貫光殺砲',
                 '早安午安',
                 '建立學以致用的學習環境',
                 '就是要夠中二才快樂',
               ]

# 產生問候字串供語音模組使用
def generate_greeting_str(input_name):
    global pre_selected_idx
    greeting_str = ''
    array_len = 0

    if input_name == '鄔執行長':
        array_len = len(greeting_wu)
    elif input_name == '蘇有老師':
        array_len = len(greeting_su)
    elif input_name == '曾裕民老師':
        array_len = len(greeting_tzeng)
    elif input_name == '林勁均老師':
        array_len = len(greeting_lin)

    gen_num = random.randint(0, array_len-1)

    # 避免重複的問候語
    while gen_num == pre_selected_idx:
        gen_num = random.randint(0, array_len-1)
        break

    pre_selected_idx = gen_num

    if input_name == '鄔執行長':
        greeting_str = greeting_wu[gen_num]
    elif input_name == '蘇有老師':
        greeting_str = greeting_su[gen_num]
    elif input_name == '曾裕民老師':
        greeting_str = greeting_tzeng[gen_num]
    elif input_name == '林勁均老師':
        greeting_str = greeting_lin[gen_num]

    return greeting_str


def play_greeting(input_name):
    if input_name != '':
        speak = wincl.Dispatch("SAPI.SpVoice")
        if (input_name == '鄔執行長' or
            input_name == '蘇有老師' or
            input_name == '曾裕民老師' or
            input_name == '林勁均老師'):
            speak.Speak(input_name)
            speak.Speak(generate_greeting_str(input_name))
        else:
            speak.Speak("非本職訓人員")
            speak.Speak("請洽櫃枱服務")
            speak.Speak("謝謝")


def deal_with_bt_string(python_state, input_string):
    global mp3_num
    if python_state == 0:
        mp3_num = input_string.lstrip("SONG_CNT=").strip()
        if mp3_num.isdigit():
            print(f"MP3 語音檔總數 {mp3_num}")
            mp3_num = int(mp3_num)
        else:
            print(f"MP3 語音檔總數出現錯誤")
        python_state = 1
    elif python_state == 2 and input_string == "SONG_DONE":
        print(input_string)
        python_state = 1

    return python_state

# 依python state傳命令給BT，BT回應後，在收BT string後，更新python state及取得所需資料
def get_bt_song_cmd(python_state):
    global mp3_num
    global pre_selected_song
    bt_string = ""
    num = 0
    if python_state == 0:
        bt_string = "SONG_CNT\n"
    elif python_state == 1:
        num = random.randint(1, mp3_num - 1)

        # 避免重複的問候語
        while num == pre_selected_song:
            num = random.randint(1, mp3_num - 1)
            break

        pre_selected_song = num
        bt_string = f"SONG_IDX={num}\n"

    return bt_string


def deal_with_bt_car_string(python_car_state, input_string):
    global car_dest_str
    if python_car_state == 1:
        if car_dest_str == "A" and input_string == "aA":
            python_car_state = 0
        elif car_dest_str == "B" and input_string == "bB":
            python_car_state = 0
        elif car_dest_str == "C" and input_string == "cC":
            python_car_state = 0
        elif car_dest_str == "D" and input_string == "dD":
            python_car_state = 0

    return python_car_state


def get_bt_car_cmd(dest_index):
    global car_dest_str
    if dest_index == 1:
        car_dest_str = "A"
    elif dest_index == 2:
        car_dest_str = "B"
    elif dest_index == 3:
        car_dest_str = "C"
    elif dest_index == 4:
        car_dest_str = "D"
    elif dest_index == 5:
        car_dest_str = "Z"

    return car_dest_str



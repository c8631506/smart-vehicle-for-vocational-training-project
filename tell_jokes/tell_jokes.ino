#include "Arduino.h"
#include "DFRobotDFPlayerMini.h"
#include <AltSoftSerial.h>
#include <SoftwareSerial.h>   

// define software serial port number
#define MP3_RX  2
#define MP3_TX  3

#define TIMER_1ST 8000                // 8秒
#define TIMER_2ND 15000               // 12秒
#define TIMER_3RD 15000               // 12秒

AltSoftSerial  BT;                    // RX=8, TX=9
SoftwareSerial MP3(MP3_RX, MP3_TX);   // 接MP3-PLAYER的TX, 接MP3-PLAYER的RX
DFRobotDFPlayerMini DFPlayer;         // 播放MP3

unsigned long previousMillis = 0;     // 程式計時器1
unsigned long currentMillis = 0;      // 程式計時器2
unsigned char prog_state = 0;         // 程式狀態
int    song_file_cnt = 0;             // 紀錄SD卡歌曲數量
int    song_index = 0;                // 紀錄SD播放歌曲的位址
String bt_receive_str = "";           // 接收BT的完整字串 
String bt_str_received = "";          // 實際儲存BT的完整字串 
String bt_send_str = "";              // 傳送NB的字串                      

void receive_bt_string(void);
void check_command_string(void);
void check_current_state(void); 
void print_detail(uint8_t, int);

void setup() 
{
  Serial.begin(9600);             // 與電腦序列埠連線  
  BT.begin(9600);                 // 設定藍牙模組的連線速率
  MP3.begin(9600);                // 設定MP3模組的連線速率

  // 透過sw serial和MP3模組溝通
  if (!DFPlayer.begin(MP3, /*isACK = */true, /*doReset = */true)) 
  {     
    Serial.println(F("1.請檢查連線 !"));
    Serial.println(F("2.請檢查SD卡 !"));
    while(true);
  }

  DFPlayer.setTimeOut(500);                           // Set serial communictaion time out 500ms
  DFPlayer.volume(29);                                 // Set volume value (0~30).
  DFPlayer.volumeUp();                                // Volume Up
  DFPlayer.volumeDown();                              // Volume Down
  DFPlayer.EQ(DFPLAYER_EQ_NORMAL);                    // Set EQ
  DFPlayer.outputDevice(DFPLAYER_DEVICE_SD);          // Set play SD Card
  
  Serial.println("BT is ready");
    
  Serial.println(DFPlayer.readState());               // read mp3 state                                   (-1)
  Serial.println(DFPlayer.readVolume());              // read current volume                              (512)
  Serial.println(DFPlayer.readEQ());                  // read EQ setting                                  (29)   
  Serial.println(DFPlayer.readFileCounts());          // read all file counts in SD card                  (0)
  song_file_cnt = DFPlayer.readCurrentFileNumber();   
  Serial.println(song_file_cnt, DEC);                 // read current play file number                    (33)
  Serial.println(DFPlayer.readFileCountsInFolder(3)); // read file counts in folder SD:/03                (1)

  DFPlayer.reset();
}

void loop() 
{  
  currentMillis = millis();

  receive_bt_string(); 

  // initial後，等python指令，傳送MP3歌曲總數給python
  if (prog_state == 0 && bt_str_received == "SONG_CNT")
  { 
    bt_send_str = "SONG_CNT=" + String(song_file_cnt);    
    Serial.println(bt_send_str);
    BT.println(bt_send_str); 
    
    previousMillis = currentMillis;    
    prog_state = 1;
    bt_send_str = "";
  }
  // 開始播放帶位語音5秒
  else if (prog_state == 1 && bt_str_received.startsWith("SONG_IDX="))
  { 
    int pos = bt_str_received.indexOf('=');
    String num_str = bt_str_received.substring(pos + 1);  
    song_index = num_str.toInt();
    
    DFPlayer.play(1);

    previousMillis = currentMillis;     
    prog_state = 2;
  } 
  // 播放第一首笑話15秒
  else if (prog_state == 2 && (currentMillis - previousMillis) > TIMER_1ST)
  {     
    DFPlayer.play(song_index);

    previousMillis = currentMillis; 
    prog_state = 3;  
  }
  // 播放第二首笑話15秒
  else if (prog_state == 3 && (currentMillis - previousMillis) > TIMER_2ND)
  {     
    if ((song_index + 1) <= song_file_cnt)
    {    
      DFPlayer.play((song_index + 1));
    }
    else
    {
      int song_idx = random(2, song_file_cnt);
      DFPlayer.play(song_idx);      
    }

    previousMillis = currentMillis; 
    prog_state = 4;  
  }    
  // 等第二首播完
  else if (prog_state == 4 && (currentMillis - previousMillis) > TIMER_3RD)
  {
    bt_send_str = "SONG_DONE";
    Serial.println(bt_send_str);
    BT.println(bt_send_str);     
    
    previousMillis = currentMillis; 
    bt_str_received = "";
    bt_send_str = "";
    prog_state = 1;      
  }

  //Print the detail message from DFPlayer to handle different errors and states.
  if (DFPlayer.available()) {
    printDetail(DFPlayer.readType(), DFPlayer.read()); 
  }  
}

void printDetail(uint8_t type, int value){
  switch (type) {
    case TimeOut:
      Serial.println(F("Time Out!"));
      DFPlayer.reset();
      break;
    case WrongStack:
      Serial.println(F("Stack Wrong!"));
      DFPlayer.reset();
      break;
    case DFPlayerCardInserted:
      Serial.println(F("Card Inserted!"));
      break;
    case DFPlayerCardRemoved:
      Serial.println(F("Card Removed!"));
      break;
    case DFPlayerCardOnline:
      Serial.println(F("Card Online!"));
      break;
    case DFPlayerUSBInserted:
      Serial.println("USB Inserted!");
      break;
    case DFPlayerUSBRemoved:
      Serial.println("USB Removed!");
      break;
    case DFPlayerPlayFinished:
      Serial.print(F("Number:"));
      Serial.print(value);
      Serial.println(F(" Play Finished!"));
      break;
    case DFPlayerError:
      Serial.print(F("DFPlayerError:"));
      switch (value) {
        case Busy:
          Serial.println(F("Card not found"));
          break;
        case Sleeping:
          Serial.println(F("Sleeping"));
          break;
        case SerialWrongStack:
          Serial.println(F("Get Wrong Stack"));
          DFPlayer.reset();
          break;
        case CheckSumNotMatch:
          Serial.println(F("Check Sum Not Match"));
          break;
        case FileIndexOut:
          Serial.println(F("File Index Out of Bound"));
          DFPlayer.reset();
          break;
        case FileMismatch:
          Serial.println(F("Cannot Find File"));
          break;
        case Advertise:
          Serial.println(F("In Advertise"));
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }  
}



void receive_bt_string(void)
{  
  while (BT.available())                  // 若收到藍牙模組的資料，則送到「序列埠監控視窗」
  {
    char val = BT.read();                 // 讀取單個字元
    if (val == '\n')                      // 檢查是否接收到換行符（表示訊息結束）
    {      
      Serial.println(bt_receive_str);     // 顯示接收到的完整字串 
      bt_str_received = bt_receive_str;
      bt_receive_str = "";
    }
    else
    {
      bt_receive_str += val;              
    }
  }
}

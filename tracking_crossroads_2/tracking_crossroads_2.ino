/**
 * @file tracking_test.ino
 * @author Anonymity(Anonymity@hiwonder.com)
 * @brief 巡线
 * @version V1.0
 * @date 2024-04-23
 *
 * @copyright Copyright (c) 2023
 *
 */

#include "FastLED.h"
#include "Ultrasound.h"
#include <Wire.h>

// 超聲波
Ultrasound ultrasound;              ///< 实例化超声波类

#define FILTER_N               3    ///< 递推平均滤波法
#define CAR_DRIFT_OFF          0    // car drift控制
#define OBJ_DISTANCE           260
#define MOTOR_ACTIVE           250
#define INITIAL_TIME           10000
#define LINE_FOLLOWER_I2C_ADDR 0x78 /* 巡线传感器的iic地址 */

const static uint8_t ledPin = 2;
const static uint8_t keyPin = 3;
const static uint8_t pwm_min = 50;
const static uint8_t motorpwmPin[4] = { 10, 9, 6, 11 };
const static uint8_t motordirectionPin[4] = { 12, 8, 7, 13 };
const static uint8_t TRACKING = 4;
const static uint8_t INTERSECTION_DETECTION = 5;

static uint8_t count_need = 0;
uint8_t nowcount = 0;
unsigned long previousMillis = 0;
unsigned long currentMillis = 0;
static char cCmd = 'O';        // 'O': 回原點, 'D': 櫃檯, 'A'~'C':教室A~C

static CRGB rgbs[1];
static uint8_t modestate = TRACKING;

bool stoped = false; 
uint16_t g_distance = 0; 
uint8_t state = 0;
uint8_t data;
uint8_t rec_data[4];

bool keyState = false;        ///< 按键状态检测
bool taskStart = 0;

// Functions
bool WireWriteByte(uint8_t val);
bool WireReadDataByte(uint8_t reg, uint8_t &val);
uint16_t Ultrasonic_Distance(void);
int Filter(void);
void Motor_Init(void);
void Velocity_Controller(uint16_t angle, uint8_t velocity, int8_t rot, bool drift = CAR_DRIFT_OFF);
void Motors_Set(int8_t Motor_0, int8_t Motor_1, int8_t Motor_2, int8_t Motor_3);
void Sensor_Receive(void);
void BT_Receive(void);
void Anti_Collision(void);
void Tracking_Line_Task(void);
void Task_Dispatcher(void);
void Rgb_Show(uint8_t rValue, uint8_t gValue, uint8_t bValue);

void setup()
{  
  // 使用D0 D1通訊
  Serial.begin(9600);
  Serial.println("BT is ready!");
  
  pinMode(keyPin, INPUT);
  FastLED.addLeds<WS2812, ledPin, GRB>(rgbs, 1);
  Rgb_Show(255, 255, 255);

  Wire.begin();   
  Motor_Init();
  delay(INITIAL_TIME);
}

void loop()
{
  // 按鈕啟動，啟動後就無法關閉
  keyState = analogRead(keyPin);
  if (!keyState || cCmd == 'Z'){ 
    taskStart = 1;
  }

  BT_Receive();
    
  if (taskStart && count_need > 0 && count_need <= 4)
  {     
    Sensor_Receive();
    Task_Dispatcher();
    //Anti_Collision();   
  } 
}

bool WireWriteByte(uint8_t val)
{
  Wire.beginTransmission(LINE_FOLLOWER_I2C_ADDR); /* 选择地址开始传输 */
  Wire.write(val);                                //发送数据
  if (Wire.endTransmission() != 0)
  {
    //Serial.println("false");  /* 发送失败 */
    return false;
  }
  
  //Serial.println("true");   /* 发送成功 */
  return true;
}

/* 讀取尋跡資訊 */
bool WireReadDataByte(uint8_t reg, uint8_t &val)
{
  if (!WireWriteByte(reg))                      /* 给传感器发送读/写信号 */
    return false;

  Wire.requestFrom(LINE_FOLLOWER_I2C_ADDR, 1);  /* 接收到传感器的应答信号 */
  while (Wire.available()){                     /* 开始读取数据 */
    val = Wire.read();    
  }

  return true;
}

/* 馬達初始化函式 */
void Motor_Init(void)
{
  for (uint8_t i = 0; i < 4; i++)
    pinMode(motordirectionPin[i], OUTPUT);

  Velocity_Controller(0, 0, 0);
}

/* 藍牙接收函式 */
void BT_Receive(void)
{
  if (Serial.available())
  { 
    switch (Serial.read())
    {
      case 'O': // 停止，重收
        Serial.println("O");
        count_need = 0;
        cCmd = 'O';
        modestate = 0;
        break;
      case 'D': // 櫃檯
        Serial.println("D");
        count_need = 1;
        cCmd = 'D';
        modestate = TRACKING;
        break;
      case 'A': // 教室A
        Serial.println("A");
        count_need = 2;
        cCmd = 'A';
        modestate = TRACKING;
        break;
      case 'B': // 教室B
        Serial.println("B");
        count_need = 3;
        cCmd = 'B';
        modestate = TRACKING;
        break;
      case 'C': // 教室C
        Serial.println("C");
        count_need = 4;
        cCmd = 'C';
        modestate = TRACKING;
        break;
      case 'Z': // initial
        Serial.println("Z");
        count_need = 0;
        cCmd = 'Z';
        modestate = 0;
        break;
      default:
        count_need = 0;
        cCmd = 'O';
        modestate = 0;
        break;
    }
  }  
}


/**
 * @brief 速度控制函数
 * @param angle     用于控制小车的运动方向，小车以车头为0度方向，逆时针为正方向。
 *                    取值为0~359
 * @param velocity  用于控制小车速度，取值为0~100。
 * @param rot       用于控制小车的自转速度，取值为-100~100，若大于0小车有一个逆
 *                    时针的自转速度，若小于0则有一个顺时针的自转速度。
 * @param drift     用于决定小车是否开启漂移功能，取值为0或1，若为0则开启，反之关闭。
 * @retval None
 */
void Velocity_Controller(uint16_t angle, uint8_t velocity, int8_t rot, bool drift)
{
  int8_t velocity_0, velocity_1, velocity_2, velocity_3;
  float speed = 1;
  
  angle += 90;
  float rad = angle * PI / 180;
  
  if (rot == 0) 
    speed = 1;                    ///< 速度因子
  else speed = 0.5;
  
  velocity /= sqrt(2);
  
  if (drift)
  {
    velocity_0 = (velocity * sin(rad) - velocity * cos(rad)) * speed;
    velocity_1 = (velocity * sin(rad) + velocity * cos(rad)) * speed;
    velocity_2 = (velocity * sin(rad) - velocity * cos(rad)) * speed - rot * speed * 2;
    velocity_3 = (velocity * sin(rad) + velocity * cos(rad)) * speed + rot * speed * 2;
  }
  else
  {
    velocity_0 = (velocity * sin(rad) - velocity * cos(rad)) * speed + rot * speed;
    velocity_1 = (velocity * sin(rad) + velocity * cos(rad)) * speed - rot * speed;
    velocity_2 = (velocity * sin(rad) - velocity * cos(rad)) * speed - rot * speed;
    velocity_3 = (velocity * sin(rad) + velocity * cos(rad)) * speed + rot * speed;
  }
  
  Motors_Set(velocity_0, velocity_1, velocity_2, velocity_3);
}

/**
 * @brief PWM与轮子转向设置函数
 * @param Motor_x   作为PWM与电机转向的控制数值。根据麦克纳姆轮的运动学分析求得。
 * @retval None
 */
void Motors_Set(int8_t Motor_0, int8_t Motor_1, int8_t Motor_2, int8_t Motor_3)
{
  int8_t pwm_set[4];
  int8_t motors[4] = { Motor_0, Motor_1, Motor_2, Motor_3 };
  bool direction[4] = { 1, 0, 0, 1 };  ///< 前进 左1 右0
  
  for (uint8_t i; i < 4; ++i)
  {
    if (motors[i] < 0) direction[i] = !direction[i];
    else direction[i] = direction[i];

    if (motors[i] == 0) pwm_set[i] = 0;
    else pwm_set[i] = map(abs(motors[i]), 0, 100, pwm_min, 255);

    digitalWrite(motordirectionPin[i], direction[i]);
    analogWrite(motorpwmPin[i], pwm_set[i]);
  }
}

/* 获取传感器数据 */
void Sensor_Receive(void)
{
  WireReadDataByte(1, data);
  rec_data[0] = data & 0x01;
  rec_data[1] = (data >> 1) & 0x01;
  rec_data[2] = (data >> 2) & 0x01;
  rec_data[3] = (data >> 3) & 0x01;
}

/* 測距防撞功能 */ 
void Anti_Collision(void)
{  
  stoped = false; 
  g_distance = Ultrasonic_Distance(); 
  while((g_distance < (uint16_t)OBJ_DISTANCE))
  {   
    stoped = true; 
    g_distance = Ultrasonic_Distance(); 
    Velocity_Controller(0, 0, 0);
  }
  
  // 微加速
  if (stoped)
    Velocity_Controller(0, 20, 0);  
    delay(100);
}

void Tracking_Line_Task(void)
{
  //Serial.println("Tracking...");    
  Rgb_Show(255, 0, 0);
  
  if (rec_data[1] == 1 && rec_data[2] == 1)
    Velocity_Controller(0, 50, 0);
  if (rec_data[1] == 1 && rec_data[2] == 0)
    Velocity_Controller(0, 50, 35);
  if (rec_data[1] == 0 && rec_data[2] == 1)
    Velocity_Controller(0, 50, -35);
  if (rec_data[1] == 0 && rec_data[2] == 0)
  {
    if (rec_data[0] == 1 && rec_data[3] == 0)
      Velocity_Controller(0, 50, 35);
    else if (rec_data[0] == 0 && rec_data[3] == 1)
      Velocity_Controller(0, 50, -35);
  }  
  
  // 0=沒辦識到黑線 1=辦識到黑線
  if (rec_data[1] == 1 && rec_data[2] == 1 && rec_data[0] == 1 && rec_data[3] == 1)  
  {
    modestate = INTERSECTION_DETECTION;
    nowcount++;
    Velocity_Controller(0, 10, 0);        
    delay(MOTOR_ACTIVE);
  } 
}

/* 到站執行函式 */
void OnSite() 
{
  Serial.println("DEST");
  
  for (int i = 0; i < 10; i++)
  {
    Rgb_Show(255,0,0);
    delay(200);
    Rgb_Show(0,255,0);
    delay(200);
    Rgb_Show(0,0,255);
    delay(200);
  }

  Rgb_Show(255,0,0);
}


/* 十字路口檢測 */
void Intersection_Detection_Task(void)
{  
  if (nowcount == count_need)
  {
    Velocity_Controller(0,0,0);
    OnSite();
    
    modestate = TRACKING;
    Velocity_Controller(0, 20, 0);
    delay(MOTOR_ACTIVE);
  }
  else if (nowcount == 5) // 回到原點
  {
    nowcount = 0;
    modestate = 0;    // modestate = TRACKING;
    
    char ch[3] = {'\0', '\0', '\0'};
    ch[1] = cCmd;
    ch[0] = cCmd + ('a' - 'A');
    Serial.println(ch); // 通知Python已可再下命令0

    Rgb_Show(0,0,255);
    Velocity_Controller(0, 0, 0);
  }
  else
  {
    modestate = TRACKING;
    Velocity_Controller(0, 20, 0);
    delay(MOTOR_ACTIVE);
  }
}

/* 任务调度 */
void Task_Dispatcher()
{
  switch (modestate)
  {
    case TRACKING:
      Tracking_Line_Task();
      break;
    case INTERSECTION_DETECTION:
			Intersection_Detection_Task();
			break;
  }
}

/**
 * @brief 设置RGB灯的颜色
 * @param  rValue; gValue; bValue;
 * @arg    三个入口参数取值分别为:0~255;
 * @retval None
 * @note (255,0,0)红色 (0,255,0)绿色 (0,0,255)蓝色 (255,255,255)白色
 */
void Rgb_Show(uint8_t rValue, uint8_t gValue, uint8_t bValue)
{
  rgbs[0].r = rValue;
  rgbs[0].g = gValue;
  rgbs[0].b = bValue;
  FastLED.show();
}

// 超聲波加的code
 /**
 * @brief 滤波
 * @param  filter_sum / FILTER_N
 * @arg    None
 * @retval None
 * @note None
 */
int Filter() 
{
  int i;
  int filter_sum = 0;
  int filter_buf[FILTER_N + 1];
  
  filter_buf[FILTER_N] = ultrasound.GetDistance();    ///< 读取超声波测值
  for(i = 0; i < FILTER_N; i++) 
  {
    filter_buf[i] = filter_buf[i + 1];                ///< 所有数据左移，低位仍掉
    filter_sum += filter_buf[i];
  }
  return (int)(filter_sum / FILTER_N);
}

 /**
 * @brief 超声波距离数据获取
 * @param None
 * @arg None
 * @retval distance
 * @note None
 */
uint16_t Ultrasonic_Distance()
{
  uint8_t s;
  uint16_t distance = Filter();                                               ///< 获得滤波器输出值
  
  if (distance > 0 && distance <= 80)
  {
    ultrasound.Breathing(1, 0, 0, 1, 0, 0);                                   ///< 呼吸灯模式，周期0.1s，颜色红色
  }   
  else if (distance > 80 && distance <= 180)
  {
    s = map(distance,80,180,0,255);
    ultrasound.Color((255-s), 0, 0, (255-s), 0, 0);                           ///< 红色渐变
  }   
  else if (distance > 180 && distance <= 320)
  {
    s = map(distance,180,320,0,255);
    ultrasound.Color(0, 0, s, 0, 0, s);                                       ///< 蓝色渐变
  }   
  else if (distance > 320 && distance <= 500)
  {
    s = map(distance,320,500,0,255);
    ultrasound.Color(0, s, 255-s, 0, s, 255-s);                               ///< 绿色渐变
  }
  else if (distance > 500)
  {
    ultrasound.Color(0, 255, 0, 0, 255, 0);                                   ///< 绿色
  }
  
  return distance;  
}

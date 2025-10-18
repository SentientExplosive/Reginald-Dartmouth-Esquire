#include <Adafruit_NeoPixel.h>
#include <Adafruit_BNO055.h>

// Definitions & Initializations For Button And Neopixel Pins
#define PIN       9
#define NUMPIXELS 2

#define PINONE  7
#define PINTWO  8

// Encoder variable initialization
#define RH_ENCODER_A 26 //A pin
#define RH_ENCODER_B 27 //B pin
#define LH_ENCODER_A 28 //A pin
#define LH_ENCODER_B 29 //B pin

volatile int lastRightEncoded = 0;
volatile long rightEncoderValue = 0;
volatile int lastLeftEncoded = 0;
volatile long leftEncoderValue = 0;

// BNO & Neopixel initialization
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// Various variables used for button functionality
int switch1 = 0;
int switch2 = 0;
long stopwatch = 0;
long stopwatch2 = 0;
long buttonDelay = 250;
long now = 0;

// Angle variables
double angle;

// Communication Variables
String msg_start = "S*";
String smsg_end = ";";
char cmsg_end = ';';
int delay_between_msgs = 50;


void ISR_button1() {
  long delta = now - stopwatch;
  if (switch1==0 && delta>buttonDelay) {
    pixels.setPixelColor(0, pixels.Color(0, 200, 0));
    // Serial.println("Button 1 on");
    switch1 = 1;
    stopwatch = now;
  
  } else if (delta>buttonDelay) {
    pixels.setPixelColor(0, pixels.Color(0, 100, 100));
    // Serial.println("Button 1 off");
    switch1 = 0;
    stopwatch = now;
  }
  pixels.show();
}

void ISR_button2() {
  long delta = now - stopwatch2;
  if (switch2==0 && delta>buttonDelay) {
    pixels.setPixelColor(1, pixels.Color(200, 0, 0));
    // Serial.println("Button 2 on");
    switch2 = 1;
    stopwatch2 = now;
  } else if (delta>buttonDelay) {
    pixels.setPixelColor(1, pixels.Color(160, 0, 170));
    // Serial.println("Button 2 off");
    switch2 = 0;
    stopwatch2 = now;
  }
  pixels.show();
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {} // Waiting for port to connect. Needed for native USB communications.
  EncoderInit(); //Initialize the module

  // Check if the angle sensor is working, else stall program
  if (!bno.begin()) {
    Serial.println("No BNO055 detected");
    while (1);
  }

  pixels.begin();  // INITIALIZE NeoPixel strip object (REQUIRED)

  // Initialize pins for the buttons
  pinMode(PINONE, INPUT_PULLUP);
  pinMode(PINTWO, INPUT_PULLUP);

  // Set interrupts for each button, set initial color and stopwatches
  attachInterrupt(digitalPinToInterrupt(PINONE), ISR_button1, RISING);
  attachInterrupt(digitalPinToInterrupt(PINTWO), ISR_button2, RISING);
  pixels.setPixelColor(0, pixels.Color(0, 100, 0));
  pixels.setPixelColor(1, pixels.Color(160, 0, 170));
  pixels.show();
  stopwatch = millis(); // Timer to fix button presses
  stopwatch2 = millis();

  // Get the initial angle
  sensors_event_t orientationData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  angle = orientationData.orientation.x;

}

void loop() {
  now = millis();
  
  // Measure the angle
  sensors_event_t orientationData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  angle = orientationData.orientation.x;

  checkInbox();  // checks for any messages sent to the rp2040 (not used as of rn but built in just in case)
  sendData();
  delay(delay_between_msgs);
}

// Encoder Functions
void EncoderInit() {
  pinMode(LH_ENCODER_A, INPUT_PULLUP);
  pinMode(LH_ENCODER_B, INPUT_PULLUP);
  pinMode(RH_ENCODER_A, INPUT_PULLUP);
  pinMode(RH_ENCODER_B, INPUT_PULLUP);
  attachInterrupt(RH_ENCODER_A , updateRightEncoder, CHANGE);
  attachInterrupt(RH_ENCODER_B , updateRightEncoder, CHANGE);
  attachInterrupt(LH_ENCODER_A , updateLeftEncoder, CHANGE);
  attachInterrupt(LH_ENCODER_B , updateLeftEncoder, CHANGE);
}

// void rightMotorEncoder() {
//   int Lstate = digitalRead(RH_ENCODER_A);
//   // Serial.print("Lstate: ");
//   // Serial.println(Lstate);
//   if((lastRightEncoded == LOW) && Lstate==HIGH)
//   {
//     int val = digitalRead(RH_ENCODER_B);
//     if(val == LOW && Direction)
//     {
//       Direction = false; //Reverse
//     }
//     else if(val == HIGH && !Direction)
//     {
//       Direction = true;  //Forward
//     }
//   }
//   lastRightEncoded = Lstate;

//   if(!Direction)  rcount  ;
//   else  rcount++;
// }

// void leftMotorEncoder() {
//   int Lstate = digitalRead(LH_ENCODER_A);
//   // Serial.print("Lstate: ");
//   // Serial.println(Lstate);
//   if((lastLeftEncoded == LOW) && Lstate==HIGH)
//   {
//     int val = digitalRead(LH_ENCODER_B);
//     if(val == LOW && Direction2)
//     {
//       Direction2 = false; //Reverse
//     }
//     else if(val == HIGH && !Direction2)
//     {
//       Direction2 = true;  //Forward
//     }
//   }
//   lastLeftEncoded = Lstate;

//   if(!Direction2)  lcount  ;
//   else  lcount++;
// }

void updateRightEncoder(){ // The interrupt function for updating the right encoder
  int MSB = digitalRead(RH_ENCODER_A); //MSB = most significant bit
  int LSB = digitalRead(RH_ENCODER_B); //LSB = least significant bit

  int encoded = (MSB << 1) |LSB; //converting the 2 pin value to single number
  int sum  = (lastRightEncoded << 2) | encoded; //adding it to the previous encoded value
  
  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) rightEncoderValue --;
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) rightEncoderValue ++;

  lastRightEncoded = encoded; //store this value for next time
}

void updateLeftEncoder(){ // The interrupt function for updating the left encoder
  int MSB = digitalRead(LH_ENCODER_A); //MSB = most significant bit
  int LSB = digitalRead(LH_ENCODER_B); //LSB = least significant bit

  int encoded = (MSB << 1) |LSB; //converting the 2 pin value to single number
  int sum  = (lastLeftEncoded << 2) | encoded; //adding it to the previous encoded value

  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) leftEncoderValue ++;
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) leftEncoderValue --;

  lastLeftEncoded = encoded; //store this value for next time
}

// Serial Communication Functions
void checkInbox() {
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil(';');  // Read input string
  }
}

void sendData() {
  int bytesAvailable = Serial.availableForWrite();
  String msg = msg_start + "encoder r: " + String(rightEncoderValue) + ", l: " + String(leftEncoderValue) + ", imu: " + String(angle) + smsg_end;
  int stringLength = msg.length();
  if (bytesAvailable > stringLength) {
    Serial.println(msg);
    // Serial.write(msg);
    Serial.flush();
  }
}

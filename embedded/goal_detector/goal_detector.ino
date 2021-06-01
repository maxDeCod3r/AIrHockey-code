#define OUT_ROBOT 6
#define IN_ROBOT 8

#define OUT_PLAYER 7
#define IN_PLAYER 9

int input_value_player;
int input_value_robot;
const int score_threshold_robot = 750;
const int score_threshold_player = 950;
int cycles = 0;

void setup() {
Serial.begin(115200);
pinMode(OUT_ROBOT, OUTPUT);
pinMode(OUT_PLAYER, OUTPUT);
pinMode(IN_ROBOT, INPUT);
pinMode(IN_PLAYER, INPUT);
digitalWrite(OUT_PLAYER, HIGH);
digitalWrite(OUT_ROBOT, HIGH);

}

void loop() {
  cycles++;
//  delay(5);
  input_value_player = analogRead(IN_PLAYER);
  input_value_robot = analogRead(IN_ROBOT);
//  Serial.println(input_value_player);
//  Serial.println(input_value_robot);
  if (input_value_player < score_threshold_player) {
    Serial.println("***ROBOT SCORED***");
    delay(500);
  } else if (input_value_robot < score_threshold_robot) {
    Serial.println("***PLAYER SCORED***");
    delay(500);
  } else {
    if (cycles > 2000) {
          Serial.println("..."); 
          cycles = 0;
    }
  }
}

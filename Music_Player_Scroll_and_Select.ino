#include <Wire.h>
#include <rgb_lcd.h>

rgb_lcd lcd; //Initiate "lcd"

//Pin Variables
const int potPin = A0;
const int buttonPin = 3;
const int speakerPin = 5;

//Scrolling and Songs
const int maxSong = 2;   //Value of max songs **********!!!!!!***********//
int scrollLevel; //Level that is showing!
int noteIndex = 0;
int song_last_played = -1; //TODO check null value---This is an arbitrary number.

//Sprites
byte pauseButton[8] = { 0,27,27,27,27,27,27, 0};   //Pause Button Sprite
byte playButton[8]  = { 8,12,14,15,14,12, 8, 0};   //Play Button Sprite

//Song Names
String songNames[][2] {
    {"Poker Face", ""},
    {"Imperial", "March"},
    {"Super Mario", "Bros."}
};

//Song Notes
int POKER_FACE_NOTE_LIST[] = {};
int IMPERIAL_MARCH_NOTE_LIST[] = {};
int SUPER_MARIO_BROS_NOTE_LIST[] = {};

//Note Lengths
float POKER_FACE_NOTE_LENGTHS[] = {};
float IMPERIAL_MARCH_NOTE_LENGTHS[] = {};
float SUPER_MARIO_BROS_NOTE_LENGTHS[] = {};

//Time Variables
unsigned long currentTime;
unsigned long time_since_last_press = 0;
const int debounceTime = 30;                  //Milliseconds of buffer time

//Sensors
int potPosition;
bool buttonPosition;
//bool buttonTrue;

//Play+Pause
bool pauseTrue;
bool playTrue;

/*TODO
buttonState = changePlayButton(buttonState);

*/

void set_pause(){     //Set "pauseTrue" to true in order to close conditional loop
  noTone(buttonPin);
  pauseTrue = true;
}

int checkPot_and_scrollLevel(){      //Return scroll value
  potPosition = analogRead(potPin);
  delay(10);
  scrollLevel = map(potPosition,0,1023,0,maxSong);
  return scrollLevel;
}

/*int _scroll(){
  scrollLevel = checkPot();          //Obselete
  return scrollLevel;
}*/

bool checkSelect(){
  currentTime = millis();
  buttonPosition = digitalRead(buttonPin);
  if(buttonPosition == true && millis()>= time_since_last_press + debounceTime){
    time_since_last_press = millis();
    return true;
  }
  else{
    return false;
  }
}

void play_song(int noteList[],float noteLength[]){
  if(song_last_played != scrollLevel){
    song_last_played = scrollLevel;
    noteIndex = 0;
  }
    for (; noteIndex < sizeof(noteList) / sizeof(int) ; noteIndex++) {
      /*if(checkSelect() == true){
        break;
      }*/
      tone(speakerPin, noteList[noteIndex], noteLength[noteIndex]);
  }
}

void screenScroll(int scrollLevel) {
    //The if statement is for button. Do not use with potentiometer.    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(scrollLevel + 1);
    lcd.setCursor( (16 - songNames[scrollLevel][0].length() ) / 2 , 0);
    lcd.print(songNames[scrollLevel][0]);
    lcd.setCursor( (16 - songNames[scrollLevel][1].length() ) / 2 , 1);
    lcd.print(songNames[scrollLevel][1]);
    changePlayButton(1);
    delay(10);
    }

int changePlayButton(int state) {    //Changes play and pause button
    state = (state + 1) % 2;
    
    lcd.setCursor (15,0);
    lcd.write(byte(state));

    return state;
}



void setup() {
  pinMode(potPin,INPUT);
  pinMode(buttonPin, INPUT);
  pinMode(speakerPin, OUTPUT);
  lcd.begin(16, 2);
  lcd.createChar(0, pauseButton);
  lcd.createChar(1, playButton);
  screenScroll(checkPot_and_scrollLevel());
  
}

void loop() {
  while(checkSelect() == false){
    screenScroll(checkPot_and_scrollLevel());
  }
  if (scrollLevel == 0){
    play_song(POKER_FACE_NOTE_LIST,POKER_FACE_NOTE_LENGTHS);
  }
  if(scrollLevel == 1){
    play_song(IMPERIAL_MARCH_NOTE_LIST,IMPERIAL_MARCH_NOTE_LENGTHS);
  }
  if(scrollLevel == 2){
    play_song(SUPER_MARIO_BROS_NOTE_LIST,SUPER_MARIO_BROS_NOTE_LENGTHS);
  }
}



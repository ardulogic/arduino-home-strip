#include <Adafruit_NeoPixel.h>

// ---- Adjust these to match your setup ----
#define LED_PIN       5        // Data pin connected to the strip (D5)
#define NUM_LEDS      30       // Number of LEDs (set to your exact count)
#define BRIGHTNESS    77       // ~30% of 255 ≈ 76.5 → 77

// Audio visualization LED range (1-based indexing)
#define AUDIO_START_LED  1     // First LED for audio visualization
#define AUDIO_END_LED    14     // Last LED for audio visualization
// ------------------------------------------

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// Configurable red color (default: bright red)
uint8_t redR = 255;
uint8_t redG = 0;
uint8_t redB = 0;

// State variables
enum State {
  STATE_IDLE,
  STATE_MOUSE_ACTIVE,
  STATE_KEYBOARD_ACTIVE,
  STATE_FADING_TO_RED,
  STATE_FADING_TO_BLACK,
  STATE_AUDIO_ACTIVE
};

State currentState = STATE_IDLE;
int currentLedPos = 0;  // Current LED position for keyboard mode
unsigned long lastActivityTime = 0;
unsigned long lastTypingTime = 0;
unsigned long lastAudioTime = 0;
const unsigned long IDLE_TIMEOUT = 5000;  // 5 seconds
const unsigned long TRANSITION_TIME = 1000;  // 1 second for transitions
const unsigned long AUDIO_TIMEOUT = 200;  // 200ms - if no audio for this long, clear visualization

int audioLevel = 0;  // Current audio level (0 to numAudioLeds)

// Calculate number of LEDs in audio range
const int numAudioLeds = AUDIO_END_LED - AUDIO_START_LED + 1;

// Fade variables
unsigned long fadeStartTime = 0;
uint32_t fadeStartColor = 0;
uint32_t fadeTargetColor = 0;
bool isFading = false;

void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.clear();
  strip.show();
  lastActivityTime = millis();
  lastTypingTime = millis();
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleCommand(command);
  }
  
  // Update state machine
  updateState();
  
  // Render current state
  renderState();
  
  delay(10);  // Small delay for stability
}

void handleCommand(String cmd) {
  if (cmd.length() == 0) return;
  
  char cmdType = cmd.charAt(0);
  
  switch (cmdType) {
    case 'M':  // Mouse moved
      if (currentState != STATE_KEYBOARD_ACTIVE) {
        startFadeToRed();
        currentState = STATE_MOUSE_ACTIVE;
      }
      lastActivityTime = millis();
      break;
      
    case 'K':  // Key pressed (normal key)
      if (currentState != STATE_KEYBOARD_ACTIVE) {
        currentState = STATE_KEYBOARD_ACTIVE;
        isFading = false;
      }
      // Move to next LED
      currentLedPos = (currentLedPos + 1) % NUM_LEDS;
      lastActivityTime = millis();
      lastTypingTime = millis();
      break;
      
    case 'B':  // Backspace
      if (currentState == STATE_KEYBOARD_ACTIVE) {
        // Move backwards
        currentLedPos = (currentLedPos - 1 + NUM_LEDS) % NUM_LEDS;
      }
      lastActivityTime = millis();
      lastTypingTime = millis();
      break;
      
    case 'S':  // Space - flash whole strip red
      flashStrip();
      lastActivityTime = millis();
      lastTypingTime = millis();
      break;
      
    case 'C':  // Set color: C,r,g,b
      {
        int firstComma = cmd.indexOf(',');
        if (firstComma > 0) {
          int secondComma = cmd.indexOf(',', firstComma + 1);
          int thirdComma = cmd.indexOf(',', secondComma + 1);
          if (secondComma > 0 && thirdComma > 0) {
            redR = cmd.substring(firstComma + 1, secondComma).toInt();
            redG = cmd.substring(secondComma + 1, thirdComma).toInt();
            redB = cmd.substring(thirdComma + 1).toInt();
          }
        }
      }
      break;
      
    case 'A':  // Audio level: A,level (0 to numAudioLeds, clamped to configured range)
      {
        int commaPos = cmd.indexOf(',');
        if (commaPos > 0) {
          int level = cmd.substring(commaPos + 1).toInt();
          // Clamp to configured audio LED range
          audioLevel = constrain(level, 0, numAudioLeds);
          currentState = STATE_AUDIO_ACTIVE;
          lastAudioTime = millis();
          lastActivityTime = millis();
        }
      }
      break;
      
  }
}

void updateState() {
  unsigned long currentTime = millis();
  
  // Check if audio stopped
  if (currentState == STATE_AUDIO_ACTIVE) {
    if (currentTime - lastAudioTime > AUDIO_TIMEOUT) {
      audioLevel = 0;
      // Don't change state immediately, let it fade naturally
    }
  }
  
  // Check if typing stopped for 5 seconds
  if (currentState == STATE_KEYBOARD_ACTIVE) {
    if (currentTime - lastTypingTime > IDLE_TIMEOUT) {
      startFadeToRed();
      currentState = STATE_FADING_TO_RED;
    }
  }
  
  // Check if no activity - fade to black (but not if audio is active)
  if (currentState != STATE_FADING_TO_BLACK && 
      currentState != STATE_KEYBOARD_ACTIVE &&
      currentState != STATE_AUDIO_ACTIVE &&
      currentTime - lastActivityTime > IDLE_TIMEOUT) {
    startFadeToBlack();
    currentState = STATE_FADING_TO_BLACK;
  }
  
  // Check if fade completed
  if (isFading) {
    unsigned long elapsed = currentTime - fadeStartTime;
    if (elapsed >= TRANSITION_TIME) {
      isFading = false;
      if (currentState == STATE_FADING_TO_RED) {
        currentState = STATE_MOUSE_ACTIVE;
      } else if (currentState == STATE_FADING_TO_BLACK) {
        currentState = STATE_IDLE;
      }
    }
  }
}

void renderState() {
  switch (currentState) {
    case STATE_IDLE:
      strip.clear();
      strip.show();
      break;
      
    case STATE_MOUSE_ACTIVE:
      if (!isFading) {
        // Solid red
        strip.fill(getRedColor());
        strip.show();
      } else {
        renderFade();
      }
      break;
      
    case STATE_KEYBOARD_ACTIVE:
      // Show current LED position
      strip.clear();
      strip.setPixelColor(currentLedPos, getRedColor());
      strip.show();
      break;
      
    case STATE_AUDIO_ACTIVE:
      renderAudioLevel();
      break;
      
    case STATE_FADING_TO_RED:
    case STATE_FADING_TO_BLACK:
      renderFade();
      break;
  }
}

void renderAudioLevel() {
  // Clear all LEDs first
  strip.clear();
  
  if (audioLevel == 0) {
    // Make sure LEDs outside audio range stay cleared
    for (int i = 0; i < AUDIO_START_LED - 1; i++) {
      if (i < NUM_LEDS) strip.setPixelColor(i, 0);
    }
    for (int i = AUDIO_END_LED; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
    return;
  }
  
  // Render level meter from center to sides on configured LED range
  // Convert 1-based LED numbers to 0-based indices
  int startIdx = AUDIO_START_LED - 1;
  int endIdx = AUDIO_END_LED - 1;
  
  // If level equals number of LEDs, light all LEDs in range
  if (audioLevel >= numAudioLeds) {
    for (int i = startIdx; i <= endIdx; i++) {
      if (i >= 0 && i < NUM_LEDS) {
        strip.setPixelColor(i, getRedColor());
      }
    }
    // Clear LEDs outside range
    for (int i = 0; i < startIdx; i++) {
      if (i < NUM_LEDS) strip.setPixelColor(i, 0);
    }
    for (int i = endIdx + 1; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
    return;
  }
  
  int centerIdx = (startIdx + endIdx) / 2;  // Center index
  
  // For level N, light up N LEDs symmetrically from center
  // Calculate how many LEDs on each side of center
  // For odd N: (N-1)/2 on left, center, (N-1)/2 on right
  // For even N: N/2 on left, N/2 on right (no single center)
  int ledsOnLeft = (audioLevel - 1) / 2;   // LEDs to the left of center (not including center)
  int ledsOnRight = (audioLevel + 1) / 2;  // LEDs to the right including center (rounds up)
  
  // Calculate start and end positions (0-indexed, clamped to audio range)
  // Start from center and expand outward
  int startLed = max(startIdx, centerIdx - ledsOnLeft);      // Start from left side
  int endLed = min(endIdx, centerIdx + ledsOnRight - 1);      // End on right side (-1 because centerIdx is 0-indexed)
  
  // Light up LEDs symmetrically from center
  // Only light LEDs within the audio range
  for (int i = startLed; i <= endLed; i++) {
    // Ensure we only light LEDs in the configured audio range
    if (i >= startIdx && i <= endIdx && i >= 0 && i < NUM_LEDS) {
      strip.setPixelColor(i, getRedColor());
    }
  }
  
  // Explicitly clear LEDs outside the audio range to be safe
  for (int i = 0; i < startIdx; i++) {
    if (i < NUM_LEDS) {
      strip.setPixelColor(i, 0);
    }
  }
  for (int i = endIdx + 1; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0);
  }
  
  strip.show();
}

void startFadeToRed() {
  if (!isFading) {
    isFading = true;
    fadeStartTime = millis();
    fadeStartColor = getCurrentColor();
    fadeTargetColor = getRedColor();
  }
}

void startFadeToBlack() {
  if (!isFading) {
    isFading = true;
    fadeStartTime = millis();
    fadeStartColor = getCurrentColor();
    fadeTargetColor = 0;  // Black
  }
}

void renderFade() {
  if (!isFading) return;
  
  unsigned long elapsed = millis() - fadeStartTime;
  float progress = min(1.0, (float)elapsed / TRANSITION_TIME);
  
  // Smooth easing (ease-in-out)
  progress = progress * progress * (3.0 - 2.0 * progress);
  
  uint8_t startR = (fadeStartColor >> 16) & 0xFF;
  uint8_t startG = (fadeStartColor >> 8) & 0xFF;
  uint8_t startB = fadeStartColor & 0xFF;
  
  uint8_t targetR = (fadeTargetColor >> 16) & 0xFF;
  uint8_t targetG = (fadeTargetColor >> 8) & 0xFF;
  uint8_t targetB = fadeTargetColor & 0xFF;
  
  uint8_t r = startR + (targetR - startR) * progress;
  uint8_t g = startG + (targetG - startG) * progress;
  uint8_t b = startB + (targetB - startB) * progress;
  
  strip.fill(strip.Color(r, g, b));
  strip.show();
}

uint32_t getCurrentColor() {
  // Get the color of the first pixel (assuming all are same)
  return strip.getPixelColor(0);
}

uint32_t getRedColor() {
  return strip.Color(redR, redG, redB);
}

void flashStrip() {
  // Flash the whole strip red
  strip.fill(getRedColor());
  strip.show();
  delay(100);
  strip.clear();
  strip.show();
}

#include <Bluepad32.h>

ControllerPtr controllers[BP32_MAX_GAMEPADS] = { nullptr };

void onConnectedController(ControllerPtr ctl) {
  for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
    if (controllers[i] == nullptr) {
      controllers[i] = ctl;
      Serial.printf("Controller connected at index %d\n", i);
      Serial.printf("Model: %s, VID=0x%04x, PID=0x%04x\n",
                    ctl->getModelName().c_str(),
                    ctl->getProperties().vendor_id,
                    ctl->getProperties().product_id);
      break;
    }
  }
}

void onDisconnectedController(ControllerPtr ctl) {
  for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
    if (controllers[i] == ctl) {
      Serial.printf("Controller disconnected from index %d\n", i);
      controllers[i] = nullptr;
      break;
    }
  }
}

void dumpGamepad(ControllerPtr ctl) {
  Serial.printf(
    "idx=%d, dpad=0x%02x, buttons=0x%04x, axisL: %4d, %4d, axisR: %4d, %4d, throttle=%4d, brake=%4d\n",
    ctl->index(),
    ctl->dpad(),
    ctl->buttons(),
    ctl->axisX(),   // left joystick X
    ctl->axisY(),   // left joystick Y
    ctl->axisRX(),  // right joystick X
    ctl->axisRY(),  // right joystick Y
    ctl->throttle(),// if supported
    ctl->brake()    // if supported
  );
}

void processControllers() {
  for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
    ControllerPtr ctl = controllers[i];
    if (ctl && ctl->isConnected() && ctl->hasData()) {
      // Print gamepad state
      dumpGamepad(ctl);
      // You could add checks like:
      // if (ctl->buttons() & SOME_BUTTON_MASK) { … }
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Starting Bluepad32 test for Xbox controller");

  Serial.printf("Firmware version: %s\n", BP32.firmwareVersion());
  char buf[20];
  const uint8_t *addr = BP32.localBdAddress();
  snprintf(buf, sizeof(buf), "BD Addr: %02X:%02X:%02X:%02X:%02X:%02X",
           addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]);
  Serial.println(buf);

  BP32.setup(&onConnectedController, &onDisconnectedController);
  BP32.forgetBluetoothKeys();        // optional: clear previously paired controllers
  BP32.enableVirtualDevice(false);   // disable HID mouse/keyboard if not needed
}

void loop() {
  if (BP32.update()) {
    processControllers();
  }
  delay(150); // yield to avoid watchdog reset
}

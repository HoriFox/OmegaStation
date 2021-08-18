#!/usr/bin/env python3

import time
from rpi_ws281x import *
import argparse
from threading import Thread


LED_COUNT      = 12      # Number of LED pixels.
#LED_PIN        = 13      # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class LEDAnimation:
    signal_queue = []
    state = None
    sound_volume = 0
    _last_state = None
    _smooth_sound_volume = 0
    #state_switch = {'idle' : idle,
    #                'loading' : loading,
    #                'heil' : heil}

    def __init__(self, color, wait_ms=50):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        self.color = color
        self.wait_ms = wait_ms
        self.state = 'idle'
        self._last_state = 'idle'


    def get_rign_index(self, index):
        return index if index >= 0 else self.strip.numPixels() - abs(index)


    def idle(self):
        pass


    def loading(self):
        led=[255, 224, 193, 162, 131, 100, 69, 38, 7, 0, 0, 0]
        changeState = 1
        smooth_value = 20
        smooth_sep = int(255 / smooth_value)
        for q in range(self.strip.numPixels()):
            for i, col_c in enumerate(led):
                self.strip.setPixelColor(self.get_rign_index(q-i), self.color & col_c)
            self.strip.show()
            time.sleep(self.wait_ms/1000.0)


    def heil(self):
        l_wait_ms = 5
        l_iteration = 2
        for _ in range(l_iteration):
            smooth_value = 20
            smooth_sep = int(255 / smooth_value)
            for i in range(smooth_value):
                for q in range(self.strip.numPixels()):
                    self.strip.setPixelColor(q, self.color & (smooth_sep * i))
                self.strip.show()
                time.sleep(l_wait_ms/1000.0)
            for i in range(smooth_value, 0, -1):
                for q in range(self.strip.numPixels()):
                    self.strip.setPixelColor(q, self.color & (smooth_sep * (i - 1)))
                self.strip.show()
                time.sleep(l_wait_ms/1000.0)


    def visualization(self):
         l_wait_ms = 5
         change_value = self.sound_volume - self._smooth_sound_volume
         l_smooth_value = 10
         change_path_value = change_value / l_smooth_value
         for smooth_i in range(l_smooth_value):
             for q in range(self.strip.numPixels()):
                 self.strip.setPixelColor(q, self.color & int(self._smooth_sound_volume * 2.55))
             self.strip.show()
             time.sleep(l_wait_ms/1000.0)
             self._smooth_sound_volume += change_path_value


    def switch(self, action):
        if action == 'idle':
            self.idle()
        elif action == 'loading':
            self.loading()
        elif action == 'heil':
            self.heil()
        elif action == 'visualization':
            self.visualization()


    def led_loop(self):
        while True:
            while len(self.signal_queue) > 0:
                self.switch(self.signal_queue.pop())
            #if self._last_state != self.state:
            #    self.transition
            self.switch(self.state)
            #self.state_switch[self.state]()


    def run(self):
        self.led_thread = Thread(target=self.led_loop)
        self.led_thread.start()


    def stop(self):
        self.led_thread.join()


if __name__ == '__main__':
    led = LEDAnimation(Color(0, 0, 255))
    led.run()
    led.state = 'loading'
    time.sleep(2)
    led.signal_queue.append('heil')
    time.sleep(2)

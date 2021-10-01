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


class ColorPro:
    red = 0
    green = 0
    blue = 0
    alpha = 1

    def __init__(self, red_, green_, blue_, alpha_ = 1):
        self.red = red_
        self.green = green_
        self.blue = blue_
        self.alpha = alpha_

    def color(self, alpha = None):
        out_alpha = alpha if alpha is not None else self.alpha
        return Color(int(self.red * out_alpha), int(self.green * out_alpha), int(self.blue * out_alpha))



class LEDAnimation:
    signal_queue = []
    state = None
    sound_volume = 0

    #Tech var
    _thread_loop = False
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


    def loading(self, param):
        color_pro = param['color'] if param and 'color' in param else self.color
        led=[255, 224, 193, 162, 131, 100, 69, 38, 7, 0, 0, 0]
        #changeState = 1
        #smooth_value = 20
        #smooth_sep = int(255 / smooth_value)
        for q in range(self.strip.numPixels()):
            for i, col_c in enumerate(led):
                self.strip.setPixelColor(self.get_rign_index(q-i), color_pro.color(col_c / 255))
            self.strip.show()
            time.sleep(self.wait_ms/1000.0)


    def heil(self, param):
        brightness = 30
        color_pro = param['color'] if param and 'color' in param else self.color
        l_wait_ms = 5
        l_iteration = 2
        for _ in range(l_iteration):
            smooth_value = 20
            smooth_sep = 1 / smooth_value
            for i in range(smooth_value):
                for q in range(self.strip.numPixels()):
                    self.strip.setPixelColor(q, color_pro.color(alpha=((smooth_sep * i) / 100 * brightness)))
                self.strip.show()
                time.sleep(l_wait_ms/1000.0)
            for i in range(smooth_value, 0, -1):
                for q in range(self.strip.numPixels()):
                     self.strip.setPixelColor(q, color_pro.color(alpha=((smooth_sep * (i - 1)) / 100 * brightness)))
                self.strip.show()
                time.sleep(l_wait_ms/1000.0)


    def visualization(self, param):
         brightness = 30
         color_pro = param['color'] if param and 'color' in param else self.color
         l_wait_ms = 5
         change_value = self.sound_volume - self._smooth_sound_volume
         l_smooth_value = 10
         change_path_value = change_value / l_smooth_value
         for smooth_i in range(l_smooth_value):
             for q in range(self.strip.numPixels()):
                 self.strip.setPixelColor(q, color_pro.color(alpha=(self._smooth_sound_volume / 10000 * brightness)))
             self.strip.show()
             time.sleep(l_wait_ms/1000.0)
             self._smooth_sound_volume += change_path_value


    def clear(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, ColorPro(0,0,0).color())
        self.strip.show()

    def switch(self, signal):
        action, param = signal
        if action == 'idle':
            self.idle()
        elif action == 'loading':
            self.loading(param)
        elif action == 'heil':
            self.heil(param)
        elif action == 'visualization':
            self.visualization(param)


    def led_loop(self):
        while self._thread_loop:
            while len(self.signal_queue) > 0:
                self.switch(self.signal_queue.pop())
            #if self._last_state != self.state:
            #    self.transition
            self.switch((self.state, None))
            #self.state_switch[self.state]()
        self.clear()

    def run(self):
        self.led_thread = Thread(target=self.led_loop)
        self._thread_loop = True
        self.led_thread.start()


    def stop(self):
        self._thread_loop = False
        #self.led_thread.join()

if __name__ == '__main__':
    led = LEDAnimation(ColorPro(0, 255, 0))
    led.run()
    led.state = 'loading'
    time.sleep(2)
#    led.state = 'visualization'
#    time.sleep(5)
    led.signal_queue.append(('heil', None))
    time.sleep(2)

# OmegaStation  
**Описание**  
Умная станция/колонка комлекса умный дом

**Архитектура**

![Схема работы](https://github.com/HoriFox/OmegaStation/blob/master/img/Omega%20station.png)

**Параметры запуска**
* Rate: 16000
* Channels: 1
* Port: 4444
* Chunk: 4096
* Device: 0 (номер звуковой карты в sounddevice)

**Минимум запуска**  
1. Модифицировать конфигурационный файл
2. Запустить на сервере (raspberry pi 4) и клиент (raspberry zero w):  
`python3 station_service.py`  

**Зависимости - звуковая карта**  
* Сервер:  
```
sudo apt install git python3-pip
pip3 install vosk
```
Если требуется модель:
```
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.15.zip
unzip vosk-model-small-ru-0.15.zip
mv vosk-model-small-ru-0.15 model
```
Если будет ругаться на libfortran:
```
wget https://raw.githubusercontent.com/raspberrypi/tools/master/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian/arm-linux-gnueabihf/lib/libgfortran.so.3.0.0
sudo cp libgfortran.so.3.0.0 /lib/arm-linux-gnueabihf/libgfortran.so.3
sudo rm /etc/ld.so.cache
sudo ldconfig
ldconfig -p | grep libgfortran
```

* Клиент:  
```
git clone https://github.com/waveshare/WM8960-Audio-HAT
cd WM8960-Audio-HAT
sudo ./install.sh
sudo reboot
```
После перезапуска желательно ещё раз:
```
sudo dkms status
cd WM8960-Audio-HAT
sudo ./install.sh
sudo reboot
```
После второго перезапуска должна отображаться версия:
```
sudo dkms status
```
Проверка звука:
```
sudo arecord -f cd -Dhw:0 | aplay -Dhw:0
```
При ошибке OSError('PortAudio library not found'):
```
sudo apt-get install libportaudio2
sudo apt-get install libasound-dev
```

**Зависимости - подсветка**  
* Клиент:  

Редактируем файл для того чтобы правильно выводить ШИМ сигнал на 18 порт,  
Отключаем встроенную звуковую карту на порту:  
`sudo nano /boot/config.txt`  
В файле комментируем данную строчку:  
`#dtparam=audio=on`  
Перезапустим для надёжности:  
`sudo reboot`  

Произведём компил rpi_ws281x и поставим пакет:  
```
sudo apt-get install scons swig
git clone https://github.com/jgarff/rpi_ws281x
cd rpi_ws281x/
sudo scons
sudo python3 setup.py build install
sudo pip3 install adafruit-circuitpython-neopixel
```  
Протестируем подсветку:  
`sudo python3 strandtest.py`


**Заметка**

Подключиться к wifi на raspberry zero w cli версии:
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
В конфиге прописать данные:
```
network={
ssid="The SSID of your network (eg. Network name)"
psk="Your Wifi Password"
}
```
Переподнять и перезагрузка:
```
sudo ip link set wlan0 down
sudo ip link set wlan0 up
reboot
```

# OmegaStation  
**Описание**  
Умная станция/колонка комлекса умный дом

**Параметры запуска**
* Rate: 16000
* Channels: 1
* Port: 4444
* Chunk: 4096
* Device: 0 (номер звуковой карты в sounddevice)

**Минимум запуска**  
* Сервер (raspberry pi 4):  
`python3 omega_server.py`  
* Клиент (raspberry zero w):  
`python3 omega_client.py -i [ip хоста с запущенным сервером]`

***

![Схема работы](https://github.com/HoriFox/OmegaStation/blob/master/img/Omega%20station.png)

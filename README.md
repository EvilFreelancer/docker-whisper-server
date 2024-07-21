# Whisper.cpp API Webserver in Docker

Whisper.cpp HTTP-сервер для автоматического распознавания речи (ASR) с API подобным OpenAI в Docker-контейнере.

Этот проект содержит в себе набор инструментов и конфигураций для сборки
Docker-контейнера с сервером транскрипции, основанным
на [whisper.cpp server](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server).

**Русский** | [中文](./README.zh.md) | [English](./README.en.md)

## Возможности

- Docker-контейнер с HTTP-сервером транскрипции Whisper.cpp
- Настраивается через переменные окружения
- Автоматически конвертирует аудио в формат WAV
- Автоматически скачивает выбранную модель при запуске (если её нет)
- Может квантовать любую модель Whisper до нужного уровня при запуске

## Требования

Docker-контейнер собирается в две стадии, сначала берётся базовый
образ `nvidia/cuda:12.5.1-devel-ubuntu22.04`, в нём происходит компиляция бинарников `server` и `quantize`, далее на
второй стадии используется контейнер `nvidia/cuda:12.5.1-runtime-ubuntu22.04`, в него доустанавливаются нужные пакеты и
копируются бинарные файлы собранные на предыдущем этапе.

По идее если вы понизите версию контейнера `nvidia/cuda` вплоть до `12.1` проблем не возникнет, но я не проверял.

Поэтому, прежде чем начать убедитесь, что в вашей системе установлена карточка с GPU, который поддерживает современную
CUDA и установлен свежий CUDA драйвер.

И так, для работы проекта понадобится:

* Видеокарта от Nvidia >= GTX 10xx (или аналог)
* CUDA >= 12.5 (хотя скорее всего и на 12.1 всё будет ок)
* Docker
* Docker Compose
* Nvidia Docker Runtime

Подробную инструкцию по подготовке Linux-машины к запуску нейросетей, включая установку CUDA, Docker и Nvidia Docker
Runtime вы сможете найти в моей публикации
"[Как подготовить Linux к запуску и обучению нейросетей? (+ Docker)](https://dzen.ru/a/ZVt9kRBCTCGlQqyP)".

## Установка

1. Склонируем репозиторий, после чего перейдём в корень с исходниками:

   ```shell
   git clone https://github.com/EvilFreelancer/docker-whisper-server.git
   cd docker-whisper-server

2. Скопируем конфигурацию Docker Compose из шаблона:

   ```shell
   cp docker-compose.dist.yml docker-compose.yml
   ```

   В конфигурации вы можете настроить переменные окружения, версию whisper.cpp, порты, подключаемы тома и так далее.

   Например, вот так можно собрать сервер из ветки `master` и при работе использовать модель `base`, которая
   будет квантизирована до `q4_0` и запущена на `1` ядре процессора в `4` потока.

   ```yaml
   version: "3.9"
   services:
     restart: "unless-stopped"
     whisper:
       build:
         context: ./whisper
         args:
           # В качестве версии можно указать: тег, ветку или коммит
           # https://github.com/ggerganov/whisper.cpp
           - WHISPER_VERSION=master
       volumes:
         - ./models:/app/models
       ports:
         - "127.0.0.1:9000:9000"
       environment:
         WHISPER_MODEL: base
         WHISPER_MODEL_QUANTIZATION: q4_0
         WHISPER_PROCESSORS: 1
         WHISPER_THREADS: 4
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: 1
                 capabilities: [ gpu ]
   ```

3. Соберём Docker-образ:

   ```shell
   docker-compose build
   ```

4. Запустим Docker-контейнер:

   ```shell
   docker-compose up -d
   ```

5. Перейдем по адресу http://localhost:8080 в браузере:

   ![Swagger UI](./assets/swagger.png)

## Эндпоинты

### /inference

Транскрибируем аудиофайл:

```shell
curl 127.0.0.1:9000/inference \
  -H "Content-Type: multipart/form-data" \
  -F file="@<file-path>" \
  -F language="auto" \
  -F response_format="json"
```

Вместо `language="auto"` (автоопределение языка аудио) вы можете явно передать нужный, например `language="ru"`.

Вместо `response_format="json"` можно попросить систему вернуть субтитры `response_format="srt"` или просто текст `response_format="text"`.

### /load

Сменить модель Whisper:

```shell
curl 127.0.0.1:9000/load \
   -H "Content-Type: multipart/form-data" \
   -F model="<path-to-model-file-in-docker-container>"
```

## Переменные окружения

**Базовая конфигурация**

| Name                         | Default                               | Description                                                                                                                 |
|------------------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `WHISPER_MODEL`              | base                                  | Модель Whisper, используемая по умолчанию                                                                                   |
| `WHISPER_MODEL_PATH`         | /app/models/ggml-${WHISPER_MODEL}.bin | Путь к файлу модели Whisper по умолчанию                                                                                    |
| `WHISPER_MODEL_QUANTIZATION` |                                       | Уровень квантования ([подробнее тут](https://github.com/ggerganov/whisper.cpp/tree/master?tab=readme-ov-file#quantization)) |

<details>
<summary>
<i><b>Расширенная конфигурация</b></i>
</summary>

| Name                      | Default    | Description                                            |
|---------------------------|------------|--------------------------------------------------------|
| `WHISPER_THREADS`         | 4          | Количество потоков для инференса                       |
| `WHISPER_PROCESSORS`      | 1          | Количество процессоров для инференса                   |
| `WHISPER_HOST`            | 0.0.0.0    | IP-адрес или имя хоста для привязки сервера            |
| `WHISPER_PORT`            | 9000       | Номер порта для прослушивания                          |
| `WHISPER_INFERENCE_PATH`  | /inference | Путь для всех запросов инференса                       |
| `WHISPER_PUBLIC_PATH`     |            | Путь к публичной папке                                 |
| `WHISPER_REQUEST_PATH`    |            | Путь для всех запросов                                 |
| `WHISPER_OV_E_DEVICE`     | CPU        | Устройство OpenViBE для обработки событий              |
| `WHISPER_OFFSET_T`        | 0          | Временное смещение в миллисекундах                     |
| `WHISPER_OFFSET_N`        | 0          | Количество секунд для смещения                         |
| `WHISPER_DURATION`        | 0          | Длительность аудиофайла в миллисекундах                |
| `WHISPER_MAX_CONTEXT`     | -1         | Максимальный размер контекста для инференса            |
| `WHISPER_MAX_LEN`         | 0          | Максимальная длина выходного текста                    |
| `WHISPER_BEST_OF`         | 2          | Стратегия "лучший из N" для инференса                  |
| `WHISPER_BEAM_SIZE`       | -1         | Размер beam для поиска                                 |
| `WHISPER_AUDIO_CTX`       | 0          | Аудиоконтекст для инференса                            |
| `WHISPER_WORD_THOLD`      | 0.01       | Порог слов для сегментации                             |
| `WHISPER_ENTROPY_THOLD`   | 2.40       | Порог энтропии для сегментации                         |
| `WHISPER_LOGPROB_THOLD`   | -1.00      | Порог логарифма вероятности для сегментации            |
| `WHISPER_LANGUAGE`        | en         | Код языка для перевода или диаризации                  |
| `WHISPER_PROMPT`          |            | Начальный промт                                        |
| `WHISPER_DTW`             |            | Вычислять временные метки на уровне токенов            |
| `WHISPER_CONVERT`         | true       | Конвертировать аудио в WAV, требует ffmpeg на сервере  |
| `WHISPER_SPLIT_ON_WORD`   | false      | Разделить по слову, а не по токену                     |
| `WHISPER_DEBUG_MODE`      | false      | Включить режим отладки                                 |
| `WHISPER_TRANSLATE`       | false      | Перевод с исходного языка на английский                |
| `WHISPER_DIARIZE`         | false      | Диаризация стерео аудио                                |
| `WHISPER_TINYDIARIZE`     | false      | Включить tinydiarize (требует модель tdrz)             |
| `WHISPER_NO_FALLBACK`     | false      | Не использовать temperature fallback при декодировании |
| `WHISPER_PRINT_SPECIAL`   | false      | Печатать специальные токены                            |
| `WHISPER_PRINT_COLORS`    | false      | Печатать цвета                                         |
| `WHISPER_PRINT_REALTIME`  | false      | Печатать вывод в реальном времени                      |
| `WHISPER_PRINT_PROGRESS`  | false      | Печатать прогресс                                      |
| `WHISPER_NO_TIMESTAMPS`   | false      | Не печатать временные метки                            |
| `WHISPER_DETECT_LANGUAGE` | false      | Выйти после автоматического определения языка          |

</details>

## Квантизация

Доступные уровни квантования которые можно указать через переменную `WHISPER_MODEL_QUANTIZATION`:

```text
q2_k или 10
q3_k или 11
q4_0 или 2
q4_1 или 3
q4_k или 12
q5_0 или 8
q5_1 или 9
q5_k или 13
q6_k или 14
q8_0 или 7
```

В случае если передать целое число скрипт entrypoint.sh [автоматически](https://github.com/EvilFreelancer/docker-whisper-server/blob/main/whisper/entrypoint.sh#L20-L36) преобразует его в соответствующую комбинация символов вида `qX_X`.

Подробнее о [квантизации](https://github.com/ggerganov/whisper.cpp/tree/master?tab=readme-ov-file#quantization) в документации проекта whisper.cpp.

## Ссылки

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- [пример сервера](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server) whisper.cpp

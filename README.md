# Whisper.cpp API Webserver in Docker

Whisper.cpp HTTP-сервер для автоматического распознавания речи (ASR) с API подобным OpenAI в Docker-контейнере.

Этот проект содержит в себе набор инструментов и конфигураций для сборки
Docker-контейнера с сервером транскрипции, основанным
на [whisper.cpp server](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server).

**Русский** | [中文](./README.zh.md) | [English](./README.en.md)

## Содержание

* [Требования](#Требования)
* [Установка](#Установка)
* [Whisper.cpp API-сервер](#Whisper.cpp-API-сервер)
    * [Swagger документация Whisper.cpp](#Swagger-документация-Whisper.cpp)
    * [Эндпоинты](#Эндпоинты)
    * [Переменные окружения](#Переменные-окружения)
    * [Квантизация](#Квантизация)
* [OpenAI-like API-сервер](#OpenAI-like-API-сервер)
    * [Пример config.yml](#Пример-config.yml)
    * [Swagger документация сервера](#Swagger-документация-сервера)
    * [Эндпоинты](#Эндпоинты)
* [Ссылки](#Ссылки)

## Требования

Docker-контейнер для Whisper.cpp собирается в две стадии, сначала берётся базовый
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

3. Скопируем конфигурацию OpenAI-like API сервера:

   ```shell
   cp config.dist.yml config.yml
   ```

4. Соберём Docker-образы:

   ```shell
   docker-compose build
   ```

5. Запустим Docker-контейнеры:

   ```shell
   docker-compose up -d
   ```

## Whisper.cpp API-сервер

В конфигурации `docker-compose.yml` вы можете настроить переменные окружения, версию whisper.cpp, порты, подключаемы
тома и так далее.

Например, вот так можно собрать сервер из ветки `master` и при работе использовать модель `base`, которая
будет квантизирована до `q4_0` и запущена на `1` ядре процессора в `4` потока.

```yaml
  whisper:
    restart: "unless-stopped"
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
```

### Swagger документация Whisper.cpp

Сервис `whisper-swagger` предоставляет визуализацию и документацию всех доступных эндпоинтов.

```yaml
  whisper-swagger:
    restart: "unless-stopped"
    image: swaggerapi/swagger-ui:v5.17.14
    ports:
      - "127.0.0.1:9010:8080"
    volumes:
      - ./whisper/openapi.yaml:/openapi.yaml
    environment:
      SWAGGER_JSON: /openapi.yaml
```

После включения по адресу http://localhost:9010 будет доступен следующего вида интерфейс:

![Swagger UI](./assets/whisper-swagger.png)

### Эндпоинты

#### /inference

Транскрибируем аудиофайл:

```shell
curl http://localhost:9000/inference \
  -H "Content-Type: multipart/form-data" \
  -F file="@<file-path>" \
  -F language="auto" \
  -F response_format="json"
```

Вместо `language="auto"` (автоопределение языка аудио) вы можете явно передать нужный, например `language="ru"`.

Вместо `response_format="json"` можно попросить систему вернуть субтитры `response_format="srt"` или просто
текст `response_format="text"`.

#### /load

Сменить модель Whisper:

```shell
curl http://localhost:9000/load \
  -H "Content-Type: multipart/form-data" \
  -F model="<path-to-model-file-in-docker-container>"
```

### Переменные окружения

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

### Квантизация

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

В случае если передать целое число скрипт
entrypoint.sh [автоматически](https://github.com/EvilFreelancer/docker-whisper-server/blob/main/whisper/entrypoint.sh#L20-L36)
преобразует его в соответствующую комбинацию символов вида `qX_X`.

Подробнее о [квантизации](https://github.com/ggerganov/whisper.cpp/tree/master?tab=readme-ov-file#quantization) в
документации проекта whisper.cpp.

## OpenAI-like API-сервер

Этот сервис представляет собой обёртку вокруг нескольких Whisper.cpp серверов, запущенных по сети. Он маршрутизирует
запросы на сервер соответствующей модели.

```yaml
  server:
    restart: "unless-stopped"
    build:
      context: ./server
    volumes:
      - ./config.yml/app/config.yaml
    ports:
      - "127.0.0.1:5000:5000"
```

### Пример config.yml

Конфигурация сервера и список доступных моделей настраивается в файле `config.yml`, по умолчанию имеет следующий вид:

```yaml
models:
  base:
    owned_by: organization-owner
    endpoints:
      - base_url: http://whisper:9000/inference
  #tiny:
  #  owned_by: organization-tiny-owner
  #  endpoints:
  #    - base_url: http://whisper01:9000/inference
  #    - base_url: https://user:pass@remote-server:9000/inference
```

В конфигурации можно указать несколько моделей и серверов для каждой модели, в случае если модель доступна на нескольких
адреса в момент запроса будет выбираться случайный сервер и запрос перенавится на него.

### Swagger документация сервера

Сервис `server-swagger` предоставляет визуализацию и документацию всех доступных эндпоинтов.

```yaml
  server-swagger:
    restart: "unless-stopped"
    image: swaggerapi/swagger-ui:v5.17.14
    ports:
      - "127.0.0.1:5010:8080"
    volumes:
      - ./server/openapi.yaml:/openapi.yaml
    environment:
      SWAGGER_JSON: /openapi.yaml
```

После включения по адресу http://localhost:5010 будет доступен следующего вида интерфейс:

![Swagger UI](./assets/server-swagger.png)

### Эндпоинты

#### /audio/transcriptions

Этот эндпоинт используется для создания транскрипции аудиофайла в исходном языке.

Метод: `POST`

Параметры запроса:

* **file** (обязательный): Аудиофайл для транскрипции. Поддерживаются
  форматы: `flac`, `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `ogg`, `wav`, или `webm`.
* **model** (обязательный): ID модели, которая будет использоваться для транскрипции.
* language (опционально): Язык аудиофайла в формате [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).
  Передача этого параметра может улучшить точность и скорость распознавания.
* prompt (опционально): Дополнительный текст, который может помочь модели в транскрипции или продолжить предыдущий
  сегмент аудио.
* response_format (опционально): Формат вывода транскрипции. Возможные значения: `json`, `text`, `srt`, `verbose_json`
  и `vtt`. По умолчанию: `json`.
* temperature (опционально): Температура выборки, значение от `0` до `1`. Более высокие значения, такие как `0.8`,
  сделают результат более случайным, а более низкие значения, такие как `0.2`, сделают его более фокусированным и
  детерминированным. Если установлено значение `0`, модель будет автоматически увеличивать температуру до достижения
  определённых порогов.

Пример запроса:

```shell
curl http://localhost:5000/audio/transcriptions \
  -H "Content-Type: multipart/form-data" \
  -F file="@./assets/audio.mp3" \
  -F model="base" \
  -F language="ru" \
  -F response_format="json"
```

Пример ответа:

```json
{
  "text": "This is the transcription of the audio."
}
```

#### /audio/translations

Этот эндпоинт используется для перевода аудиофайла на английский язык.

Работает один в один как `/audio/transcriptions` только `language=en` и его нельзя менять.

Пример запроса:

```shell
curl http://localhost:5000/audio/transcriptions \
  -H "Content-Type: multipart/form-data" \
  -F file="@./assets/audio.mp3" \
  -F model="base" \
  -F response_format="json"
```

Пример ответа:

```json
{
  "text": "This is the translated transcription of the audio."
}
```

#### /models

Этот эндпоинт используется для получения списка всех доступных моделей.

Метод: `GET`

Пример запроса:

```shell
curl http://localhost:5000/models
```

Пример ответа:

```json
{
  "object": "list",
  "data": [
    {
      "id": "base",
      "object": "model",
      "created": 1686935002,
      "owned_by": "organization-owner"
    }
  ]
}
```

#### /models/{model}

Этот эндпоинт используется для получения информации о конкретной модели.

Метод: `GET`

Параметры пути:

* model (обязательный): ID модели, о которой нужно получить информацию.

Пример запроса:

```shell
curl http://localhost:5000/models/base
```

Пример ответа:

```json
{
  "id": "base",
  "object": "model",
  "created": 1686935002,
  "owned_by": "organization-owner"
}
```

## Ссылки

Whisper.cpp

- https://github.com/ggerganov/whisper.cpp
- https://github.com/ggerganov/whisper.cpp/tree/master/examples/server

OpenAI-like API

- https://platform.openai.com/docs/api-reference/audio/createTranscription
- https://platform.openai.com/docs/api-reference/audio/createTranslation
- https://platform.openai.com/docs/api-reference/models/list
- https://platform.openai.com/docs/api-reference/models/retrieve

## Цитирование

Если вы используете этот проект в своих исследованиях или работе, пожалуйста, укажите ссылку на него следующим образом:

```text
[Pavel Rykov]. (2024). Whisper.cpp API Webserver in Docker. GitHub. https://github.com/EvilFreelancer/docker-whisper-server
```

Альтернатива в формате BibTeX:

```text
@misc{pavelrykov2024whisperapi,
  author = {Pavel Rykov},
  title  = {Whisper.cpp API Webserver in Docker},
  year   = {2024},
  url    = {https://github.com/EvilFreelancer/docker-whisper-server}
}
```

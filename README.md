# Whisper.cpp API Webserver in Docker

HTTP-сервер транскрипции Whisper.cpp с API, подобным OpenAI, в Docker.

Этот проект содержит в себе набор инструментов и конфигураций для сборки
Docker-контейнер с сервером транскрипции, основанным
на [whisper.cpp](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server).

**Русский** | [English](./README.en.md)

## Возможности

- Docker-контейнер с HTTP-сервером транскрипции Whisper.cpp
- Настраивается через переменные окружения
- Автоматически конвертирует аудио в формат WAV
- Автоматически загружает выбранную модель при запуске
- Может квантовать любую модель Whisper до нужного типа при запуске

## Требования

Перед началом убедитесь, что на вашей машине установлена карточка с GPU, поддерживающим современную CUDA, из-за
вычислительных требований Docker-образа.

* Nvidia GPU
* CUDA
* Docker
* Docker Compose
* Nvidia Docker Runtime

Для подробных инструкций по подготовке Linux-машины к запуску нейросетей, включая установку CUDA, Docker и Nvidia Docker
Runtime, обратитесь к моей публикации
"[Как подготовить Linux к запуску и обучению нейросетей? (+ Docker)](https://dzen.ru/a/ZVt9kRBCTCGlQqyP)".

## Установка

1. Склонируем репозиторий, после чего перейдём в корень исходников:

   ```shell
   git clone https://github.com/EvilFreelancer/docker-whisper-server.git
   cd docker-whisper-server

2. Скопируем конфигурацию Docker Compose из шаблона:

   ```shell
   cp docker-compose.dist.yml docker-compose.yml
   ```

   В конфиге вы можете настроить переменные окружения, версию whisper.cpp, порты, подключаемы тома и так далее.

3. Cобираем Docker-образ:
   
   ```shell
   docker-compose build
   ```
### /load

Сменить модель Whisper:

```shell
curl 127.0.0.1:9000/load \
   -H "Content-Type: multipart/form-data" \
   -F model="<path-to-model-file-in-docker-container>"
```

## Переменные окружения

### Базовая конфигурация


| Name                         | Default                               | Description                                                                   |
|------------------------------|---------------------------------------|-------------------------------------------------------------------------------|
| `WHISPER_MODEL`              | base.en                               | Модель Whisper, используемая по умолчанию                                     |
| `WHISPER_MODEL_PATH`         | /app/models/ggml-${WHISPER_MODEL}.bin | Путь к файлу модели Whisper по умолчанию                                      |
| `WHISPER_MODEL_QUANTIZATION` |                                       | Уровень квантования (применяется только если `WHISPER_MODEL_PATH` не изменен) |

<details>
<summary>
<i>Advanced Configuration</i>
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

## Ссылки

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- [пример сервера](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server) whisper.cpp

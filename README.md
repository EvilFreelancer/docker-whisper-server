# Whisper.cpp API Webserver in Docker

Whisper.cpp HTTP transcription server with OAI-like API in Docker.

## Overview

This project provides a Dockerized transcription server based
on [whisper.cpp](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server).
It uses Whisper models to transcribe audio files via an HTTP API, similar to OpenAI's API.

## Features

- HTTP server for audio transcription
- Support for various Whisper models
- Configurable via environment variables
- Dockerized for easy deployment
- Includes ffmpeg for audio processing
- Automatically converts audio to WAV format

## Installation

1. Copy the provided Docker Compose template:

```shell
cp docker-compose.dist.yml docker-compose.yml
```

2. Build the Docker images:

```shell
docker-compose build
```

3. Start the services:

```shell
docker-compose up -d
```

## Endpoints

### /transcribe

Transcribe an audio file:

```shell
curl 127.0.0.1:9000/transcribe \
-H "Content-Type: multipart/form-data" \
-F file="@<file-path>" \
-F temperature="0.0" \
-F temperature_inc="0.2" \
-F response_format="json"
```
### /load

Load a new Whisper model:

```shell
curl 127.0.0.1:9000/load \
-H "Content-Type: multipart/form-data" \
-F model="<path-to-model-file-in-docker-container>"
```

## Environment variables

| Name                         | Default                               | Description                                                                      |
|------------------------------|---------------------------------------|----------------------------------------------------------------------------------|
| `WHISPER_MODEL`              | base.en                               | The default Whisper model to use                                                 |
| `WHISPER_MODEL_PATH`         | /app/models/ggml-${WHISPER_MODEL}.bin | The default path to the Whisper model file                                       |
| `WHISPER_MODEL_QUANTIZATION` |                                       | Level of quantization (will be applied only if `WHISPER_MODEL_PATH` not changed) |
| `WHISPER_THREADS`            | 4                                     | Number of threads to use for inference                                           |
| `WHISPER_PROCESSORS`         | 1                                     | Number of processors to use for inference                                        |
| `WHISPER_HOST`               | 0.0.0.0                               | Host IP or hostname to bind the server to                                        |
| `WHISPER_PORT`               | 9000                                  | Port number to listen on                                                         |
| `WHISPER_INFERENCE_PATH`     | /transcribe                           | Path to load inference models from                                               |
| `WHISPER_PUBLIC_PATH`        |                                       | Path to the public folder                                                        |
| `WHISPER_REQUEST_PATH`       |                                       | Request path for all requests                                                    |
| `WHISPER_OV_E_DEVICE`        | CPU                                   | OpenViBE Event Device to use                                                     |
| `WHISPER_OFFSET_T`           | 0                                     | Time offset in milliseconds                                                      |
| `WHISPER_OFFSET_N`           | 0                                     | Number of seconds to offset                                                      |
| `WHISPER_DURATION`           | 0                                     | Duration of the audio file in milliseconds                                       |
| `WHISPER_MAX_CONTEXT`        | -1                                    | Maximum context size for inference                                               |
| `WHISPER_MAX_LEN`            | 0                                     | Maximum length of output text                                                    |
| `WHISPER_BEST_OF`            | 2                                     | Best-of-N strategy for inference                                                 |
| `WHISPER_BEAM_SIZE`          | -1                                    | Beam size for search                                                             |
| `WHISPER_AUDIO_CTX`          | 0                                     | Audio context to use for inference                                               |
| `WHISPER_WORD_THOLD`         | 0.01                                  | Word threshold for segmentation                                                  |
| `WHISPER_ENTROPY_THOLD`      | 2.40                                  | Entropy threshold for segmentation                                               |
| `WHISPER_LOGPROB_THOLD`      | -1.00                                 | Log probability threshold for segmentation                                       |
| `WHISPER_LANGUAGE`           | en                                    | Language code to use for translation or diarization                              |
| `WHISPER_PROMPT`             |                                       | Initial prompt                                                                   |
| `WHISPER_DTW`                |                                       | Compute token-level timestamps                                                   |
| `WHISPER_CONVERT`            | true                                  | Convert audio to WAV, requires ffmpeg on the server                              |
| `WHISPER_SPLIT_ON_WORD`      | false                                 | Boolean flag to split output on words                                            |
| `WHISPER_DEBUG_MODE`         | false                                 | Enable debug mode                                                                |
| `WHISPER_TRANSLATE`          | false                                 | Translate from source language to english                                        |
| `WHISPER_DIARIZE`            | false                                 | Stereo audio diarization                                                         |
| `WHISPER_TINYDIARIZE`        | false                                 | Enable tinydiarize (requires a tdrz model)                                       |
| `WHISPER_NO_FALLBACK`        | false                                 | Do not use temperature fallback while decoding                                   |
| `WHISPER_PRINT_SPECIAL`      | false                                 | Print special tokens                                                             |
| `WHISPER_PRINT_COLORS`       | false                                 | Print colors                                                                     |
| `WHISPER_PRINT_REALTIME`     | false                                 | Print output in realtime                                                         |
| `WHISPER_PRINT_PROGRESS`     | false                                 | Print progress                                                                   |
| `WHISPER_NO_TIMESTAMPS`      | false                                 | Do not print timestamps                                                          |
| `WHISPER_DETECT_LANGUAGE`    | false                                 | Exit after automatically detecting language                                      |

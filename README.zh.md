# Whisper.cpp API Webserver in Docker

Whisper.cpp HTTP 语音转录服务器，类似 OpenAI 的 API，运行在 Docker 中。

该项目包含一组工具和配置，用于构建基于 [whisper.cpp](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server)
的 Docker 容器转录服务器。

[Русский](./README.md) | **中文** | [English](./README.en.md)

## 功能

- Docker 容器化的 Whisper.cpp HTTP 语音转录服务器
- 通过环境变量进行配置
- 自动将音频转换为 WAV 格式
- 启动时自动下载所需的模型
- 启动时可以将任何 Whisper 模型量化到所需类型

## 要求

在开始之前，请确保您的机器上安装了支持现代 CUDA 的 GPU，由于 Docker 镜像的计算需求较高。

* Nvidia GPU
* CUDA
* Docker
* Docker Compose
* Nvidia Docker Runtime

有关如何准备运行神经网络的 Linux 机器的详细说明，包括 CUDA、Docker 和 Nvidia Docker Runtime
的安装，请参考我的文章 "[如何准备 Linux 以运行和训练神经网络？（包括 Docker）](https://dzen.ru/a/ZVt9kRBCTCGlQqyP)"。

## 安装

1. 克隆代码库，然后进入源代码根目录：

    ```shell
    git clone https://github.com/EvilFreelancer/docker-whisper-server.git
    cd docker-whisper-server
    ```

2. 从模板复制 Docker Compose 配置：

    ```shell
    cp docker-compose.dist.yml docker-compose.yml
    ```

   在配置文件中，您可以配置环境变量、whisper.cpp 版本、端口、挂载卷等。

3. 构建 Docker 镜像：

    ```shell
    docker-compose build
    ```

4. 启动服务：

   ```shell
   docker-compose up -d
   ```

5. 在浏览器中访问 http://localhost:8080：

   ![Swagger UI](./assets/swagger.png)

## 接口

### /inference

转录音频文件：

```shell
curl 127.0.0.1:9000/inference \
  -H "Content-Type: multipart/form-data" \
  -F file="@<file-path>" \
  -F temperature="0.0" \
  -F temperature_inc="0.2" \
  -F response_format="json"
```

### /load

加载新的 Whisper 模型：

```shell
curl 127.0.0.1:9000/load \
   -H "Content-Type: multipart/form-data" \
   -F model="<path-to-model-file-in-docker-container>"
```

## 环境变量

### 基本配置

| 名称                           | 默认值                                   | 描述                                   |
|------------------------------|---------------------------------------|--------------------------------------|
| `WHISPER_MODEL`              | base.en                               | 默认使用的 Whisper 模型                     |
| `WHISPER_MODEL_PATH`         | /app/models/ggml-${WHISPER_MODEL}.bin | Whisper 模型文件的默认路径                    |
| `WHISPER_MODEL_QUANTIZATION` |                                       | 量化级别（仅在 `WHISPER_MODEL_PATH` 未更改时适用） |

<details>
<summary>
<i>高级配置</i>
</summary>

| 名称                        | 默认值        | 描述                         |
|---------------------------|------------|----------------------------|
| `WHISPER_THREADS`         | 4          | 用于推理的线程数                   |
| `WHISPER_PROCESSORS`      | 1          | 用于推理的处理器数                  |
| `WHISPER_HOST`            | 0.0.0.0    | 绑定服务器的 IP 地址或主机名           |
| `WHISPER_PORT`            | 9000       | 监听的端口号                     |
| `WHISPER_INFERENCE_PATH`  | /inference | 所有推理请求的路径                  |
| `WHISPER_PUBLIC_PATH`     |            | 公共文件夹的路径                   |
| `WHISPER_REQUEST_PATH`    |            | 所有请求的路径                    |
| `WHISPER_OV_E_DEVICE`     | CPU        | 使用的 OpenViBE 事件设备          |
| `WHISPER_OFFSET_T`        | 0          | 时间偏移（毫秒）                   |
| `WHISPER_OFFSET_N`        | 0          | 时间偏移（秒）                    |
| `WHISPER_DURATION`        | 0          | 音频文件的持续时间（毫秒）              |
| `WHISPER_MAX_CONTEXT`     | -1         | 推理的最大上下文大小                 |
| `WHISPER_MAX_LEN`         | 0          | 输出文本的最大长度                  |
| `WHISPER_BEST_OF`         | 2          | 推理的 "最佳 N 选择" 策略           |
| `WHISPER_BEAM_SIZE`       | -1         | 搜索的光束大小                    |
| `WHISPER_AUDIO_CTX`       | 0          | 用于推理的音频上下文                 |
| `WHISPER_WORD_THOLD`      | 0.01       | 分段的单词阈值                    |
| `WHISPER_ENTROPY_THOLD`   | 2.40       | 分段的熵阈值                     |
| `WHISPER_LOGPROB_THOLD`   | -1.00      | 分段的对数概率阈值                  |
| `WHISPER_LANGUAGE`        | en         | 用于翻译或对话分段的语言代码             |
| `WHISPER_PROMPT`          |            | 初始提示                       |
| `WHISPER_DTW`             |            | 计算基于 token 的时间戳            |
| `WHISPER_CONVERT`         | true       | 将音频转换为 WAV，需要服务器上安装 ffmpeg |
| `WHISPER_SPLIT_ON_WORD`   | false      | 按单词而不是 token 分割输出          |
| `WHISPER_DEBUG_MODE`      | false      | 启用调试模式                     |
| `WHISPER_TRANSLATE`       | false      | 从源语言翻译成英语                  |
| `WHISPER_DIARIZE`         | false      | 立体声音频分段                    |
| `WHISPER_TINYDIARIZE`     | false      | 启用 tinydiarize（需要 tdrz 模型） |
| `WHISPER_NO_FALLBACK`     | false      | 解码时不使用温度后备选项               |
| `WHISPER_PRINT_SPECIAL`   | false      | 打印特殊 token                 |
| `WHISPER_PRINT_COLORS`    | false      | 打印颜色                       |
| `WHISPER_PRINT_REALTIME`  | false      | 实时打印输出                     |
| `WHISPER_PRINT_PROGRESS`  | false      | 打印进度                       |
| `WHISPER_NO_TIMESTAMPS`   | false      | 不打印时间戳                     |
| `WHISPER_DETECT_LANGUAGE` | false      | 自动检测语言后退出                  |

</details>

## 链接

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- [whisper.cpp 服务器示例](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server)

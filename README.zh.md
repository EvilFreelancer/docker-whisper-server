# Whisper.cpp API Webserver in Docker

Whisper.cpp HTTP 服务器，用于自动语音识别 (ASR)，API 类似于 OpenAI 的接口，运行在 Docker 容器中。

该项目包含构建带有基于 [whisper.cpp](https://github.com/ggerganov/whisper.cpp/tree/master/examples/server) 的转录服务器的
Docker 容器的工具和配置。

[Русский](./README.md) | **中文** | [English](./README.en.md)

## 功能

- 包含 Whisper.cpp 转录 HTTP 服务器的 Docker 容器
- 可通过环境变量进行配置
- 自动将音频转换为 WAV 格式
- 启动时自动下载所选模型（如果不存在）
- 启动时可量化任意 Whisper 模型到所需级别

## 要求

Docker 容器分两阶段构建，首先是使用基础镜像 `nvidia/cuda:12.5.1-devel-ubuntu22.04`，在其中编译 `server` 和 `quantize`
二进制文件，然后在第二阶段使用镜像 `nvidia/cuda:12.5.1-runtime-ubuntu22.04`，在其中安装必要的包并复制在第一阶段编译的二进制文件。

理论上，如果将 `nvidia/cuda` 镜像版本降到 `12.1`，应该不会有问题，但尚未测试。

因此，在开始之前，请确保您的系统中安装了支持现代 CUDA 的 GPU，并且已安装最新的 CUDA 驱动程序。

因此，项目运行需要：

* Nvidia 显卡 >= GTX 10xx（或同等）
* CUDA >= 12.5（可能 12.1 也可以）
* Docker
* Docker Compose
* Nvidia Docker Runtime

有关如何准备 Linux 机器以运行神经网络，包括安装 CUDA、Docker 和 Nvidia Docker Runtime
的详细说明，请参阅我的文章 "[如何准备 Linux 以运行和训练神经网络？（包括 Docker）](https://dzen.ru/a/ZVt9kRBCTCGlQqyP)"。

## 安装

1. 克隆仓库，然后进入源码根目录：

    ```shell
    git clone https://github.com/EvilFreelancer/docker-whisper-server.git
    cd docker-whisper-server
    ```

2. 从模板复制 Docker Compose 配置：

    ```shell
    cp docker-compose.dist.yml docker-compose.yml
    ```

   在配置中，您可以设置环境变量、whisper.cpp 的版本、端口、挂载的卷等。

   例如，可以从 `master` 分支构建服务器，并在运行时使用量化到 `q4_0` 的 `base` 模型，在 `1` 个处理器和 `4` 个线程上运行。

   ```yaml
   version: "3.9"
   services:
     restart: "unless-stopped"
     whisper:
       build:
         context: ./whisper
         args:
           # 版本可以是：tag、分支或提交哈希
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

3. 构建 Docker 镜像：

    ```shell
    docker-compose build
    ```

4. 启动 Docker 容器：

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
  -F language="auto" \
  -F response_format="json"
```

可以将 `language="auto"`（自动检测音频语言）替换为所需的语言，例如 `language="zh"`。

可以将 `response_format="json"` 替换为请求系统返回字幕 `response_format="srt"` 或纯文本 `response_format="text"`。

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

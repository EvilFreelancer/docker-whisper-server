## Enpoints



## Environment variables

| Name                    | Default                               | Description                                         |
|-------------------------|---------------------------------------|-----------------------------------------------------|
| WHISPER_MODEL           | base.en                               | The default Whisper model to use                    |
| WHISPER_MODEL_PATH      | /app/models/ggml-${WHISPER_MODEL}.bin | The path to the Whisper model file                  |
| WHISPER_THREADS         | 4                                     | Number of threads to use for inference              |
| WHISPER_PROCESSORS      | 1                                     | Number of processors to use for inference           |
| WHISPER_HOST            | 0.0.0.0                               | Host IP or hostname to bind the server to           |
| WHISPER_PORT            | 9000                                  | Port number to listen on                            |
| WHISPER_INFERENCE_PATH  | /transcribe                           | Path to load inference models from                  |
| WHISPER_PUBLIC_PATH     |                                       | Path to the public folder                           |
| WHISPER_OV_E_DEVICE     | CPU                                   | OpenViBE Event Device to use                        |
| WHISPER_OFFSET_T        | 0                                     | Time offset in milliseconds                         |
| WHISPER_OFFSET_N        | 0                                     | Number of seconds to offset                         |
| WHISPER_DURATION        | 0                                     | Duration of the audio file in milliseconds          |
| WHISPER_MAX_CONTEXT     | -1                                    | Maximum context size for inference                  |
| WHISPER_MAX_LEN         | 0                                     | Maximum length of output text                       |
| WHISPER_BEST_OF         | 2                                     | Best-of-N strategy for inference                    |
| WHISPER_BEAM_SIZE       | -1                                    | Beam size for search                                |
| WHISPER_AUDIO_CTX       | 0                                     | Audio context to use for inference                  |
| WHISPER_WORD_THOLD      | 0.01                                  | Word threshold for segmentation                     |
| WHISPER_ENTROPY_THOLD   | 2.40                                  | Entropy threshold for segmentation                  |
| WHISPER_LOGPROB_THOLD   | -1.00                                 | Log probability threshold for segmentation          |
| WHISPER_LANGUAGE        | en                                    | Language code to use for translation or diarization |
| WHISPER_PROMPT          |                                       | Prompt text for generation                          |
| WHISPER_DTW             |                                       | Compute token-level timestamps                      |
| WHISPER_REQUEST_PATH    |                                       | Request path for all requests                       |
| WHISPER_SPLIT_ON_WORD   | false                                 | Boolean flag to split output on words               |
| WHISPER_DEBUG_MODE      | false                                 | Boolean flag to enable debug mode                   |
| WHISPER_TRANSLATE       | false                                 | Boolean flag to translate text                      |
| WHISPER_DIARIZE         | false                                 | Boolean flag to diarize audio                       |
| WHISPER_TINYDIARIZE     | false                                 | Boolean flag to tiny-diarianze audio                |
| WHISPER_NO_FALLBACK     | false                                 | Boolean flag to disable fallbacks                   |
| WHISPER_PRINT_SPECIAL   | false                                 | Boolean flag to print special characters            |
| WHISPER_PRINT_COLORS    | false                                 | Boolean flag to print colors                        |
| WHISPER_PRINT_REALTIME  | false                                 | Boolean flag to print real-time information         |
| WHISPER_PRINT_PROGRESS  | false                                 | Boolean flag to print progress updates              |
| WHISPER_NO_TIMESTAMPS   | false                                 | Boolean flag to disable timestamps                  |
| WHISPER_DETECT_LANGUAGE | false                                 | Boolean flag to detect language automatically       |
| WHISPER_CONVERT         | false                                 | Boolean flag to convert text                        |

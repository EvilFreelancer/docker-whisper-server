#!/bin/bash

# Default values
WHISPER_MODEL=${WHISPER_MODEL:-"base.en"}
WHISPER_MODEL_PATH=${WHISPER_MODEL_PATH:-"/app/models/ggml-${WHISPER_MODEL}.bin"}
WHISPER_HOST=${WHISPER_HOST:-"0.0.0.0"}
WHISPER_PORT=${WHISPER_PORT:-"9000"}
WHISPER_REQUEST_PATH=${WHISPER_REQUEST_PATH:-""}
WHISPER_PUBLIC_PATH=${WHISPER_PUBLIC_PATH:-""}
WHISPER_INFERENCE_PATH=${WHISPER_INFERENCE_PATH:-"/transcribe"}
WHISPER_CONVERT=${WHISPER_CONVERT:-"true"}
WHISPER_THREADS=${WHISPER_THREADS:-"4"}
WHISPER_PROCESSORS=${WHISPER_PROCESSORS:-"1"}

# Function to convert boolean-like strings to bash true/false
to_boolean() {
  case "$1" in
    [Yy][Ee][Ss]|[Yy]|[Tt][Rr][Uu][Ee]|1) echo "true" ;;
    *) echo "false" ;;
  esac
}

# Check if the model file exists, if not, download it
if [ ! -f "$WHISPER_MODEL_PATH" ]; then
  echo "Model not found at $WHISPER_MODEL_PATH. Downloading model..."
  [ ! -f "/app/models/download-ggml-model.sh" ] && cp -v /app/download-ggml-model.sh /app/models/
  bash /app/models/download-ggml-model.sh "$WHISPER_MODEL"
fi

# Construct the command with the options
CMD="./server"
CMD+=" --model $WHISPER_MODEL_PATH"

# Basic parameters
[ -n "$WHISPER_THREADS" ]         && CMD+=" --threads $WHISPER_THREADS"
[ -n "$WHISPER_PROCESSORS" ]      && CMD+=" --processors $WHISPER_PROCESSORS"
[ -n "$WHISPER_HOST" ]            && CMD+=" --host $WHISPER_HOST"
[ -n "$WHISPER_PORT" ]            && CMD+=" --port $WHISPER_PORT"
[ -n "$WHISPER_INFERENCE_PATH" ]  && CMD+=" --inference-path $WHISPER_INFERENCE_PATH"
[ -n "$WHISPER_PUBLIC_PATH" ]     && CMD+=" --public $WHISPER_PUBLIC_PATH"
[ -n "$WHISPER_OV_E_DEVICE" ]     && CMD+=" --ov-e-device $WHISPER_OV_E_DEVICE"

# Optional parameters
[ -n "$WHISPER_OFFSET_T" ]        && CMD+=" --offset-t $WHISPER_OFFSET_T"
[ -n "$WHISPER_OFFSET_N" ]        && CMD+=" --offset-n $WHISPER_OFFSET_N"
[ -n "$WHISPER_DURATION" ]        && CMD+=" --duration $WHISPER_DURATION"
[ -n "$WHISPER_MAX_CONTEXT" ]     && CMD+=" --max-context $WHISPER_MAX_CONTEXT"
[ -n "$WHISPER_MAX_LEN" ]         && CMD+=" --max-len $WHISPER_MAX_LEN"
[ -n "$WHISPER_BEST_OF" ]         && CMD+=" --best-of $WHISPER_BEST_OF"
[ -n "$WHISPER_BEAM_SIZE" ]       && CMD+=" --beam-size $WHISPER_BEAM_SIZE"
[ -n "$WHISPER_AUDIO_CTX" ]       && CMD+=" --audio-ctx $WHISPER_AUDIO_CTX"
[ -n "$WHISPER_WORD_THOLD" ]      && CMD+=" --word-thold $WHISPER_WORD_THOLD"
[ -n "$WHISPER_ENTROPY_THOLD" ]   && CMD+=" --entropy-thold $WHISPER_ENTROPY_THOLD"
[ -n "$WHISPER_LOGPROB_THOLD" ]   && CMD+=" --logprob-thold $WHISPER_LOGPROB_THOLD"
[ -n "$WHISPER_LANGUAGE" ]        && CMD+=" --language $WHISPER_LANGUAGE"
[ -n "$WHISPER_PROMPT" ]          && CMD+=" --prompt $WHISPER_PROMPT"
[ -n "$WHISPER_DTW" ]             && CMD+=" --dtw $WHISPER_DTW"
[ -n "$WHISPER_REQUEST_PATH" ]    && CMD+=" --request-path $WHISPER_REQUEST_PATH"

# Boolean flags
[ "$(to_boolean "$WHISPER_SPLIT_ON_WORD")" = "true" ]   && CMD+=" --split-on-word"
[ "$(to_boolean "$WHISPER_DEBUG_MODE")" = "true" ]      && CMD+=" --debug-mode"
[ "$(to_boolean "$WHISPER_TRANSLATE")" = "true" ]       && CMD+=" --translate"
[ "$(to_boolean "$WHISPER_DIARIZE")" = "true" ]         && CMD+=" --diarize"
[ "$(to_boolean "$WHISPER_TINYDIARIZE")" = "true" ]     && CMD+=" --tinydiarize"
[ "$(to_boolean "$WHISPER_NO_FALLBACK")" = "true" ]     && CMD+=" --no-fallback"
[ "$(to_boolean "$WHISPER_PRINT_SPECIAL")" = "true" ]   && CMD+=" --print-special"
[ "$(to_boolean "$WHISPER_PRINT_COLORS")" = "true" ]    && CMD+=" --print-colors"
[ "$(to_boolean "$WHISPER_PRINT_REALTIME")" = "true" ]  && CMD+=" --print-realtime"
[ "$(to_boolean "$WHISPER_PRINT_PROGRESS")" = "true" ]  && CMD+=" --print-progress"
[ "$(to_boolean "$WHISPER_NO_TIMESTAMPS")" = "true" ]   && CMD+=" --no-timestamps"
[ "$(to_boolean "$WHISPER_DETECT_LANGUAGE")" = "true" ] && CMD+=" --detect-language"
[ "$(to_boolean "$WHISPER_CONVERT")" = "true" ]         && CMD+=" --convert"

# Execute the command
echo "Executing command: $CMD"
exec $CMD

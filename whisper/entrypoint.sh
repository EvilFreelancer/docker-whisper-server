#!/bin/bash

# Model defaults
WHISPER_MODEL=${WHISPER_MODEL:-"base"}
DEFAULT_MODEL_PATH="/app/models/ggml-${WHISPER_MODEL}.bin"
WHISPER_MODEL_PATH=${WHISPER_MODEL_PATH:-$DEFAULT_MODEL_PATH}
WHISPER_MODEL_QUANTIZATION=${WHISPER_MODEL_QUANTIZATION:-""}

# System defaults
WHISPER_HOST=${WHISPER_HOST:-"0.0.0.0"}
WHISPER_PORT=${WHISPER_PORT:-"9000"}
WHISPER_REQUEST_PATH=${WHISPER_REQUEST_PATH:-""}
WHISPER_PUBLIC_PATH=${WHISPER_PUBLIC_PATH:-""}
WHISPER_INFERENCE_PATH=${WHISPER_INFERENCE_PATH:-"/inference"}
WHISPER_CONVERT=${WHISPER_CONVERT:-"true"}
WHISPER_THREADS=${WHISPER_THREADS:-"4"}
WHISPER_PROCESSORS=${WHISPER_PROCESSORS:-"1"}

# Detect quantization type and convert to text if number has been provided
validate_quantization_type() {
    case $1 in
        10) echo "q2_k" ;;
        11) echo "q3_k" ;;
        2)  echo "q4_0" ;;
        3)  echo "q4_1" ;;
        12) echo "q4_k" ;;
        8)  echo "q5_0" ;;
        9)  echo "q5_1" ;;
        13) echo "q5_k" ;;
        14) echo "q6_k" ;;
        7)  echo "q8_0" ;;
        q2_k | q3_k | q4_0 | q4_1 | q4_k | q5_0 | q5_1 | q5_k | q6_k | q8_0)
            echo "$1" ;;
        *)  echo "Invalid type" ;;
    esac
}

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
  cp -v /app/download-ggml-model.sh /app/models/
  bash /app/models/download-ggml-model.sh "$WHISPER_MODEL"
fi

# If quantization level is set
if [ -n "$WHISPER_MODEL_QUANTIZATION" ]; then
  QUANTIZATION_TYPE=$(validate_quantization_type "$WHISPER_MODEL_QUANTIZATION")

  # Break if quantization type is not valid
  if [ "$QUANTIZATION_TYPE" == "Invalid type" ]; then
    echo "Invalid quantization type provided: $WHISPER_MODEL_QUANTIZATION"
    exit 1
  fi

  # Generate quantization type
  QUANTIZED_MODEL_PATH="/app/models/ggml-${WHISPER_MODEL}-${QUANTIZATION_TYPE}.bin"

  # Check if file of quantized model is already exists
  if [ ! -f "$QUANTIZED_MODEL_PATH" ]; then
    echo "Quantized model not found at $QUANTIZED_MODEL_PATH. Quantizing model..."
    /app/quantize "$WHISPER_MODEL_PATH" "$QUANTIZED_MODEL_PATH" "$QUANTIZATION_TYPE"
  fi

  # Replace path from default model to quantized version
  WHISPER_MODEL_PATH="$QUANTIZED_MODEL_PATH"
fi

# Construct the command with the options
CMD="./whisper-server"
CMD+=" --model $WHISPER_MODEL_PATH"
CMD+=" -mc 0"

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
[ "true" = "$(to_boolean "$WHISPER_SPLIT_ON_WORD")" ]   && CMD+=" --split-on-word"
[ "true" = "$(to_boolean "$WHISPER_DEBUG_MODE")" ]      && CMD+=" --debug-mode"
[ "true" = "$(to_boolean "$WHISPER_TRANSLATE")" ]       && CMD+=" --translate"
[ "true" = "$(to_boolean "$WHISPER_DIARIZE")" ]         && CMD+=" --diarize"
[ "true" = "$(to_boolean "$WHISPER_TINYDIARIZE")" ]     && CMD+=" --tinydiarize"
[ "true" = "$(to_boolean "$WHISPER_NO_FALLBACK")" ]     && CMD+=" --no-fallback"
[ "true" = "$(to_boolean "$WHISPER_PRINT_SPECIAL")" ]   && CMD+=" --print-special"
[ "true" = "$(to_boolean "$WHISPER_PRINT_COLORS")" ]    && CMD+=" --print-colors"
[ "true" = "$(to_boolean "$WHISPER_PRINT_REALTIME")" ]  && CMD+=" --print-realtime"
[ "true" = "$(to_boolean "$WHISPER_PRINT_PROGRESS")" ]  && CMD+=" --print-progress"
[ "true" = "$(to_boolean "$WHISPER_NO_TIMESTAMPS")" ]   && CMD+=" --no-timestamps"
[ "true" = "$(to_boolean "$WHISPER_DETECT_LANGUAGE")" ] && CMD+=" --detect-language"
[ "true" = "$(to_boolean "$WHISPER_CONVERT")" ]         && CMD+=" --convert"

# Execute the command
echo && echo "Executing command: $CMD" && echo
exec $CMD

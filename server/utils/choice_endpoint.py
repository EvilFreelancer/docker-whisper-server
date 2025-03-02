import random
import subprocess
import re
from utils import get_logger
from pynvml import (
    nvmlInit,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetCount,
    nvmlShutdown,
)

_log = get_logger()

def detect_gpus():
    """Определяет установленные в системе видеокарты."""
    try:
        result = subprocess.run(
            ["lspci"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            _log.error(f"Ошибка при выполнении lspci: {result.stderr}")
            return []

        gpus = []
        for line in result.stdout.split('\n'):
            if 'VGA compatible controller' in line or '3D controller' in line:
                if 'NVIDIA' in line:
                    gpus.append({"vendor": "NVIDIA", "name": line})
                elif 'AMD' in line or 'ATI' in line:
                    gpus.append({"vendor": "AMD", "name": line})
                elif 'Intel' in line:
                    gpus.append({"vendor": "Intel", "name": line})
        return gpus
    except Exception as e:
        _log.error(f"Ошибка определения видеокарт: {e}")
        return []

def get_nvidia_gpu_utilization(index):
    """Получает загрузку NVIDIA GPU через NVML."""
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(index)
        utilization = nvmlDeviceGetUtilizationRates(handle)
        nvmlShutdown()
        return utilization.gpu
    except Exception as e:
        _log.error(f"Ошибка получения загрузки NVIDIA GPU: {e}")
        return random.randint(0, 100)

def get_amd_gpu_utilization():
    """Получает загрузку AMD GPU через rocm-smi."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showuse"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            _log.error(f"Ошибка при выполнении rocm-smi: {result.stderr}")
            return []

        gpu_loads = []
        for line in result.stdout.split('\n'):
            match = re.search(r'GPU\s+(\d+).*?(\d+)%', line)
            if match:
                gpu_index = int(match.group(1))
                load = int(match.group(2))
                gpu_loads.append({"gpu": f"AMD-{gpu_index}", "load": load})
        return gpu_loads
    except Exception as e:
        _log.error(f"Ошибка получения загрузки AMD GPU: {e}")
        return []


def get_intel_gpu_utilization():
    """Получает загрузку Intel GPU через intel_gpu_top."""
    try:
        result = subprocess.run(
            ["intel_gpu_top", "-J"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            _log.error(f"Ошибка при выполнении intel_gpu_top: {result.stderr}")
            return []
        import json
        data = json.loads(result.stdout)
        engines = data.get('engines', [])
        gpu_load = 0
        for engine in engines:
            if 'busy' in engine:
                gpu_load += engine['busy']
        gpu_load = (gpu_load / len(engines)) * 100 if engines else 0
        return [{"gpu": "Intel-0", "load": gpu_load}]
    except Exception as e:
        _log.error(f"Ошибка получения загрузки Intel GPU: {e}")
    return []


def get_all_gpu_utilization():
    """Определяет все видеокарты и получает их загрузку."""
    gpus = detect_gpus()
    gpu_loads = []

    for index, gpu in enumerate(gpus):
        if gpu['vendor'] == 'NVIDIA':
            load = get_nvidia_gpu_utilization(index)
            gpu_loads.append({"gpu": f"NVIDIA-{index}", "load": load if load is not None else random.randint(0, 100)})
        elif gpu['vendor'] == 'AMD':
            amd_loads = get_amd_gpu_utilization()
            gpu_loads.extend(amd_loads if amd_loads else [{"gpu": f"AMD-{i}", "load": random.randint(0, 100)} for i in range(len(amd_loads))])
        elif gpu['vendor'] == 'Intel':
            intel_loads = get_intel_gpu_utilization()
            gpu_loads.extend(intel_loads if intel_loads else [{"gpu": "Intel-0", "load": random.randint(0, 100)}])
        else:
            _log.warning(f"Неизвестный производитель GPU: {gpu['vendor']}")

    return gpu_loads

def get_least_loaded_server(local_servers, gpu_loads):
    """Выбирает сервер с минимальной загрузкой GPU."""
    if not gpu_loads:
        _log.warning("Не удалось получить загрузку GPU, выбираем случайный локальный сервер.")
        return random.choice(local_servers)

    gpu_dict = {gpu['gpu']: gpu['load'] for gpu in gpu_loads}
    available_servers = [
        s for s in local_servers
        if f"NVIDIA-{s['gpu']}" in gpu_dict or f"AMD-{s['gpu']}" in gpu_dict or f"Intel-{s['gpu']}" in gpu_dict
    ]

    if not available_servers:
        _log.error("Ошибка: нет доступных локальных серверов после фильтрации по GPU.")
        return random.choice(local_servers)

    min_load_server = min(
        available_servers,
        key=lambda ep: gpu_dict.get(f"NVIDIA-{ep['gpu']}", gpu_dict.get(f"AMD-{ep['gpu']}", gpu_dict.get(f"Intel-{ep['gpu']}", 100)))
    )
    _log.info(f"Выбран сервер с минимальной загрузкой: {min_load_server['base_url']} (GPU {min_load_server['gpu']})")
    return min_load_server


def select_best_server(endpoints):
    """Выбираем оптимальный сервер на основе загрузки GPU и вероятности."""
    local_servers = [ep for ep in endpoints if 'gpu' in ep]  # Серверы с GPU
    cloud_servers = [ep for ep in endpoints if 'gpu' not in ep]  # Облачные серверы

    if not local_servers and not cloud_servers:
        _log.error("Нет доступных серверов.")
        return None

    if not local_servers:  # Если нет локальных серверов, выбираем облачный
        _log.info("Нет локальных серверов, используем облачный сервер.")
        return random.choice(cloud_servers)

    if not cloud_servers:  # Если нет облачных серверов, выбираем локальный
        _log.info("Нет облачных серверов, используем локальный сервер.")
        return get_least_loaded_server(local_servers)

    # Определяем веса для выбора между локальными и облачными серверами
    weights = [len(local_servers), len(cloud_servers)]
    server_type = random.choices(['local', 'cloud'], weights=weights, k=1)[0]

    if server_type == 'local':
        _log.info("Выбор локального сервера.")
        return get_least_loaded_server(local_servers, get_all_gpu_utilization())
    else:
        _log.info("Выбор облачного сервера.")
        return random.choice(cloud_servers)


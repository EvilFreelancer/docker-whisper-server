import random
import subprocess
from utils import get_logger

_log = get_logger()

def get_gpu_utilization():
    """Получаем загрузку GPU с помощью nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            _log.error(f"Ошибка при выполнении nvidia-smi: {result.stderr}")
            return None

        gpu_loads = result.stdout.strip().split("\n")

        # Проверяем, что список не пуст и все элементы являются числами
        if not gpu_loads or any(not item.isdigit() for item in gpu_loads):
            _log.error(f"Некорректный вывод nvidia-smi: {gpu_loads}")
            return None

        return list(map(int, gpu_loads))

    except Exception as e:
        _log.error(f"Ошибка получения данных GPU: {e}")
        return None

def get_least_loaded_server(local_servers, gpu_loads):
    """Выбирает сервер с минимальной загрузкой GPU."""
    if gpu_loads is None:
        _log.warning("Не удалось получить загрузку GPU, выбираем случайный локальный сервер.")
        return random.choice(local_servers)

    # Проверяем, что gpu_loads содержит достаточно элементов
    available_gpus = len(gpu_loads)
    local_servers = [s for s in local_servers if s['gpu'] < available_gpus]

    if not local_servers:
        _log.error("Ошибка: нет доступных локальных серверов после фильтрации по GPU.")
        return random.choice(local_servers)

    min_load_server = min(local_servers, key=lambda ep: gpu_loads[ep['gpu']])
    _log.info(
        f"Выбран сервер с минимальной загрузкой: {min_load_server['base_url']} (GPU {min_load_server['gpu']})"
    )
    return min_load_server

def select_best_server(endpoints):
    """Выбираем оптимальный сервер на основе загрузки GPU и вероятности."""

    local_servers = [ep for ep in endpoints if 'gpu' in ep]  # Серверы с GPU
    cloud_servers = [ep for ep in endpoints if 'gpu' not in ep]  # Облачные серверы

    if not local_servers:  # Если нет локальных серверов, выбираем облачный
        _log.info("Нет локальных серверов, используем облачный сервер.")
        return random.choice(cloud_servers)

    gpu_loads = get_gpu_utilization()

    if not cloud_servers:  # Если нет облачных серверов, выбираем сервер с минимальной загрузкой GPU
        _log.info("Нет облачных серверов, выбираем локальный сервер на основе загрузки GPU.")
        return get_least_loaded_server(local_servers, gpu_loads)

    # вероятность выбрать локальный сервер
    if random.randint(0, 99) < (len(local_servers) / (len(local_servers) + len(cloud_servers)) * 100):
        _log.info("Выбор локального сервера.")
        return get_least_loaded_server(local_servers, gpu_loads)

    _log.info("Выбор облачного сервера.")
    return random.choice(cloud_servers)

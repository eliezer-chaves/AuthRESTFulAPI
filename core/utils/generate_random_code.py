import random
import time

def generate_reset_code():
    # Usa a hora atual como semente para maior aleatoriedade
    random.seed(time.time_ns())
    # Gera um número aleatório de 6 dígitos (100000 a 999999)
    return str(random.randint(100000, 999999))


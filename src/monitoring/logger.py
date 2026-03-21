import logging
from logging.handlers import RotatingFileHandler
import os

# Criar diretório de logs se não existir
os.makedirs("logs", exist_ok=True)

# Formato detalhado com contexto
log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"

# Configurar logger root
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Handler para arquivo com rotação (máx 5MB por arquivo, 5 arquivos históricos)
file_handler = RotatingFileHandler(
    "logs/fiap_tech_challenge_phase_3.log",
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(log_format, log_date_format))
root_logger.addHandler(file_handler)

# Handler para console (desenvolvimento)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format, log_date_format))
root_logger.addHandler(console_handler)
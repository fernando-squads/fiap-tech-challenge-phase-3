from src.monitoring import logging
from src.dataset.download_and_prepare_datasets import download_pubmedqa, process_pubmedqa, download_medquad, process_medquad, unify_datasets

logger = logging.getLogger(__name__)

download_pubmedqa()
pubmedqa_data = process_pubmedqa()

download_medquad()
medquad_data = process_medquad()

unify_datasets(pubmedqa_data, medquad_data)

logger.info(f"Finalizando geração de dataset")
# model/embedding.py

from sentence_transformers import SentenceTransformer
import config
import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import logging
logging.set_verbosity_error()

from sentence_transformers import SentenceTransformer
import logging as py_logging
py_logging.getLogger("sentence_transformers").setLevel(py_logging.ERROR)


# ✅ 全局只加载一次
model = SentenceTransformer(config.MODELS)

def encode(text):
    return model.encode(text).tolist()
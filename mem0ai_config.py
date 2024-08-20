from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from typenv import Env

env = Env()
env.read_env()

vector_config = {
    "provider": env.str(name="VECTOR_STORE_PROVIDER", default="qdrant"),
    "config": {
        "host": env.str(name="VECTOR_STORE_SERVER_HOST"),
        "port": env.int(name="VECTOR_STORE_SERVER_PORT"),
        "path": env.str("VECTOR_STORE_QDRANT_PATH", default=None),
        "api_key": env.str("VECTOR_STORE_API_KEY", default=None),
        "on_disk": env.bool("VECTOR_STORE_QDRANT_ON_DISK", default=False),
        "embedding_model_dims": env.int(name="VECTOR_STORE_EMBEDDING_MODEL_DIMS", default=1536)
    }
}

llm_config = LlmConfig(
    provider="openai",
    config={
        "model": env.str("OPENAI_MODEL")
    }
).dict()

embedding_config = EmbedderConfig(
    provider="openai",
    config={
        "model": env.str("OPENAI_EMBEDDING_MODEL")
    }
).dict()



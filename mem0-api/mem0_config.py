import os
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from typenv import Env

env = Env()
env.read_env()

vector_config = {
    "provider": env.str(name="VECTOR_STORE_PROVIDER", default="qdrant"),
    "config": {
        "url": f"http://{env.str(name='VECTOR_STORE_DB_HOST')}:{env.str(name='VECTOR_STORE_DB_PORT')}",  # Note: if http is not specified, https will be required by default, while qdrant does not enable tls by default
        "port": env.int(name='VECTOR_STORE_DB_PORT', default=6333),
        "api_key": env.str("VECTOR_STORE_DB_API_KEY", default=None),
        "embedding_model_dims": env.int(name="VECTOR_STORE_EMBEDDING_MODEL_DIMS", default=384),
        "collection_name": env.str("VECTOR_STORE_COLLECTION_NAME", default="mem0")
    }
}

llm_config = LlmConfig(
    provider=env.str("LLM_PROVIDER", default="deepseek"),
    config={
        "model": env.str("LLM_MODEL", default="deepseek-chat"),
        "temperature": env.float("TEMPERATURE"),
        "max_tokens": env.int("MAX_TOKENS"),
        "top_p": env.float("TOP_P")
    }
).dict()

# Learn more: https://docs.mem0.ai/components/embedders/models/huggingface
embedding_config = EmbedderConfig(
    provider="huggingface",
    config={
        "model": "multi-qa-MiniLM-L6-cos-v1"
    }
).dict()



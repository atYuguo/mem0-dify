import dotenv
from typenv import Env
from fastapi import status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from typing_extensions import TypedDict
from mem0 import Memory
from mem0_config import vector_config, llm_config, embedding_config
from errors.exception import UnauthorizedException, DatabaseConnectionError
from qdrant_client.http.exceptions import ResponseHandlingException

dotenv.load_dotenv()

env = Env()

authorization_scheme = HTTPBearer(auto_error=False)


class MemoryHistory(TypedDict):
    is_deleted: bool


# delay initialization mem0
_mem0 = None

def get_mem0():
    global _mem0
    if _mem0 is None:
        try:
            _mem0 = Memory.from_config({
                "vector_store": vector_config,
                "llm": llm_config,
                "embedder": embedding_config
            })
        except ResponseHandlingException as e:
            if "timed out" in str(e):
                raise DatabaseConnectionError()
            raise
    return _mem0


def get_memory_id(
        memory_id: str = None,
):
    if memory_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="memory_id cannot be None")

    mem0 = get_mem0()
    memory_histories: List[MemoryHistory] = mem0.history(memory_id=memory_id)

    if len(memory_histories) == 0 or memory_histories[-1].get("is_deleted"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Memory {memory_id} not found')

    return memory_id


def authorize(token: Optional[HTTPAuthorizationCredentials] = Depends(authorization_scheme)):
    auth_key = env.str("MEM0_API_AUTH_KEY", default="")
    if auth_key == "" or (token is not None and token.credentials == auth_key):
        pass
    else:
        raise UnauthorizedException()

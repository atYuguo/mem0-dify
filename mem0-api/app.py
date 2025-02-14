import uvicorn
import time
import sys
import os
import asyncio
from pathlib import Path

from fastapi import FastAPI, APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typenv import Env
from pydantic import BaseModel, Field
from typing import Dict, Union, List
from dependencies import get_memory_id, MemoryHistory, authorize, get_mem0
from response import SuccessfulResponse, ErrorResponse
from mem0_config import vector_config, llm_config, embedding_config, graph_config
from errors.exception import UnauthorizedException, DatabaseConnectionError
from errors.handler import (
    unauthorized_exception_handler, 
    qdrant_client_unexpected_handler, 
    database_connection_error_handler, 
    database_request_error_handler,
    response_handling_exception_handler
)
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException

ROOT_DIR = Path(__file__).parent.parent

env = Env()
# read .env from project root directory
env.read_env(os.path.join(ROOT_DIR, '.env'))

app = FastAPI(
    title="Mem0 to API",
    description="A RESTful API service for managing longterm memory storage and retrieval operations. This API provides endpoints for storing, updating, searching, and managing longterm memory entries with support for user-specific and agent-specific operations.",
    servers=[
        {
            "url": f"http://{env.str('MEM0_API_HOST')}:{env.int('MEM0_API_PORT', default=8000)}",
            "description": "Memory API Server"
        }
    ]
)

api_router = APIRouter(
    tags=["mem0"]
)


class StoreMemoryData(BaseModel):
    """Request model for storing a new memory entry.
    This model defines the structure for creating new memory entries with support for various metadata and filtering options.
    Learn more: https://docs.mem0.ai/api-reference/memory/add-memories
    """
    data: str = Field(description="The content or text to be stored as a memory. This is the primary content that will be vectorized and stored. Example: 'The user asked about improving code performance.'")
    user_id: Union[str, None] = Field(default=None, description="Optional identifier for the user associated with this memory. Used for user-specific memory management and retrieval. Example: 'user_123'")
    agent_id: Union[str, None] = Field(default=None, description="Optional identifier for the AI agent associated with this memory. Useful for tracking which AI agent generated or processed this memory. Example: 'agent_gpt4'")
    run_id: Union[str, None] = Field(default=None, description="Optional identifier for tracking specific execution runs. Helps in grouping related memories from the same interaction session. Example: 'run_20230615_001'")
    metadata: Union[dict, None] = Field(default=None, description="Optional metadata to store with the memory. Can include any additional structured information about the memory. Example: {'source': 'chat', 'importance': 'high', 'tags': ['performance', 'code'], 'context': {'session_id': '123', 'timestamp': '2023-06-15T10:30:00Z'}}")
    filters: Union[Dict, None] = Field(default=None, description="Optional filtering criteria for memory retrieval. Supports complex nested structures for advanced filtering. Example: {'category': 'technical', 'date': '2023-06-15', 'tags': {'$in': ['performance', 'code']}, 'importance': {'$gte': 'medium'}, 'custom_field': {'$exists': true}}")
    prompt: Union[str, None] = Field(default=None, description="Optional prompt text that generated this memory. Useful for tracking the context that led to this memory's creation. Example: 'How can I improve my code performance?'")


@api_router.get("/authorized", description="Check authorization status")
def authorized(token=Depends(authorize)):
    return SuccessfulResponse()


@api_router.post(
    path="/store",
    description="Create a new memory.",
    response_model=SuccessfulResponse
)
async def store_memory(data: StoreMemoryData, token=Depends(authorize)):
    mem0 = get_mem0()
    execute_results = mem0.add(
        messages=data.data,
        user_id=data.user_id,
        agent_id=data.agent_id,
        run_id=data.run_id,
        metadata=data.metadata,
        filters=data.filters,
        prompt=data.prompt
    )
    return SuccessfulResponse(
        data=execute_results
    )


class UpdateMemoryData(BaseModel):
    """Request model for updating a memory entry.
    
    This model defines the structure for updating existing memory entries, allowing modification of content and metadata.
    Learn more: https://docs.mem0.ai/api-reference/memory/update-memory
    """
    data: str = Field(description="The new content or text to update the memory with. This will replace the existing content. Example: 'Updated information about code performance.'")
    metadata: Union[dict, None] = Field(default=None, description="Optional metadata to update with the memory. Can be used to add or update additional structured information. Example: {'importance': 'high', 'tags': ['updated', 'performance'], 'last_modified': '2023-06-15T10:30:00Z'}")
    filters: Union[Dict, None] = Field(default=None, description="Optional filtering criteria for memory retrieval. Supports complex nested structures for advanced filtering. Example: {'category': 'technical', 'status': 'updated', 'tags': {'$in': ['performance']}, 'importance': {'$gte': 'high'}}")
    timestamp: Union[str, None] = Field(default=None, description="Optional timestamp for when the memory was updated. Should be in ISO 8601 format. Example: '2023-06-15T10:30:00Z'")

@api_router.put(
    path="/update/{memory_id}",
    description="Update a memory by ID."
)
async def update_memory(
        data: UpdateMemoryData,
        memory_id: str = Depends(get_memory_id),
        token=Depends(authorize)
):
    mem0 = get_mem0()
    execute_result = mem0.update(
        memory_id=memory_id,
        data=data.data
    )
    return SuccessfulResponse(
        data=execute_result
    )


class SearchMemoryData(BaseModel):
    """Request model for searching stored memories.
    
    This model provides comprehensive search capabilities with support for various filtering and sorting options.
    Learn more: https://docs.mem0.ai/api-reference/memory/v2-search-memories
    """
    query: str = Field(description="The search query text to match against stored memories. Supports semantic search using embeddings. Example: 'code performance tips'")
    user_id: Union[str, None] = Field(default=None, description="Filter results by specific user ID. Useful for retrieving user-specific memories. Example: 'user_123'")
    agent_id: Union[str, None] = Field(default=None, description="Filter results by specific agent ID. Helps in finding memories created by a particular AI agent. Example: 'agent_gpt4'")
    run_id: Union[str, None] = Field(default=None, description="Filter results by specific run ID. Useful for retrieving memories from a specific interaction session. Example: 'run_20230615_001'")
    limit: Union[int, None] = Field(default=10, ge=1, le=100, description="Maximum number of results to return. Range: 1-100. Default: 10. Example: 20")
    filters: Union[dict, None] = Field(default=None, description="Additional filtering criteria for the search. Supports complex nested queries with operators. Example: {'category': 'technical', 'date_range': {'$gte': '2023-01-01', '$lte': '2023-12-31'}, 'importance': {'$in': ['high', 'medium']}, 'tags': {'$all': ['performance', 'optimization']}, 'custom_field': {'$exists': true}}")


@api_router.post(
    path="/search",
    description="Search for memories.",
    dependencies=[Depends(authorize)]
)
async def search_memories(
        data: SearchMemoryData
):
    mem0 = get_mem0()
    memories = mem0.search(
        **data.model_dump()
    )
    return SuccessfulResponse(
        data=memories
    )


@api_router.get(
    path="/retrieve",
    description="List all memories.",
    dependencies=[Depends(authorize)]
)
async def retrieve_memories(
        user_id: Union[str, None] = None,
        agent_id: Union[str, None] = None,
        run_id: Union[str, None] = None,
        limit: Union[int, None] = 100
):
    """Retrieve all memories with optional filtering by user, agent, or run ID.
    
    Parameters:
    - user_id: Optional filter to retrieve memories for a specific user
    - agent_id: Optional filter to retrieve memories created by a specific AI agent
    - run_id: Optional filter to retrieve memories from a specific execution run
    - limit: Maximum number of memories to return (default: 100)
    """
    mem0 = get_mem0()
    memories = mem0.get_all(
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        limit=limit
    )

    return SuccessfulResponse(
        data=memories
    )


@api_router.get(
    path="/retrieve/{memory_id}",
    description="Get the history of changes for a memory by ID."
)
async def retrieve_memory(
        memory_id: str = Depends(get_memory_id),
        token=Depends(authorize)
):
    mem0 = get_mem0()
    memory = mem0.history(memory_id=memory_id)
    return SuccessfulResponse(
        data=memory
    )


@api_router.delete(
    path="/delete/{memory_id}",
    description="Delete a memory by ID."
)
async def delete_memory(
        memory_id: str = Depends(get_memory_id),
        token=Depends(authorize)
):
    try:
        mem0 = get_mem0()
        # Get memory history records
        memory_histories: List[MemoryHistory] = mem0.history(memory_id=memory_id)
        
        # If no history records or last record shows deletion, return 404
        if not memory_histories or memory_histories[-1] is None or memory_histories[-1].get("is_deleted"):
            return JSONResponse(
                content=ErrorResponse(
                    code=status.HTTP_404_NOT_FOUND,
                    error="NotFoundError",
                    message=f"Memory {memory_id} not found or already deleted."
                ).model_dump(),
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # If checks passed, proceed with deletion
        try:
            delete_result = mem0.delete(memory_id=memory_id)
            # mem0.delete() returns None on success
            if delete_result is None:
                return SuccessfulResponse()
            return SuccessfulResponse(data=delete_result)
        
        except AttributeError as e:
            # If NoneType error occurs, likely means memory doesn't exist in database
            if "NoneType" in str(e):
                return JSONResponse(
                    content=ErrorResponse(
                        code=status.HTTP_404_NOT_FOUND,
                        error="NotFoundError",
                        message=f"Memory {memory_id} not found in the database."
                    ).model_dump(),
                    status_code=status.HTTP_404_NOT_FOUND
                )
            # Handle other AttributeError cases
            return JSONResponse(
                content=ErrorResponse(
                    code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    error="InvalidMemoryError",
                    message=f"Invalid memory object: {str(e)}"
                ).model_dump(),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    except Exception as e:
        # Handle unexpected errors
        return JSONResponse(
            content=ErrorResponse(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error="DeletionError",
                message=f"Unexpected error while deleting memory {memory_id}: {str(e)}"
            ).model_dump(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_router.delete(
    path="/delete-all",
    description="Delete all memories matching the specified criteria."
)
async def delete_memory(
        user_id: Union[str, None] = None,
        agent_id: Union[str, None] = None,
        run_id: Union[str, None] = None,
        token=Depends(authorize)
):
    """Delete all memories that match the specified filtering criteria.
    
    Parameters:
    - user_id: Optional filter to delete memories for a specific user
    - agent_id: Optional filter to delete memories created by a specific AI agent
    - run_id: Optional filter to delete memories from a specific execution run
    """
    try:
        mem0 = get_mem0()
        mem0.delete_all(
            user_id, agent_id, run_id
        )

        return SuccessfulResponse()
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="ValueError",
                message=e
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@api_router.delete(
    path="/reset-all",
    description="Reset the memory store."
)
async def reset_all_memories(token=Depends(authorize)):
    mem0 = get_mem0()
    mem0.reset()
    return JSONResponse(
        content=SuccessfulResponse().model_dump_json(),
        status_code=status.HTTP_202_ACCEPTED
    )


@api_router.get("/health", description="Check service health status")
async def health_check():
    try:
        mem0 = get_mem0()
        # Test database connection
        mem0.vector_store.client.get_collections()
        return SuccessfulResponse(data={
            "status": "healthy",
            "database": "connected",
            "message": "Service is running normally"
        })
    except ResponseHandlingException as e:
        if "timed out" in str(e):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=ErrorResponse(
                    code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    error="DatabaseConnectionTimeout",
                    message="Database connection timed out. Please check network connectivity."
                ).dict()
            )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
                error="HealthCheckFailed",
                message=f"Service is unhealthy: {str(e)}"
            ).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
                error="HealthCheckFailed",
                message=f"Service is unhealthy: {str(e)}"
            ).dict()
        )


def check_database_connection():
    """Check database connection status"""
    try:
        mem0 = get_mem0()
        mem0.vector_store.client.get_collections()
        return True, None
    except Exception as e:
        return False, str(e)

def wait_for_database(max_retries=None):
    """Wait for database connection to be ready"""
    retry_count = 0
    while True:
        print("Checking database connection...")
        is_connected, error = check_database_connection()
        
        if is_connected:
            print("✓ Database connection successful!")
            return True
        
        retry_count += 1
        if max_retries and retry_count >= max_retries:
            print(f"✗ Database connection failed, maximum retry count {max_retries} reached")
            print(f"错误信息: {error}")
            return False
            
        print(f"✗ Database connection failed: {error}")
        print("Will retry in 10 seconds...")
        time.sleep(10)


app.include_router(api_router)
app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
app.add_exception_handler(UnexpectedResponse, qdrant_client_unexpected_handler)
app.add_exception_handler(ConnectionError, database_connection_error_handler)
app.add_exception_handler(Exception, database_request_error_handler)
app.add_exception_handler(ResponseHandlingException, response_handling_exception_handler)

if __name__ == "__main__":
    try:
        port = env.int('MEM0_API_PORT', default=8000)
        uvicorn.run(
            "app:app",
            host="0.0.0.0",  # listening on all interfaces
            port=port,
            reload=True
        )
    except Exception as e:
        print(f"Failed to start service: {str(e)}")
        raise

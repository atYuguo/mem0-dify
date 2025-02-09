Integrate Mem0 to Dify, bring Dify a long-term memory function. 

## Background

Mem0 is a project that extracts and stores long-term memories from conversations, providing the following capabilities:

- Storing memories of any unstructured text
- Updating memories for a given `memory_id`
- Retrieving memories based on queries
- Returning memories for a specific user/agent/session
- Describing the change history of a specific `memory_id`

It also supports using common vector databases and graph databases as memory storage.
Unfortunately, the Mem0 community edition does not provide a Web API or a Dify plugin.

This project aims to solve the above problems, enabling Dify to better support long-term memory, and to reflect, summarize and refine chat content.

## Core Features

### Memory Management

- Store Memory: Save important information from conversations
- Update Memory: Modify existing memory content
- Retrieve Memory: Search for relevant memories based on similarity
- Track Memory: View the change history of a specific memory
- Context Association: Support memory management at the user/agent/session level

**Features:**

- Based on Docker Compose for quick deployment of Mem0 API and vector database.

## Directory Structure

```
.
├── mem0-api/         # Mem0 API service directory
│
├── db/             # Various databases
│   ├── qdrant/     # qdrant database
│   └── ......     # Other databases
│
├── refs/             # Third-party interface documentation directory, convenient for AI Coding
│
├── .env.example     # Example of environment variable configuration
├── pyproject.toml     # Poetry project configuration
└── README.md         # Project documentation
```

## Installation Steps

### Install Mem0 API

Enter the project directory, copy `.env.example` to `.env`, and modify the configuration.
Run:

```
docker compose up
```

### Use in Dify

API documentation: http://MEM0_API_HOST:MEM0_API_PORT/docs

Open Dify - Tools - Custom - Create Custom Tool:

- Schema: Select Import from URL: http://MEM0_API_HOST:MEM0_API_PORT/openapi.json.
- Authentication method: Select API Key, authentication header as Bearer, key as Authorization, and value as EM0_API_AUTH_KEY.
- In Workflow, add a node, select Tools - Custom, and each interface you just created is an independent tool.

Usage Suggestions:

- Writing memories can be slow. It is recommended to query memories first, and write memories in parallel branches.
- The input of the Write Memory node does not contain dialogue context by default, and needs to be added manually.
- Therefore, a Memory Classification and Reasoning LLM node can be added before the write node to: classify and tag memories, combine dialogue context for reflection and reasoning, and tag. Replace pronouns. Filter unnecessary memories and improve performance.

## References

- [Mem0 - Github](https://github.com/mem0ai/mem0)
- [Mem0 - Docs ](https://docs.mem0.ai/overview)
- [Qdrant - Docs](https://qdrant.tech/documentation/)

## Acknowledgements

This project integrates the following code:

- [API for Dify plugin for Mem0](https://github.com/tonori/mem0ai-api) by [tonori](https://github.com/tonori)

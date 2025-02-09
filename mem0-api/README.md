## File Description

`.cache` Stores downloaded model files, such as those from Hugging Face.

## Running

### Running the Entire Project

In the project root directory, simply run `docker compose up`.

### Running mem0-api Independently via Code

```
cd mem0-api
pip install poetry
# [Optional] Set poetry source to add mirror sources from Aliyun and Tsinghua
poetry source add aliyun https://mirrors.aliyun.com/pypi/simple/
poetry source add tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/
# [Optional] Set timeout to 600 seconds
export POETRY_HTTP_TIMEOUT=600
# Install only the main dependencies, minimizing the dependency set
poetry install --only main --no-root
poetry run python app.py
```

#### [Optional] Building as a System Service

First, modify the absolute paths and other configurations in `mem0-api.service`. Then:

```
# Copy the service file
sudo cp mem0-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mem0-api.service
# Start the service
sudo systemctl start mem0-api.service
# Check if the service output is normal
sudo journalctl -u mem0-api.service -f
```

## Using in Dify

API documentation: http://MEM0_API_HOST:MEM0_API_PORT/docs

Open Dify - Tools - Custom - Create Custom Tool:

- Schema: Select Import from URL: http://MEM0_API_HOST:MEM0_API_PORT/openapi.json.
- Authentication method: Select API Key, authentication header as Bearer, key as Authorization, and value as EM0_API_AUTH_KEY.
- In Workflow, add a node, select Tools - Custom. Each interface you just created is an independent tool.

Usage Suggestions:

- Writing memories can be slow. It is recommended to query memories first, and write memories in parallel branches.
- The input of the Write Memory node does not contain dialogue context by default and needs to be added manually.
- Therefore, a Memory Classification and Reasoning LLM node can be added before the write node to: classify and tag memories, combine dialogue context for reflection and reasoning, and tag. Replace pronouns. Filter unnecessary memories and improve performance.

## 文件说明
.cache  存储下载的HuggingFace等模型文件

## 运行
### 通过项目整体运行
在项目根目录 docker compose up 即可

### 通过代码单独运行mem0-api
```
cd mem0-api
pip install poetry
# [可选]设置 poetry 源添加阿里云、清华的镜像源
poetry source add aliyun https://mirrors.aliyun.com/pypi/simple/
poetry source add tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/
# [可选]超时设置为600秒
export POETRY_HTTP_TIMEOUT=600  
# 只安装主依赖，最小化依赖集合
poetry install --only main --no-root
poetry run python app.py
```

#### [可选]构建成系统服务 
先修改 mem0-api.service 中绝对路径等配置，然后：  
```
# 复制服务文件
sudo cp mem0-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mem0-api.service
# 启动服务
sudo systemctl start mem0-api.service
# 查看服务输出是否正常
sudo journalctl -u mem0-api.service -f
```

## 在Dify中使用
接口文档：http://MEM0_API_HOST:MEM0_API_PORT/docs   

打开 Diy - 工具 - 自定义 - 创建自定义工具：
- Schema选择从URL中导入： http://MEM0_API_HOST:MEM0_API_PORT/openapi.json 。
- 鉴权方法：选API Key，鉴权头部为 Bearer，键 Authorization，值为 EM0_API_AUTH_KEY。  
- 在Workflow中，添加节点，选 工具 - 自定义， 刚创建的每个接口都是个独立的工具。  

使用建议：  
- 写入记忆 会比较慢，建议先 查询记忆，同时在并行的支线写入记忆。 
- 写入记忆 节点的输入，默认不含对话上下文，需要手动添加。  
- 故在写入节点之前，可以加一个 记忆分类及推理 LLM节点，从而：对记忆进行分类、打标签，结合对话上下文进行反思推理，打标签。对代词进行替换。过滤不需要的记忆，提升性能。  


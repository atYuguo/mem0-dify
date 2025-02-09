将Mem0整合到Dify，为Dify带来长期记忆功能。

## 背景
Mem0 是一个从对话中提取、存储长期记忆的项目，提供了以下能力：
- 存储任意非结构化文本的记忆
- 更新给定memory_id的记忆
- 根据查询获取记忆
- 返回特定用户/代理/会话的记忆
- 描述特定memory_id的记忆变更历史

也支持使用常见向量数据库，以及图数据库，做为记忆存储。
但是很可惜，Mem0社区版没有提供Web API，也没有Dify插件。

本项目就是为了解决上述问题，让Dify更好支持长期记忆，以及对聊天内容进行反思、总结与提炼。    
## 核心功能
### 记忆管理
- 存储记忆：保存对话中的重要信息
- 更新记忆：修改已存在的记忆内容
- 检索记忆：基于相似度搜索相关记忆
- 记忆追踪：查看特定记忆的变更历史
- 上下文关联：支持用户/代理/会话级别的记忆管理

**特性：**
- 基于Docker Compose，快速部署Mem0 API和向量数据库。

## 目录结构
.
├── mem0-api/               # Mem0 API服务目录   
│     
├── db/                     # 各类数据库  
│   ├── qdrant/             # qdrant数据库  
│   └── ......              # 其他数据库  
│  
├── refs/                   # 三方接口文档目录，方便 AI Coding  
│  
├── .env.example            # 环境变量配置示例  
├── pyproject.toml          # Poetry项目配置  
└── README.md               # 项目说明文档  

## 安装步骤
### 安装Mem0 API
进入项目目录，将 .env.example 复制为 .env，并修改配置。  
运行：  
```
docker compose up
```
### 在Dify中使用
接口文档：http://MEM0_API_HOST:MEM0_API_PORT/docs   

打开 Diy - 工具 - 自定义 - 创建自定义工具：
- Schema选择从URL中导入： http://MEM0_API_HOST:MEM0_API_PORT/openapi.json 。
- 鉴权方法：选API Key，鉴权头部为 Bearer，键 Authorization，值为 EM0_API_AUTH_KEY。  
- 在Workflow中，添加节点，选 工具 - 自定义， 刚创建的每个接口都是个独立的工具。  

使用建议：  
- 写入记忆 会比较慢，建议先 查询记忆，同时在并行的支线写入记忆。 
- 写入记忆 节点的输入，默认不含对话上下文，需要手动添加。  
- 故在写入节点之前，可以加一个 记忆分类及推理 LLM节点，从而：对记忆进行分类、打标签，结合对话上下文进行反思推理，打标签。对代词进行替换。过滤不需要的记忆，提升性能。 

## 参考
- [Mem0 - Github](https://github.com/mem0ai/mem0)
- [Mem0 - Docs ](https://docs.mem0.ai/overview)
- [Qdrant - Docs](https://qdrant.tech/documentation/)

## 致谢
本项目整合了以下代码：
- [针对Mem0的Dify插件的API](https://github.com/tonori/mem0ai-api)，作者：[tonori](https://github.com/tonori)

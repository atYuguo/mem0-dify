## 文件说明
.data/  存储数据库记录
.snapshots/ 存储快照

## 运行
### 通过项目整体运行
在项目根目录 docker compose up 即可

### 单独运行qdrant
在 db/qdrant 运行 ./run-docker.sh


## 使用
Web管理页：
http://localhost:6333/dashboard
需要输入配置的 MEM0_API_AUTH_KEY 进行登录认证。
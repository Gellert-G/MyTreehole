# 我的树洞 - 匿名社交应用

一个基于 Flask 的匿名社交应用，用户可以匿名发表言论、点赞、收藏、评论和搜索。

## 功能特性

- 用户注册和登录
- 匿名发表言论（最多200字）
- 点赞和收藏言论
- 评论互动
- 搜索言论
- 个人中心（查看我的发表和收藏）
- 删除自己的言论

## 技术栈

- 后端：Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- 数据库：SQLite
- 前端：HTML5, CSS3, JavaScript, Bootstrap 5
- 交互：AJAX

## 项目结构

```
todo/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models.py            # 数据库模型
│   ├── forms.py             # 表单类
│   ├── auth/                # 认证蓝图
│   │   └── __init__.py
│   ├── main/                # 主蓝图
│   │   └── __init__.py
│   └── profile/             # 个人中心蓝图
│       └── __init__.py
├── static/
│   ├── css/
│   │   └── style.css        # 自定义样式
│   └── js/
│       └── main.js          # JavaScript交互
├── templates/
│   ├── base.html            # 基础模板
│   ├── index.html           # 首页
│   ├── search.html          # 搜索结果页
│   ├── auth/
│   │   ├── login.html       # 登录页
│   │   └── register.html    # 注册页
│   └── profile/
│       ├── index.html       # 个人中心
│       ├── posts.html       # 我的发表
│       └── favorites.html   # 我的收藏
├── config.py                # 配置文件
├── requirements.txt          # 依赖包
├── run.py                   # 启动文件
└── README.md                # 项目说明
```

## 安装和运行

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python run.py
```

应用将在 `http://127.0.0.1:5000/` 启动。

## 使用说明

1. 访问首页，点击"注册"创建账号
2. 使用用户名和密码登录
3. 登录后可以发表言论（最多200字）
4. 对其他用户的言论进行点赞、收藏或评论
5. 使用搜索框查找感兴趣的言论
6. 在个人中心查看自己的发表和收藏
7. 可以删除自己发表的言论

## 数据库模型

### User（用户）
- id: 主键
- username: 用户名（唯一）
- password_hash: 密码哈希
- created_at: 创建时间

### Post（言论）
- id: 主键
- content: 言论内容
- user_id: 作者ID
- created_at: 创建时间
- likes: 点赞数
- favorites: 收藏数

### Like（点赞关联）
- user_id: 用户ID
- post_id: 言论ID

### Favorite（收藏关联）
- user_id: 用户ID
- post_id: 言论ID

### Comment（评论）
- id: 主键
- content: 评论内容
- user_id: 评论者ID
- post_id: 言论ID
- created_at: 创建时间

## API 端点

### 认证
- `GET /auth/register` - 注册页面
- `POST /auth/register` - 处理注册
- `GET /auth/login` - 登录页面
- `POST /auth/login` - 处理登录
- `GET /auth/logout` - 登出

### 言论
- `GET /` - 首页
- `POST /post` - 发布言论
- `POST /post/<id>/like` - 点赞/取消点赞
- `POST /post/<id>/favorite` - 收藏/取消收藏
- `POST /post/<id>/comment` - 评论
- `POST /post/<id>/delete` - 删除言论

### 搜索
- `GET /search?q=<keyword>` - 搜索言论

### 个人中心
- `GET /profile/` - 个人中心
- `GET /profile/posts` - 我的发表
- `GET /profile/favorites` - 我的收藏

## 安全特性

- CSRF 保护（Flask-WTF）
- 密码哈希存储（Werkzeug）
- 用户认证（Flask-Login）

## 开发说明

- 使用 Flask 蓝图组织路由
- 使用 SQLAlchemy ORM 进行数据库操作
- 使用 WTForms 进行表单验证
- 使用 Bootstrap 5 进行响应式设计
- 使用 AJAX 实现点赞和收藏的实时更新

## 许可证

MIT License

# RepoIcon

<p align="center">
  <img src="public/logo.svg" width="128" height="128" alt="RepoIcon Logo">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a>
</p>

使用 AI 为你的 GitHub 仓库生成精美的极简图标。

## 特性

- 🎨 为 GitHub 仓库生成极简现代的图标
- 🤖 由通义 AI 驱动的智能提示词生成
- 🔄 自动分析仓库内容和用途
- 🎯 针对不同编程语言的特定设计元素
- ⚡ 快速响应的界面
- 🌐 基于 URL 的简单生成方式

## 技术栈

- **前端**: React + TypeScript + Vite + TailwindCSS
- **后端**: FastAPI + Python
- **AI**: 通义 API（文本生成 + 图像生成）

## 开始使用

### 前置要求

- Node.js 16+
- Python 3.9+
- 通义 API 密钥

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/SimonGino/repoicon.git
cd repoicon
```

2. 安装前端依赖：
```bash
npm install
```

3. 安装后端依赖：
```bash
cd backend
pdm install
```

4. 配置环境变量：
```bash
# 在 backend/.env 中
TONGYI_API_KEY=你的_API_密钥
```

### 开发

1. 启动后端服务器：
```bash
cd backend
pdm run start
```

2. 启动前端开发服务器：
```bash
npm run dev
```

应用将在 `http://localhost:5173` 上可用

## 使用方法

1. 在浏览器中访问应用
2. 输入 GitHub 仓库 URL
3. 点击"生成图标"
4. 等待 AI 分析仓库并生成图标
5. 下载生成的图标

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [通义 API](https://tongyi.aliyun.com/)
- [TailwindCSS](https://tailwindcss.com/) 
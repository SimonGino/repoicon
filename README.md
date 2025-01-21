# RepoIcon

<p align="center">
  <img src="public/logo.svg" width="128" height="128" alt="RepoIcon Logo">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a>
</p>

Generate beautiful, minimalist icons for your GitHub repositories using AI.

## Features

- 🎨 Generate minimalist, modern icons for GitHub repositories
- 🤖 Powered by Tongyi AI for intelligent prompt generation
- 🔄 Automatic analysis of repository content and purpose
- 🎯 Language-specific design elements
- ⚡ Fast and responsive interface
- 🌐 Simple URL-based generation

## Tech Stack

- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: FastAPI + Python
- **AI**: Tongyi API (Text Generation + Image Generation)

## Getting Started

### Prerequisites

- Node.js 16+
- Python 3.9+
- Tongyi API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/SimonGino/repoicon.git
cd repoicon
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install backend dependencies:
```bash
cd backend
pdm install
```

4. Configure environment variables:
```bash
# In backend/.env
TONGYI_API_KEY=your_api_key_here
```

### Development

1. Start the backend server:
```bash
cd backend
pdm run start
```

2. Start the frontend development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

1. Visit the application in your browser
2. Enter a GitHub repository URL
3. Click "Generate Icon"
4. Wait for the AI to analyze the repository and generate an icon
5. Download the generated icon

## Deployment

### Using Docker (Recommended)

1. Install Docker and Docker Compose on your system

2. Clone the repository:
```bash
git clone https://github.com/SimonGino/repoicon.git
cd repoicon
```

3. Create a `.env` file in the root directory (you can copy from .env.example):
```bash
cp .env.example .env
```

4. Configure your environment variables in `.env`:
```bash
# Required
TONGYI_API_KEY=your_api_key_here

# Optional - change these if the default ports are in use
API_HOST=localhost
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

5. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: `http://localhost:{FRONTEND_PORT}` (default: 5173)
- Backend: `http://localhost:{BACKEND_PORT}` (default: 8000)

To use different ports, simply change the values in your `.env` file.

To stop the containers:
```bash
docker-compose down
```

### Manual Installation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Tongyi API](https://tongyi.aliyun.com/)
- [TailwindCSS](https://tailwindcss.com/)

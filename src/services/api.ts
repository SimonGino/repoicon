import axios from 'axios';
import type { GitHubRepo, ImageGenerationRequest, ImageGenerationResponse } from '../types';

const GITHUB_API_BASE = 'https://api.github.com';

// 构建 API_BASE URL
const buildApiBaseUrl = () => {
  // 如果提供了完整的 API URL，直接使用
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  const host = import.meta.env.API_HOST || 'localhost';
  const port = import.meta.env.BACKEND_PORT || '8000';
  const useHttps = import.meta.env.USE_HTTPS === 'true';
  const protocol = useHttps ? 'https' : 'http';

  // 如果是域名且使用标准端口（http:80 或 https:443），则不显示端口
  const isStandardPort = (useHttps && port === '443') || (!useHttps && port === '80');
  const portSuffix = isStandardPort ? '' : `:${port}`;

  return `${protocol}://${host}${portSuffix}`;
};

const API_BASE = buildApiBaseUrl();

const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
  baseURL: API_BASE,
});

export const getRepoInfo = async (owner: string, repo: string): Promise<GitHubRepo> => {
  const response = await axios.get(`${GITHUB_API_BASE}/repos/${owner}/${repo}`);
  const data = response.data;
  
  return {
    name: data.name,
    description: data.description,
    stars: data.stargazers_count,
    language: data.language,
    owner: data.owner.login,
  };
};

export const generateImage = async (request: ImageGenerationRequest): Promise<ImageGenerationResponse> => {
  const response = await api.post(`${API_BASE}/api/generate-image`, request);
  const data = response.data;
  
  if (!data.results?.[0]?.url) {
    throw new Error('No image URL in response');
  }

  return {
    imageUrl: data.results[0].url,
    prompt: request.prompt,
    timestamp: new Date().toISOString(),
  };
};

export interface GenerateIconResponse {
  task_id: string;
  prompt: string;
  repo_info: GitHubRepo;
}

export interface TaskStatusResponse {
  status: string;
  completed: boolean;
  image_url?: string;
  error?: {
    code: string;
    message: string;
  };
}

export const generateRepoIcon = async (repoUrl: string): Promise<GenerateIconResponse> => {
  const response = await api.post(`${API_BASE}/api/generate-repo-icon`, {
    url: repoUrl
  });
  return response.data;
};

export const checkImageStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await api.get(`${API_BASE}/api/check-image-status/${taskId}`);
  return response.data;
}; 
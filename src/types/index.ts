export interface GitHubRepo {
  name: string;
  description: string;
  stars: number;
  language: string;
  owner: string;
}

export interface ImageGenerationRequest {
  prompt: string;
  negative_prompt?: string;
  n: number;
  size?: string;
  style?: string;
}

export interface ImageGenerationResponse {
  imageUrl: string;
  prompt: string;
  timestamp: string;
} 
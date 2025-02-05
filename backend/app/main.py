from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
import os
import time
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import asyncio
import re
import base64

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://icon.mytest.cc",
        "https://icon.mytest.cc",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/api/v1"

class RepoUrlRequest(BaseModel):
    url: HttpUrl

# 删除 ImageGenerationRequest 和 TaskResponse 类

def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    patterns = [
        r"github\.com/([^/]+)/([^/]+)/?$",
        r"github\.com/([^/]+)/([^/]+)\.git$",
        r"github\.com:([^/]+)/([^/]+)\.git$"
    ]
    
    for pattern in patterns:
        if match := re.search(pattern, str(url)):
            return match.group(1), match.group(2)
    
    raise HTTPException(
        status_code=400,
        detail="Invalid GitHub URL format. Please provide a valid repository URL."
    )

async def get_repo_info(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch repository information from GitHub API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        response.raise_for_status()
        return response.json()

async def get_readme_content(owner: str, repo: str) -> str:
    """Fetch and decode README content from GitHub API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        if response.status_code == 404:
            return ""
        
        response.raise_for_status()
        content = response.json().get("content", "")
        if content:
            try:
                return base64.b64decode(content).decode('utf-8')
            except:
                return ""
        return ""

# 删除整个 generate_prompt 函数

async def generate_prompt_with_qianwen(repo_info: Dict[str, Any], readme_content: str) -> str:
    """Use Qianwen to generate an optimized image prompt."""
    name = repo_info.get("name", "")
    description = repo_info.get("description") or ""
    
    # Prepare context for Qianwen
    context = f"""Create an image generation prompt for a GitHub repository icon.

Repository Information:
- Name: {name}
- Purpose: {description.strip()}
- Details: {readme_content[:300]}

Guidelines:
1. Focus on the repository's core functionality and purpose
2. Create a symbolic representation of what this project does
3. Keep the design clean and minimalist
4. No text or letters allowed

The prompt should emphasize WHAT the repository does rather than HOW it looks.
Format your response as a concise image generation prompt."""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('TONGYI_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen-plus",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert at understanding software projects and converting their core purpose into visual concepts. Focus on what the project does and create prompts that will generate meaningful icons."
                        },
                        {
                            "role": "user",
                            "content": context
                        }
                    ]
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                generated_prompt = result["choices"][0]["message"]["content"].strip()
                # 只添加最基本的设计约束
                generated_prompt += ", minimalist style, no text"
                return generated_prompt
            
            raise HTTPException(
                status_code=500,
                detail="Failed to generate prompt with Qianwen"
            )
            
        except httpx.HTTPError as e:
            print(f"Error response: {e.response.text if hasattr(e, 'response') else str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calling Qianwen API: {str(e)}"
            )

async def check_task_status(task_id: str, api_key: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DASHSCOPE_API_BASE}/tasks/{task_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
            }
        )
        response.raise_for_status()
        return response.json()

@app.post("/api/generate-repo-icon")
async def generate_repo_icon(request: RepoUrlRequest):
    # Parse GitHub URL
    owner, repo = parse_github_url(str(request.url))
    
    # Fetch repository information and README content in parallel
    repo_info, readme_content = await asyncio.gather(
        get_repo_info(owner, repo),
        get_readme_content(owner, repo)
    )
    
    # Generate prompt using Qianwen
    prompt = await generate_prompt_with_qianwen(repo_info, readme_content)
    
    # Generate image using the prompt
    tongyi_api_key = os.getenv("TONGYI_API_KEY")
    if not tongyi_api_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    async with httpx.AsyncClient() as client:
        try:
            # Submit the initial request
            response = await client.post(
                f"{DASHSCOPE_API_BASE}/services/aigc/text2image/image-synthesis",
                json={
                    "model": "flux-dev",
                    "input": {
                        "prompt": prompt,
                        "negative_prompt": "icon"
                    },
                    "parameters": {
                        "steps": 50,
                        "size": "1024*1024"
                    },
                },
                headers={
                    "Authorization": f"Bearer {tongyi_api_key}",
                    "X-DashScope-Async": "enable",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            initial_data = response.json()
            
            if "code" in initial_data:
                raise HTTPException(
                    status_code=400,
                    detail={"code": initial_data["code"], "message": initial_data["message"]}
                )

            task_id = initial_data["output"]["task_id"]
            
            # Return immediately with task_id and prompt
            return {
                "task_id": task_id,
                "prompt": prompt,
                "repo_info": {
                    "name": repo_info["name"],
                    "description": repo_info.get("description"),
                    "language": repo_info.get("language"),
                    "stars": repo_info.get("stargazers_count")
                }
            }

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/check-image-status/{task_id}")
async def check_image_status(task_id: str):
    tongyi_api_key = os.getenv("TONGYI_API_KEY")
    if not tongyi_api_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    try:
        task_data = await check_task_status(task_id, tongyi_api_key)
        status = task_data["output"]["task_status"]
        
        if status == "SUCCEEDED":
            results = task_data["output"].get("results", [])
            successful_results = [r for r in results if "url" in r]
            
            if not successful_results:
                raise HTTPException(
                    status_code=500,
                    detail="No successful results in the response"
                )
            
            return {
                "status": status,
                "completed": True,
                "image_url": successful_results[0]["url"]
            }
        elif status == "FAILED":
            return {
                "status": status,
                "completed": True,
                "error": {
                    "code": task_data["output"].get("code"),
                    "message": task_data["output"].get("message")
                }
            }
        else:
            return {
                "status": status,
                "completed": False
            }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))
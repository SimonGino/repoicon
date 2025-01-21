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
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/api/v1"

class RepoUrlRequest(BaseModel):
    url: HttpUrl

class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    n: int = 1
    size: str = "32*32"

class TaskResponse(BaseModel):
    task_id: str
    task_status: str
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[Dict[str, str]] = None

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

def extract_key_concepts(text: str, max_words: int = 5) -> List[str]:
    """Extract key concepts from text, filtering out common words and code-related terms."""
    common_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as',
        'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will',
        'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which',
        'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year',
        'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its',
        'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
        'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
        # Code-related common terms to filter
        'code', 'install', 'using', 'used', 'example', 'file', 'files', 'data', 'function', 'method', 'class', 'object',
        'package', 'module', 'library', 'framework', 'api', 'documentation', 'docs', 'readme', 'installation', 'usage',
        'contributing', 'license', 'test', 'testing', 'build', 'run', 'running', 'setup', 'configure', 'configuration'
    }
    
    # Split text into words and clean them
    words = text.lower().replace('\n', ' ').split()
    words = [w.strip('.,!?()[]{}#*-_=+<>') for w in words]
    
    # Filter words
    meaningful_words = [
        word for word in words 
        if word and len(word) > 2  # Skip very short words
        and word not in common_words  # Skip common words
        and not word.startswith(('http', 'https', '#', '@'))  # Skip URLs and mentions
        and not any(c in word for c in '`\'"/\\')  # Skip code snippets and paths
    ]
    
    # Get unique words by frequency
    word_freq = {}
    for word in meaningful_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and get top words
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in top_words[:max_words]]

def generate_prompt(repo_info: Dict[str, Any], readme_content: str = "") -> str:
    """Generate an image prompt based on repository information and README content."""
    name = repo_info["name"]
    description = repo_info.get("description", "").strip()
    language = repo_info.get("language", "").lower()
    
    # Extract key concepts from description and README
    key_concepts = []
    if description:
        key_concepts.extend(extract_key_concepts(description, 3))
    if readme_content:
        key_concepts.extend(extract_key_concepts(readme_content, 3))
    key_concepts = list(dict.fromkeys(key_concepts))  # Remove duplicates
    
    # Base prompt components for icon generation
    components = [
        f"minimalist icon representing {name}",
        "modern app icon design",
        "flat design",
        "simple geometric shapes",
        "clean vector style",
        "no text or letters",
        "suitable for GitHub repository icon",
        "professional branding",
        "high contrast",
        "scalable design"
    ]
    
    # Add language-specific elements
    language_elements = {
        "python": "blue and yellow color scheme, subtle snake-like curves",
        "javascript": "modern geometric design in yellow and black",
        "typescript": "clean geometric shapes in blue tones",
        "rust": "warm orange and metallic elements",
        "go": "light blue tones with curved elements",
        "java": "red and white color scheme with curved elements",
        "c++": "modern design in blue tones",
        "ruby": "elegant gem-inspired shapes in red",
    }
    
    if language.lower() in language_elements:
        components.append(language_elements[language.lower()])
    
    # Add key concepts from description and README
    if key_concepts:
        concepts_str = " and ".join(key_concepts[:3])
        components.append(f"incorporating visual elements suggesting {concepts_str}")
    
    # Join all components
    prompt = ", ".join(components)
    
    # Add strong styling directives
    prompt += ". Absolutely no text or letters in the design. Pure iconographic representation."
    
    return prompt

async def generate_prompt_with_qianwen(repo_info: Dict[str, Any], readme_content: str) -> str:
    """Use Qianwen to generate an optimized image prompt."""
    name = repo_info["name"]
    description = repo_info.get("description", "").strip()
    language = repo_info.get("language", "").lower()
    
    # Prepare context for Qianwen
    context = f"""Generate an image generation prompt for a minimalist GitHub repository icon.

Repository Details:
- Name: {name}
- Language: {language}
- Description: {description}
- README Excerpt: {readme_content[:500]}

Requirements:
1. Create a minimalist, modern icon design
2. NO text or letters in the design
3. Use simple geometric shapes
4. Incorporate the project's essence
5. Consider the programming language's identity ({language})
6. Keep it professional and suitable for GitHub

Focus on visual elements that represent the core purpose of the repository.
Format the response as a clear, concise image generation prompt."""

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
                            "content": "You are an expert at creating image generation prompts. Create clear, detailed prompts that will result in minimalist, professional icons. Focus on visual elements and avoid any text in the design. Your responses should be direct image generation prompts without any explanation or conversation."
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
                
                # Add our standard constraints
                generated_prompt += ", minimalist icon design, no text, no letters, clean vector style, professional branding, high contrast, scalable design"
                
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
                    "model": "wanx2.1-t2i-turbo",
                    "input": {
                        "prompt": prompt,
                        "negative_prompt": "icon"
                    },
                    "parameters": {
                        "n": 1,
                        "size": "1024*1024",
                        "style": "minimalism",
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
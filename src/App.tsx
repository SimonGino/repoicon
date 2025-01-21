import { useState, useEffect } from 'react'
import * as Form from '@radix-ui/react-form'
import * as Toast from '@radix-ui/react-toast'
import { generateRepoIcon, checkImageStatus } from './services/api'
import type { GenerateIconResponse, TaskStatusResponse } from './services/api'

function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [generationResult, setGenerationResult] = useState<GenerateIconResponse | null>(null)
  const [imageStatus, setImageStatus] = useState<TaskStatusResponse | null>(null)

  // Poll for image status
  useEffect(() => {
    if (!generationResult?.task_id || imageStatus?.completed) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await checkImageStatus(generationResult.task_id);
        setImageStatus(status);
        
        if (status.completed) {
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Error checking image status:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [generationResult?.task_id, imageStatus?.completed]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setGenerationResult(null)
    setImageStatus(null)

    const formData = new FormData(event.currentTarget)
    const repoUrl = formData.get('repoUrl') as string

    try {
      const response = await generateRepoIcon(repoUrl)
      setGenerationResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Toast.Provider>
      <div className="min-h-screen bg-background p-8 flex flex-col">
        <div className="max-w-2xl mx-auto flex-grow w-full">
          <h1 className="text-4xl font-bold mb-8">Repository Icon Generator</h1>
          
          <Form.Root className="space-y-6" onSubmit={handleSubmit}>
            <Form.Field name="repoUrl">
              <Form.Label className="text-sm font-medium">GitHub Repository URL</Form.Label>
              <Form.Control asChild>
                <input
                  className="w-full px-3 py-2 border rounded-md"
                  type="url"
                  required
                  placeholder="e.g., https://github.com/facebook/react"
                />
              </Form.Control>
              <Form.Message className="text-xs text-muted-foreground mt-1">
                Enter the full GitHub repository URL
              </Form.Message>
            </Form.Field>

            <Form.Submit asChild>
              <button
                className="w-full bg-primary text-primary-foreground py-2 rounded-md hover:opacity-90 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Icon'}
              </button>
            </Form.Submit>
          </Form.Root>

          {error && (
            <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md">
              {error}
            </div>
          )}

          {generationResult && (
            <div className="mt-8 space-y-4">
              <div className="bg-card p-4 rounded-lg">
                <h2 className="text-xl font-semibold mb-2">{generationResult.repo_info.name}</h2>
                <p className="text-sm text-muted-foreground mb-2">{generationResult.repo_info.description}</p>
                <div className="flex gap-4 text-sm">
                  <span className="text-muted-foreground">Language: {generationResult.repo_info.language}</span>
                  <span className="text-muted-foreground">Stars: {generationResult.repo_info.stars}</span>
                </div>
                <details className="mt-2">
                  <summary className="text-sm text-muted-foreground cursor-pointer">View Prompt</summary>
                  <p className="text-sm mt-1 p-2 bg-muted rounded-md">{generationResult.prompt}</p>
                </details>
              </div>

              <div className="bg-card p-4 rounded-lg">
                <h3 className="text-lg font-medium mb-2">Generated Icon</h3>
                {!imageStatus?.completed ? (
                  <div className="flex items-center justify-center h-32 bg-muted rounded-lg">
                    <p className="text-muted-foreground">Generating image...</p>
                  </div>
                ) : imageStatus.error ? (
                  <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                    Error: {imageStatus.error.message}
                  </div>
                ) : (
                  <img
                    src={imageStatus.image_url}
                    alt={`Generated icon for ${generationResult.repo_info.name}`}
                    className="w-full rounded-lg shadow-lg"
                  />
                )}
              </div>
            </div>
          )}
        </div>

        <footer className="mt-16 pt-8 border-t border-border">
          <div className="max-w-2xl mx-auto flex flex-col items-center gap-4">
            <a
              href="https://github.com/SimonGino/repoicon"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <svg
                viewBox="0 0 24 24"
                className="w-6 h-6"
                fill="currentColor"
              >
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <span className="font-medium">View on GitHub</span>
            </a>
            <div className="text-sm text-muted-foreground text-center">
              <p>Built with FastAPI, React, and Tongyi API</p>
              <p>© 2025 RepoIcon. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>

      <Toast.Viewport className="fixed bottom-0 right-0 p-6 gap-2 flex flex-col" />
    </Toast.Provider>
  )
}

export default App

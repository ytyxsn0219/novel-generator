import type { Novel, Chapter, Job, FeedbackItem } from './types';

const API_BASE = '';

export async function createNovel(title: string, theme: string): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, theme }),
  });
  return res.json();
}

export async function getNovel(id: string): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels/${id}`);
  return res.json();
}

export async function generateSettings(id: string): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels/${id}/settings/generate`, { method: 'POST' });
  return res.json();
}

export async function confirmSettings(id: string, settings: Record<string, unknown>): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels/${id}/settings/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ settings }),
  });
  return res.json();
}

export async function listChapters(novelId: string): Promise<Chapter[]> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/chapters`);
  return res.json();
}

export async function createJob(novelId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/jobs`, { method: 'POST' });
  return res.json();
}

export async function getJob(novelId: string, jobId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/jobs/${jobId}`);
  return res.json();
}

export async function createFeedback(novelId: string, content: string, chapterId?: string): Promise<FeedbackItem> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/feedbacks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, chapter_id: chapterId }),
  });
  return res.json();
}

// Config APIs
export interface LLMConfig {
  provider: string;
  model: string;
  api_key: string;
  base_url?: string;
  temperature: number;
  max_tokens: number;
}

export interface LLMConfigResponse {
  provider: string;
  model: string;
  base_url?: string;
  temperature: number;
  max_tokens: number;
}

export interface LLMStatus {
  configured: boolean;
  provider: string;
  model: string;
}

export async function getLLMConfig(): Promise<LLMConfigResponse> {
  const res = await fetch(`${API_BASE}/config/llm`);
  return res.json();
}

export async function updateLLMConfig(config: LLMConfig): Promise<{status: string; message: string}> {
  const res = await fetch(`${API_BASE}/config/llm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return res.json();
}

export async function getLLMStatus(): Promise<LLMStatus> {
  const res = await fetch(`${API_BASE}/config/llm/status`);
  return res.json();
}

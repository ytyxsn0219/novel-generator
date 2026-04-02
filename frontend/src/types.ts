export interface Novel {
  id: string;
  title: string;
  theme: string;
  settings: Record<string, unknown>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  content: string;
  status: string;
  locked: boolean;
}

export interface Job {
  id: string;
  job_type: string;
  start_chapter: number;
  end_chapter: number;
  current_chapter: number;
  status: string;
}

export interface FeedbackItem {
  id: string;
  content: string;
  inferred_scope?: string;
  handled: boolean;
}

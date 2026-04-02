import { useEffect, useState } from 'react';
import type { Chapter, Job, Novel } from '../types';
import { listChapters, createJob, getJob } from '../api';
import FeedbackPanel from './FeedbackPanel';

interface Props {
  novel: Novel;
}

export default function Reader({ novel }: Props) {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);

  const refreshChapters = async () => {
    const data = await listChapters(novel.id);
    setChapters(data);
  };

  useEffect(() => {
    refreshChapters();
    const interval = setInterval(refreshChapters, 5000);
    return () => clearInterval(interval);
  }, [novel.id]);

  const startSerializing = async () => {
    const j = await createJob(novel.id);
    setJob(j);
  };

  useEffect(() => {
    if (!job) return;
    const interval = setInterval(async () => {
      const updated = await getJob(novel.id, job.id);
      setJob(updated);
      if (updated.current_chapter > chapters.length) {
        refreshChapters();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [job, novel.id, chapters.length]);

  return (
    <div style={{ marginTop: 20, display: 'flex', gap: 20 }}>
      <div style={{ flex: 1 }}>
        <h2>Chapters</h2>
        <button onClick={startSerializing} disabled={!!job}>Start Serializing</button>
        {job && <p>Job: {job.status} (chapter {job.current_chapter})</p>}
        <ul>
          {chapters.map((c) => (
            <li key={c.id}>
              <button onClick={() => setSelectedChapter(c)}>
                #{c.number} {c.title} {c.locked ? '🔒' : ''}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div style={{ flex: 2 }}>
        {selectedChapter ? (
          <div>
            <h3>#{selectedChapter.number} {selectedChapter.title}</h3>
            <pre style={{ whiteSpace: 'pre-wrap' }}>{selectedChapter.content}</pre>
            <FeedbackPanel novelId={novel.id} chapterId={selectedChapter.id} />
          </div>
        ) : (
          <p>Select a chapter to read</p>
        )}
      </div>
    </div>
  );
}

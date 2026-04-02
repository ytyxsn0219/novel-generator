import { useState } from 'react';
import type { Novel } from '../types';
import { createNovel } from '../api';

interface Props {
  onSelect: (novel: Novel) => void;
}

export default function NovelList({ onSelect }: Props) {
  const [novels, setNovels] = useState<Novel[]>([]);
  const [title, setTitle] = useState('');
  const [theme, setTheme] = useState('');


  const handleCreate = async () => {
    const novel = await createNovel(title || 'Untitled', theme);
    setNovels((prev) => [...prev, novel]);
    setTitle('');
    setTheme('');
    onSelect(novel);
  };

  return (
    <div>
      <h2>Novels</h2>
      <div style={{ marginBottom: 12 }}>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input placeholder="Theme / Idea" value={theme} onChange={(e) => setTheme(e.target.value)} style={{ marginLeft: 8 }} />
        <button onClick={handleCreate} style={{ marginLeft: 8 }}>Create</button>
      </div>
      <ul>
        {novels.map((n) => (
          <li key={n.id}>
            <button onClick={() => onSelect(n)}>{n.title}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

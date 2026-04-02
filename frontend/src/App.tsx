import { useState } from 'react';
import NovelList from './components/NovelList';
import SettingEditor from './components/SettingEditor';
import Reader from './components/Reader';
import type { Novel } from './types';

function App() {
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);

  return (
    <div style={{ padding: 20 }}>
      <h1>Novel Generator</h1>
      <NovelList onSelect={setSelectedNovel} />
      {selectedNovel && selectedNovel.status === 'drafting' && (
        <SettingEditor novel={selectedNovel} onUpdate={setSelectedNovel} />
      )}
      {selectedNovel && selectedNovel.status === 'serializing' && (
        <Reader novel={selectedNovel} />
      )}
    </div>
  );
}

export default App;

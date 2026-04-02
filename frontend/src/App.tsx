import { useState } from 'react';
import NovelList from './components/NovelList';
import SettingEditor from './components/SettingEditor';
import Reader from './components/Reader';
import ConfigPanel from './components/ConfigPanel';
import type { Novel } from './types';

function App() {
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Novel Generator</h1>
        <button onClick={() => setShowConfig(!showConfig)}>
          {showConfig ? '返回' : '⚙️ 设置'}
        </button>
      </div>

      {showConfig ? (
        <ConfigPanel onClose={() => setShowConfig(false)} />
      ) : (
        <>
          <NovelList onSelect={setSelectedNovel} />
          {selectedNovel && selectedNovel.status === 'drafting' && (
            <SettingEditor novel={selectedNovel} onUpdate={setSelectedNovel} />
          )}
          {selectedNovel && selectedNovel.status === 'serializing' && (
            <Reader novel={selectedNovel} />
          )}
        </>
      )}
    </div>
  );
}

export default App;

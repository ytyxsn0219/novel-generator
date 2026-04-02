import { useState } from 'react';
import type { Novel } from '../types';
import { generateSettings, confirmSettings } from '../api';

interface Props {
  novel: Novel;
  onUpdate: (novel: Novel) => void;
}

export default function SettingEditor({ novel, onUpdate }: Props) {
  const [settingsJson, setSettingsJson] = useState(JSON.stringify(novel.settings, null, 2));

  const handleGenerate = async () => {
    const updated = await generateSettings(novel.id);
    setSettingsJson(JSON.stringify(updated.settings, null, 2));
    onUpdate(updated);
  };

  const handleConfirm = async () => {
    const parsed = JSON.parse(settingsJson);
    const updated = await confirmSettings(novel.id, parsed);
    onUpdate(updated);
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h2>Settings</h2>
      <button onClick={handleGenerate}>Generate from Theme</button>
      <textarea
        value={settingsJson}
        onChange={(e) => setSettingsJson(e.target.value)}
        rows={20}
        cols={80}
        style={{ display: 'block', marginTop: 12 }}
      />
      <button onClick={handleConfirm} style={{ marginTop: 12 }}>Confirm Settings & Start</button>
    </div>
  );
}

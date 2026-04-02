import { useState } from 'react';
import { createFeedback } from '../api';

interface Props {
  novelId: string;
  chapterId: string;
}

export default function FeedbackPanel({ novelId, chapterId }: Props) {
  const [content, setContent] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    await createFeedback(novelId, content, chapterId);
    setSubmitted(true);
    setContent('');
  };

  return (
    <div style={{ marginTop: 20, borderTop: '1px solid #ccc', paddingTop: 12 }}>
      <h4>Feedback</h4>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={4}
        cols={60}
      />
      <button onClick={handleSubmit} style={{ display: 'block', marginTop: 8 }}>
        Submit Feedback
      </button>
      {submitted && <p>Feedback submitted. System will process it in background.</p>}
    </div>
  );
}

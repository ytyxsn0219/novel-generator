import { useEffect, useState } from 'react';
import { getLLMConfig, updateLLMConfig, getLLMStatus, type LLMConfig, type LLMConfigResponse } from '../api';

interface Props {
  onClose: () => void;
}

export default function ConfigPanel({ onClose }: Props) {
  const [config, setConfig] = useState<LLMConfig>({
    provider: 'openai',
    model: 'gpt-4o',
    api_key: '',
    base_url: '',
    temperature: 0.7,
    max_tokens: 4000,
  });
  const [originalConfig, setOriginalConfig] = useState<LLMConfigResponse | null>(null);
  const [status, setStatus] = useState<{ configured: boolean; provider: string; model: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const [cfg, sts] = await Promise.all([getLLMConfig(), getLLMStatus()]);
      setOriginalConfig(cfg);
      setStatus(sts);
      setConfig(prev => ({
        ...prev,
        provider: cfg.provider,
        model: cfg.model,
        base_url: cfg.base_url || '',
        temperature: cfg.temperature,
        max_tokens: cfg.max_tokens,
        // api_key 不返回，保留空值
      }));
    } catch (err) {
      setMessage('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const result = await updateLLMConfig(config);
      setMessage('配置保存成功！');
      setStatus({
        configured: true,
        provider: config.provider,
        model: config.model,
      });
    } catch (err) {
      setMessage('保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 20 }}>加载中...</div>;
  }

  return (
    <div style={{ padding: 20, maxWidth: 600 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2>系统设置</h2>
        <button onClick={onClose}>关闭</button>
      </div>

      {status && (
        <div
          style={{
            padding: '10px 15px',
            marginBottom: 20,
            borderRadius: 4,
            backgroundColor: status.configured ? '#e6f7e6' : '#fff3cd',
            border: `1px solid ${status.configured ? '#28a745' : '#ffc107'}`,
          }}
        >
          <strong>状态: </strong>
          {status.configured ? (
            <span style={{ color: '#28a745' }}>✓ 已配置 ({status.provider} / {status.model})</span>
          ) : (
            <span style={{ color: '#ffc107' }}>⚠ 未配置 API Key</span>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>LLM 提供商</label>
          <select
            value={config.provider}
            onChange={(e) => setConfig({ ...config, provider: e.target.value })}
            style={{ width: '100%', padding: 8 }}
          >
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="deepseek">DeepSeek</option>
            <option value="custom">自定义 (OpenAI 兼容)</option>
          </select>
        </div>

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>模型名称</label>
          <input
            type="text"
            value={config.model}
            onChange={(e) => setConfig({ ...config, model: e.target.value })}
            placeholder="gpt-4o, gpt-3.5-turbo, claude-3-sonnet, deepseek-chat"
            style={{ width: '100%', padding: 8 }}
          />
          <small style={{ color: '#666' }}>例如: gpt-4o, gpt-3.5-turbo, claude-3-sonnet, deepseek-chat</small>
        </div>

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>API Key</label>
          <input
            type="password"
            value={config.api_key}
            onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
            placeholder="sk-..."
            style={{ width: '100%', padding: 8 }}
          />
          <small style={{ color: '#666' }}>输入新的 API Key 以更新，留空则保持不变</small>
        </div>

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Base URL (可选)</label>
          <input
            type="text"
            value={config.base_url}
            onChange={(e) => setConfig({ ...config, base_url: e.target.value })}
            placeholder="https://api.openai.com"
            style={{ width: '100%', padding: 8 }}
          />
          <small style={{ color: '#666' }}>使用第三方服务时填写，如 https://api.deepseek.com</small>
        </div>

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Temperature: {config.temperature}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={config.temperature}
            onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
            style={{ width: '100%' }}
          />
          <small style={{ color: '#666' }}>0 = 确定性高，1 = 创造性高</small>
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Max Tokens: {config.max_tokens}</label>
          <input
            type="range"
            min="1000"
            max="8000"
            step="500"
            value={config.max_tokens}
            onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
            style={{ width: '100%' }}
          />
        </div>

        {message && (
          <div
            style={{
              padding: 10,
              marginBottom: 15,
              borderRadius: 4,
              backgroundColor: message.includes('成功') ? '#e6f7e6' : '#f8d7da',
              color: message.includes('成功') ? '#155724' : '#721c24',
            }}
          >
            {message}
          </div>
        )}

        <button type="submit" disabled={saving} style={{ padding: '10px 20px' }}>
          {saving ? '保存中...' : '保存配置'}
        </button>
      </form>
    </div>
  );
}

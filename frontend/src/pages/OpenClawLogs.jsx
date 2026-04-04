import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Search, Download, Trash2, Play, Pause, Filter } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const logsEndRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    fetchLogs();
    if (!isPaused) {
      intervalRef.current = setInterval(fetchLogs, 2000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPaused]);

  useEffect(() => {
    if (autoScroll) {
      scrollToBottom();
    }
  }, [logs, autoScroll]);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchLogs = async () => {
    try {
      const params = new URLSearchParams({ lines: '200' });
      if (filter) params.append('filter', filter);
      
      const response = await fetch(`${API}/api/openclaw/ui/logs/tail?${params}`);
      const data = await response.json();
      
      if (data && data.logs) {
        setLogs(data.logs);
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  const filteredLogs = logs.filter(log => {
    const logText = typeof log === 'string' ? log : JSON.stringify(log);
    const matchesSearch = filter === '' || logText.toLowerCase().includes(filter.toLowerCase());
    
    if (levelFilter === 'all') return matchesSearch;
    
    const matchesLevel = 
      (levelFilter === 'error' && (logText.includes('ERROR') || logText.includes('error'))) ||
      (levelFilter === 'warn' && (logText.includes('WARN') || logText.includes('warn'))) ||
      (levelFilter === 'info' && (logText.includes('INFO') || logText.includes('info'))) ||
      (levelFilter === 'debug' && (logText.includes('DEBUG') || logText.includes('debug')));
    
    return matchesSearch && matchesLevel;
  });

  const exportLogs = () => {
    const logsText = filteredLogs.join('\n');
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `openclaw-logs-${Date.now()}.txt`;
    a.click();
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const togglePause = () => {
    setIsPaused(!isPaused);
  };

  const getLogColor = (log) => {
    const logText = typeof log === 'string' ? log : JSON.stringify(log);
    if (logText.includes('ERROR') || logText.includes('error')) return 'text-red-400';
    if (logText.includes('WARN') || logText.includes('warn')) return 'text-yellow-400';
    if (logText.includes('INFO') || logText.includes('info')) return 'text-blue-400';
    if (logText.includes('DEBUG') || logText.includes('debug')) return 'text-purple-400';
    return 'text-slate-300';
  };

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col text-white">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-lg border-b border-purple-500/20 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Terminal className="w-6 h-6 text-purple-400" />
              <h1 className="text-2xl font-bold">Live Logs</h1>
              <div className={`px-3 py-1 rounded-full text-sm ${
                isPaused ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
              }`}>
                {isPaused ? '⏸ Paused' : '▶ Live'}
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={togglePause}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-all"
                title={isPaused ? 'Resume' : 'Pause'}
              >
                {isPaused ? (
                  <Play className="w-5 h-5 text-green-400" />
                ) : (
                  <Pause className="w-5 h-5 text-yellow-400" />
                )}
              </button>
              <button
                onClick={exportLogs}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-all"
                title="Export logs"
              >
                <Download className="w-5 h-5 text-slate-400" />
              </button>
              <button
                onClick={clearLogs}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-all"
                title="Clear logs"
              >
                <Trash2 className="w-5 h-5 text-slate-400" />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Filter logs..."
                className="w-full bg-slate-900/50 border border-purple-500/20 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
              />
            </div>

            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="bg-slate-900/50 border border-purple-500/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500/50"
            >
              <option value="all">All Levels</option>
              <option value="error">Errors</option>
              <option value="warn">Warnings</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>

            <label className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 border border-purple-500/20 rounded-lg cursor-pointer">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="form-checkbox h-4 w-4 text-purple-600"
              />
              <span className="text-sm">Auto-scroll</span>
            </label>
          </div>
        </div>
      </div>

      {/* Logs Display */}
      <div className="flex-1 overflow-y-auto p-6 font-mono text-sm">
        <div className="max-w-7xl mx-auto bg-slate-900/30 rounded-lg border border-purple-500/10 p-4">
          {filteredLogs.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No logs to display</p>
            </div>
          ) : (
            <div className="space-y-1">
              {filteredLogs.map((log, idx) => (
                <div
                  key={idx}
                  className={`${getLogColor(log)} hover:bg-slate-800/30 px-2 py-1 rounded`}
                >
                  {typeof log === 'string' ? log : JSON.stringify(log)}
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Footer Stats */}
      <div className="bg-slate-800/50 backdrop-blur-lg border-t border-purple-500/20 p-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-slate-400">
          <div>Total logs: {logs.length} | Filtered: {filteredLogs.length}</div>
          <div>Auto-refresh: {isPaused ? 'Off' : '2s'}</div>
        </div>
      </div>
    </div>
  );
};

export default OpenClawLogs;

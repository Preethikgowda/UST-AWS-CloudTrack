import React, { useEffect, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import apiClient from '../api/client';
import ChartCard from '../components/ChartCard';
import SectionHeader from '../components/SectionHeader';
import StatWidget from '../components/StatWidget';
import TableCard from '../components/TableCard';
import type { Portfolio, PortfolioHistoryItem } from '../types';

const PortfolioHistory: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState('');
  const [history, setHistory] = useState<PortfolioHistoryItem[]>([]);
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadPortfolios = async () => {
      try {
        const response = await apiClient.get<Portfolio[]>('/portfolio');
        setPortfolios(response.data);
        if (response.data.length > 0) {
          setSelectedPortfolioId(response.data[0].id);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Unable to load portfolios.');
      }
    };

    loadPortfolios();
  }, []);

  useEffect(() => {
    const loadHistory = async () => {
      if (!selectedPortfolioId) return;
      try {
        const response = await apiClient.get<PortfolioHistoryItem[]>(`/portfolio/history/${selectedPortfolioId}`);
        setHistory(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Unable to load history.');
      }
    };

    loadHistory();
  }, [selectedPortfolioId]);

  const recordSnapshot = async () => {
    if (!selectedPortfolioId) return;

    setIsSaving(true);
    setError('');
    try {
      await apiClient.post(`/portfolio/history/${selectedPortfolioId}/snapshot`);
      const response = await apiClient.get<PortfolioHistoryItem[]>(`/portfolio/history/${selectedPortfolioId}`);
      setHistory(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to record snapshot.');
    } finally {
      setIsSaving(false);
    }
  };

  const selectedPortfolio = portfolios.find((portfolio) => portfolio.id === selectedPortfolioId);
  const startValue = history[0]?.value || 0;
  const currentValue = selectedPortfolio?.total_value || 0;
  const growth = startValue > 0 ? ((currentValue - startValue) / startValue) * 100 : 0;

  return (
    <div className="page-stack">
      <SectionHeader title="Portfolio History" subtitle="Historical snapshots read from the portfolio history table." />

      {error && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

      {portfolios.length > 0 && (
        <div className="flex flex-col gap-3 sm:flex-row">
          <select
            value={selectedPortfolioId}
            onChange={(event) => setSelectedPortfolioId(event.target.value)}
            className="w-full max-w-sm rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100"
          >
            {portfolios.map((portfolio) => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </option>
            ))}
          </select>
          <button onClick={recordSnapshot} disabled={isSaving} className="rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
            {isSaving ? 'Recording...' : 'Record Snapshot'}
          </button>
        </div>
      )}

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <StatWidget label="Snapshots" value={String(history.length)} />
        <StatWidget label="Current Value" value={`$${currentValue.toLocaleString()}`} />
        <StatWidget label="Growth From First Snapshot" value={`${growth.toFixed(2)}%`} />
      </section>

      <ChartCard title="Timeline" subtitle="Saved historical portfolio valuations">
        <div className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history.map((item) => ({ date: item.snapshot_date.slice(0, 10), value: item.value }))}>
              <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke="#94a3b8" axisLine={false} tickLine={false} />
              <YAxis stroke="#94a3b8" axisLine={false} tickLine={false} tickFormatter={(value) => `$${(Number(value) / 1000).toFixed(0)}k`} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
              <Line dataKey="value" stroke="#818cf8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      <TableCard title="Snapshots" subtitle={`${history.length} records found`}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px]">
            <thead>
              <tr className="border-b border-slate-700 text-left text-xs uppercase tracking-[0.15em] text-slate-400">
                <th className="pb-4">Date</th>
                <th className="pb-4">Value</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id} className="border-b border-slate-800/80 text-sm text-slate-200">
                  <td className="py-4">{new Date(item.snapshot_date).toLocaleDateString()}</td>
                  <td className="py-4">${item.value.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </TableCard>
    </div>
  );
};

export default PortfolioHistory;

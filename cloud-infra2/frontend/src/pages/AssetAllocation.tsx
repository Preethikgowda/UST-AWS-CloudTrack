import React, { useEffect, useMemo, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import apiClient from '../api/client';
import ChartCard from '../components/ChartCard';
import SectionHeader from '../components/SectionHeader';
import type { Portfolio } from '../types';

const colors = ['#6366f1', '#8b5cf6', '#f59e0b', '#10b981', '#ec4899', '#64748b'];

const AssetAllocation: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPortfolios = async () => {
      try {
        const response = await apiClient.get<Portfolio[]>('/portfolio');
        setPortfolios(response.data);
        if (response.data.length > 0) {
          setSelectedPortfolioId(response.data[0].id);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Unable to load allocation data.');
      }
    };

    loadPortfolios();
  }, []);

  const portfolio = portfolios.find((item) => item.id === selectedPortfolioId) || portfolios[0];
  const allocation = useMemo(() => {
    if (!portfolio) return [];
    const totals = portfolio.assets.reduce<Record<string, number>>((acc, asset) => {
      acc[asset.asset_type] = (acc[asset.asset_type] || 0) + asset.current_value;
      return acc;
    }, {});

    return Object.entries(totals).map(([name, value], index) => ({
      name: name.replace('_', ' '),
      value,
      percentage: portfolio.total_value > 0 ? Number(((value / portfolio.total_value) * 100).toFixed(2)) : 0,
      color: colors[index % colors.length],
    }));
  }, [portfolio]);

  return (
    <div className="page-stack">
      <SectionHeader title="Asset Allocation" subtitle="Allocation calculated from assets saved in your portfolio." />

      {error && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

      {portfolios.length > 0 && (
        <select
          value={portfolio?.id || ''}
          onChange={(event) => setSelectedPortfolioId(event.target.value)}
          className="w-full max-w-sm rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100"
        >
          {portfolios.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
      )}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
        <ChartCard title="Donut Allocation" className="xl:col-span-3">
          <div className="flex h-[520px] flex-col items-center justify-center">
            <ResponsiveContainer width="100%" height={360}>
              <PieChart>
                <Pie data={allocation} dataKey="value" cx="50%" cy="50%" innerRadius={88} outerRadius={140}>
                  {allocation.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-3 flex flex-wrap items-center justify-center gap-4 text-sm text-slate-300">
              {allocation.map((entry) => (
                <span key={entry.name} className="flex items-center gap-2 capitalize">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                  {entry.name}
                </span>
              ))}
            </div>
          </div>
        </ChartCard>

        <section className="space-y-6 xl:col-span-2">
          <div className="app-card h-[520px] p-7">
            <h2 className="text-lg font-semibold text-slate-100">Allocation Breakdown</h2>
            <div className="mt-8 space-y-5">
              {allocation.map((entry) => (
                <div key={entry.name}>
                  <div className="mb-2 flex items-center justify-between text-sm capitalize">
                    <span className="text-slate-300">{entry.name}</span>
                    <span className="text-slate-200">{entry.percentage}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-800">
                    <div className="h-2 rounded-full" style={{ width: `${entry.percentage}%`, backgroundColor: entry.color }} />
                  </div>
                </div>
              ))}
              {allocation.length === 0 && <p className="text-sm text-slate-400">No assets saved yet. Add assets from the Portfolio page.</p>}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AssetAllocation;

import React, { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import apiClient from '../api/client';
import { useAuth } from '../auth/AuthContext';
import ChartCard from '../components/ChartCard';
import MetricCard from '../components/MetricCard';
import SectionHeader from '../components/SectionHeader';
import TableCard from '../components/TableCard';
import type { Asset, Portfolio } from '../types';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPortfolios = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await apiClient.get<Portfolio[]>('/portfolio');
        setPortfolios(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Unable to load dashboard data.');
      } finally {
        setIsLoading(false);
      }
    };

    loadPortfolios();
  }, []);

  const assets = useMemo(() => portfolios.flatMap((portfolio) => portfolio.assets), [portfolios]);
  const totalValue = portfolios.reduce((sum, portfolio) => sum + portfolio.total_value, 0);
  const allocation = useMemo(() => {
    const totals = assets.reduce<Record<string, number>>((acc, asset) => {
      acc[asset.asset_type] = (acc[asset.asset_type] || 0) + asset.current_value;
      return acc;
    }, {});

    return Object.entries(totals).map(([name, value]) => ({ name: name.replace('_', ' '), value }));
  }, [assets]);

  return (
    <div className="page-stack">
      <SectionHeader
        title={`Welcome, ${user?.name || 'Investor'}`}
        subtitle={isLoading ? 'Loading your portfolio data.' : 'Your dashboard is calculated from database-backed portfolio records.'}
      />

      {error && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Portfolio Value" value={`$${totalValue.toLocaleString()}`} />
        <MetricCard label="Portfolios" value={String(portfolios.length)} />
        <MetricCard label="Assets" value={String(assets.length)} />
        <MetricCard label="Largest Holding" value={assets.length ? `$${Math.max(...assets.map((asset) => asset.current_value)).toLocaleString()}` : '$0'} />
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <ChartCard title="Portfolio Values" subtitle="Current total value by portfolio" className="xl:col-span-7">
          <div className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={portfolios.map((portfolio) => ({ name: portfolio.name, value: portfolio.total_value }))}>
                <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#94a3b8" axisLine={false} tickLine={false} />
                <YAxis stroke="#94a3b8" axisLine={false} tickLine={false} tickFormatter={(value) => `$${(Number(value) / 1000).toFixed(0)}k`} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
                <Bar dataKey="value" fill="#818cf8" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Asset Allocation" subtitle="Current value by asset class" className="xl:col-span-5">
          <div className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={allocation} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid stroke="rgba(148,163,184,0.1)" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" axisLine={false} tickLine={false} width={110} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
                <Bar dataKey="value" fill="#6366f1" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </section>

      <TableCard title="Current Holdings" subtitle={`${assets.length} assets stored for your account`} className="min-h-[350px]">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px]">
            <thead>
              <tr className="border-b border-slate-700 text-left text-xs uppercase tracking-[0.15em] text-slate-400">
                <th className="pb-4">Asset</th>
                <th className="pb-4">Type</th>
                <th className="pb-4">Quantity</th>
                <th className="pb-4">Value</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset: Asset) => (
                <tr key={asset.id} className="border-b border-slate-800/80 text-sm text-slate-200">
                  <td className="py-4">{asset.asset_name}</td>
                  <td className="py-4 capitalize">{asset.asset_type.replace('_', ' ')}</td>
                  <td className="py-4">{asset.quantity}</td>
                  <td className="py-4">${asset.current_value.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </TableCard>
    </div>
  );
};

export default Dashboard;

import React, { useEffect, useMemo, useState } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../auth/AuthContext';
import SectionHeader from '../components/SectionHeader';
import type { Asset, AssetType, Portfolio } from '../types';

const assetTypes: AssetType[] = ['stocks', 'bonds', 'gold', 'crypto', 'mutual_funds', 'cash'];

const PortfolioOverview: React.FC = () => {
  const { user } = useAuth();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState('');
  const [portfolioName, setPortfolioName] = useState('Default Portfolio');
  const [assetName, setAssetName] = useState('');
  const [assetType, setAssetType] = useState<AssetType>('stocks');
  const [quantity, setQuantity] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [filter, setFilter] = useState<'all' | AssetType>('all');
  const [showAssetForm, setShowAssetForm] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const selectedPortfolio = portfolios.find((portfolio) => portfolio.id === selectedPortfolioId) || portfolios[0];
  const assets = selectedPortfolio?.assets || [];

  const filteredAssets = useMemo(
    () => (filter === 'all' ? assets : assets.filter((asset) => asset.asset_type === filter)),
    [assets, filter],
  );

  const loadPortfolios = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await apiClient.get<Portfolio[]>('/portfolio');
      setPortfolios(response.data);
      if (response.data.length > 0) {
        setSelectedPortfolioId((current) => current || response.data[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to load portfolios.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolios();
  }, []);

  const createPortfolio = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setError('');
    try {
      const response = await apiClient.post<Portfolio>('/portfolio', {
        customer_id: user.id,
        name: portfolioName,
      });
      setPortfolios((current) => [...current, response.data]);
      setSelectedPortfolioId(response.data.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to create portfolio.');
    } finally {
      setIsSaving(false);
    }
  };

  const addAsset = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedPortfolio) return;

    setIsSaving(true);
    setError('');
    try {
      await apiClient.post('/portfolio/add-asset', {
        portfolio_id: selectedPortfolio.id,
        asset_name: assetName,
        asset_type: assetType,
        quantity: Number(quantity),
        purchase_price: Number(purchasePrice),
      });
      setAssetName('');
      setQuantity('');
      setPurchasePrice('');
      setShowAssetForm(false);
      await loadPortfolios();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to add asset.');
    } finally {
      setIsSaving(false);
    }
  };

  const removeAsset = async (asset: Asset) => {
    setError('');
    try {
      await apiClient.delete(`/portfolio/remove-asset/${asset.id}`);
      await loadPortfolios();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to remove asset.');
    }
  };

  return (
    <div className="page-stack">
      <SectionHeader title="Portfolio Overview" subtitle="Create portfolios and manage assets stored in PostgreSQL." />

      {error && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

      <section className="app-card p-7">
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">Portfolios</h2>
            <p className="mt-1 text-sm text-slate-400">{isLoading ? 'Loading from database' : `${portfolios.length} portfolios found`}</p>
          </div>
          {portfolios.length > 0 && (
            <div className="flex flex-col gap-3 sm:flex-row">
              <select
                value={selectedPortfolio?.id || ''}
                onChange={(event) => setSelectedPortfolioId(event.target.value)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-100"
              >
                {portfolios.map((portfolio) => (
                  <option key={portfolio.id} value={portfolio.id}>
                    {portfolio.name}
                  </option>
                ))}
              </select>
              <button onClick={() => setShowAssetForm((value) => !value)} className="rounded-xl border border-indigo-400/40 px-4 py-2 text-sm text-indigo-200">
                {showAssetForm ? 'Close Asset Form' : 'Add Asset'}
              </button>
            </div>
          )}
        </div>

        {portfolios.length === 0 && !isLoading && (
          <form onSubmit={createPortfolio} className="flex flex-col gap-3 sm:flex-row">
            <input
              value={portfolioName}
              onChange={(event) => setPortfolioName(event.target.value)}
              placeholder="Portfolio name"
              required
              className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            />
            <button type="submit" disabled={isSaving} className="rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {isSaving ? 'Creating...' : 'Create Portfolio'}
            </button>
          </form>
        )}

        {showAssetForm && selectedPortfolio && (
          <form onSubmit={addAsset} className="mt-6 grid gap-4 rounded-xl border border-slate-700 bg-slate-950 p-5 md:grid-cols-2 xl:grid-cols-5">
            <input
              value={assetName}
              onChange={(event) => setAssetName(event.target.value)}
              placeholder="Asset name"
              required
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            />
            <select
              value={assetType}
              onChange={(event) => setAssetType(event.target.value as AssetType)}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            >
              {assetTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace('_', ' ')}
                </option>
              ))}
            </select>
            <input
              type="number"
              min="0"
              step="any"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
              placeholder="Quantity"
              required
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            />
            <input
              type="number"
              min="0"
              step="any"
              value={purchasePrice}
              onChange={(event) => setPurchasePrice(event.target.value)}
              placeholder="Purchase price"
              required
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            />
            <button type="submit" disabled={isSaving} className="rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {isSaving ? 'Saving...' : 'Save Asset'}
            </button>
          </form>
        )}
      </section>

      {selectedPortfolio && (
        <>
          <div className="flex flex-wrap gap-3">
            {(['all', ...assetTypes] as Array<'all' | AssetType>).map((type) => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`rounded-xl px-4 py-2 text-sm capitalize ${filter === type ? 'bg-indigo-500/20 text-indigo-200' : 'bg-slate-900 text-slate-300'}`}
              >
                {type.replace('_', ' ')}
              </button>
            ))}
          </div>

          <section className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
            {filteredAssets.map((asset) => (
              <article key={asset.id} className="app-card min-h-[220px] p-7">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-100">{asset.asset_name}</h3>
                    <span className="mt-2 inline-flex rounded-full bg-slate-800 px-3 py-1 text-xs capitalize text-slate-300">{asset.asset_type.replace('_', ' ')}</span>
                  </div>
                  <button onClick={() => removeAsset(asset)} className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300">
                    Remove
                  </button>
                </div>
                <div className="mt-8 grid grid-cols-2 gap-5 text-sm">
                  <div>
                    <p className="text-slate-400">Quantity</p>
                    <p className="mt-1 text-slate-100">{asset.quantity}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Purchase Price</p>
                    <p className="mt-1 text-slate-100">${asset.purchase_price.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Current Value</p>
                    <p className="mt-1 text-slate-100">${asset.current_value.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Portfolio</p>
                    <p className="mt-1 text-slate-100">{selectedPortfolio.name}</p>
                  </div>
                </div>
              </article>
            ))}
          </section>
        </>
      )}
    </div>
  );
};

export default PortfolioOverview;

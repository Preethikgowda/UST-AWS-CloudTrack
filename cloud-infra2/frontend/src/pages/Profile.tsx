import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../auth/AuthContext';
import SectionHeader from '../components/SectionHeader';
import type { User } from '../types';

const Profile: React.FC = () => {
  const { user, updateStoredUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setName(user?.name || '');
    setEmail(user?.email || '');
  }, [user]);

  const saveProfile = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setMessage('');
    setError('');

    try {
      const response = await apiClient.put<User>(`/customers/${user.id}`, { name, email });
      updateStoredUser(response.data);
      setMessage('Profile saved to database.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to save profile.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="page-stack">
      <SectionHeader title="Profile" subtitle="Update the account record stored in PostgreSQL." />

      <form onSubmit={saveProfile} className="mx-auto w-full max-w-[900px] app-card p-7">
        <div className="mb-7">
          <h2 className="text-2xl font-semibold text-slate-100">Account Details</h2>
          <p className="mt-2 text-sm text-slate-400">Changes here are written through the customer API.</p>
        </div>

        {message && <div className="mb-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{message}</div>}
        {error && <div className="mb-5 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <label className="text-sm text-slate-300">
            Full Name
            <input
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200 outline-none focus:border-indigo-400"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </label>
          <label className="text-sm text-slate-300">
            Email
            <input
              type="email"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200 outline-none focus:border-indigo-400"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label className="text-sm text-slate-300">
            Role
            <input
              className="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-500"
              value={user?.role || ''}
              disabled
            />
          </label>
          <label className="text-sm text-slate-300">
            Account Status
            <input
              className="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-500"
              value={user?.is_active ? 'Active' : 'Inactive'}
              disabled
            />
          </label>
        </div>

        <div className="mt-7 flex justify-end">
          <button type="submit" disabled={isSaving} className="rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
            {isSaving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Profile;

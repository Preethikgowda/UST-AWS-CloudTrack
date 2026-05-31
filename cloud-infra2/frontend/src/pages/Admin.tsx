import React, { useEffect, useMemo, useState } from 'react';
import apiClient from '../api/client';
import SectionHeader from '../components/SectionHeader';
import StatWidget from '../components/StatWidget';
import TableCard from '../components/TableCard';
import type { CustomerPayload, User } from '../types';

type UserForm = {
  id?: string;
  name: string;
  email: string;
  password: string;
  role: 'investor' | 'advisor' | 'admin';
  is_active: boolean;
};

const emptyForm: UserForm = {
  name: '',
  email: '',
  password: '',
  role: 'investor',
  is_active: true,
};

const Admin: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState<UserForm>(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const loadUsers = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await apiClient.get<User[]>('/customers');
      setUsers(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to load users.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const filtered = useMemo(
    () =>
      users.filter((user) =>
        `${user.name} ${user.email} ${user.role}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [search, users],
  );

  const startCreate = () => {
    setForm(emptyForm);
    setShowForm(true);
    setError('');
  };

  const startEdit = (user: User) => {
    setForm({
      id: user.id,
      name: user.name,
      email: user.email,
      password: '',
      role: user.role,
      is_active: user.is_active,
    });
    setShowForm(true);
    setError('');
  };

  const saveUser = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSaving(true);
    setError('');

    try {
      if (form.id) {
        const payload = {
          name: form.name,
          email: form.email,
          role: form.role,
          is_active: form.is_active,
        };
        await apiClient.put(`/customers/${form.id}`, payload);
      } else {
        const payload: CustomerPayload = {
          name: form.name,
          email: form.email,
          password: form.password,
          role: form.role,
        };
        await apiClient.post('/customers', payload);
      }

      setShowForm(false);
      setForm(emptyForm);
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to save user.');
    } finally {
      setIsSaving(false);
    }
  };

  const toggleActive = async (user: User) => {
    setError('');
    try {
      await apiClient.put(`/customers/${user.id}`, { is_active: !user.is_active });
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to update user status.');
    }
  };

  return (
    <div className="page-stack">
      <SectionHeader title="Admin" subtitle="Platform user management backed by the customer database." />

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <StatWidget label="Total Users" value={String(users.length)} />
        <StatWidget label="Active Users" value={String(users.filter((user) => user.is_active).length)} />
        <StatWidget label="Admins" value={String(users.filter((user) => user.role === 'admin').length)} />
      </section>

      <TableCard
        title="User Management"
        subtitle={isLoading ? 'Loading users from database' : `${filtered.length} users shown`}
        action={
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search users"
              className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 outline-none focus:border-indigo-400 sm:w-64"
            />
            <button onClick={startCreate} className="rounded-xl border border-indigo-400/40 px-4 py-2 text-sm text-indigo-200">
              Add User
            </button>
          </div>
        }
      >
        {error && <div className="mb-5 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

        {showForm && (
          <form onSubmit={saveUser} className="mb-7 grid gap-4 rounded-xl border border-slate-700 bg-slate-950 p-5 md:grid-cols-2">
            <input
              value={form.name}
              onChange={(event) => setForm((value) => ({ ...value, name: event.target.value }))}
              placeholder="Full name"
              required
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            />
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((value) => ({ ...value, email: event.target.value }))}
              placeholder="Email"
              required
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            />
            {!form.id && (
              <input
                type="password"
                value={form.password}
                onChange={(event) => setForm((value) => ({ ...value, password: event.target.value }))}
                placeholder="Temporary password"
                minLength={8}
                required
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
              />
            )}
            <select
              value={form.role}
              onChange={(event) => setForm((value) => ({ ...value, role: event.target.value as UserForm['role'] }))}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-400"
            >
              <option value="investor">Investor</option>
              <option value="advisor">Advisor</option>
              <option value="admin">Admin</option>
            </select>
            <label className="flex items-center gap-3 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(event) => setForm((value) => ({ ...value, is_active: event.target.checked }))}
              />
              Active account
            </label>
            <div className="flex justify-end gap-3 md:col-span-2">
              <button type="button" onClick={() => setShowForm(false)} className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300">
                Cancel
              </button>
              <button type="submit" disabled={isSaving} className="rounded-xl bg-indigo-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
                {isSaving ? 'Saving...' : 'Save User'}
              </button>
            </div>
          </form>
        )}

        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px]">
            <thead className="sticky top-0 bg-[#0f172a]">
              <tr className="border-b border-slate-700 text-left text-xs uppercase tracking-[0.15em] text-slate-400">
                <th className="pb-4">User</th>
                <th className="pb-4">Role</th>
                <th className="pb-4">Status</th>
                <th className="pb-4">Joined</th>
                <th className="pb-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((user) => (
                <tr key={user.id} className="border-b border-slate-800/80 text-sm text-slate-200">
                  <td className="py-4">
                    {user.name}
                    <div className="text-xs text-slate-400">{user.email}</div>
                  </td>
                  <td className="py-4 capitalize">{user.role}</td>
                  <td className="py-4">{user.is_active ? 'Active' : 'Inactive'}</td>
                  <td className="py-4 text-slate-400">{new Date(user.created_at).toLocaleDateString()}</td>
                  <td className="py-4 text-right">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => startEdit(user)} className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs">
                        Edit
                      </button>
                      <button onClick={() => toggleActive(user)} className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs">
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </TableCard>
    </div>
  );
};

export default Admin;

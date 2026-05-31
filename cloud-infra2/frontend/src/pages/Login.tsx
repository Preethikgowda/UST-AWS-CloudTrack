import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const Login: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (mode === 'signup') {
        await register({ name, email, password });
      } else {
        await login(email, password);
      }
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to complete request. Check the form and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#020617] px-4 py-10 text-slate-100">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 h-14 w-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-500" />
          <h1 className="text-3xl font-bold">IntelliWealth</h1>
          <p className="mt-2 text-sm text-slate-400">Portfolio intelligence backed by real account data.</p>
        </div>

        <section className="app-card p-7">
          <div className="mb-6 grid grid-cols-2 rounded-xl bg-slate-950 p-1">
            <button
              type="button"
              onClick={() => setMode('login')}
              className={`rounded-lg px-4 py-2 text-sm ${mode === 'login' ? 'bg-slate-800 text-white' : 'text-slate-400'}`}
            >
              Sign in
            </button>
            <button
              type="button"
              onClick={() => setMode('signup')}
              className={`rounded-lg px-4 py-2 text-sm ${mode === 'signup' ? 'bg-slate-800 text-white' : 'text-slate-400'}`}
            >
              Sign up
            </button>
          </div>

          {error && <div className="mb-4 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'signup' && (
              <label className="block text-sm text-slate-300">
                Full name
                <input
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  required
                  className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-indigo-400"
                />
              </label>
            )}

            <label className="block text-sm text-slate-300">
              Email
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-indigo-400"
              />
            </label>

            <label className="block text-sm text-slate-300">
              Password
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={8}
                required
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-indigo-400"
              />
            </label>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-xl bg-indigo-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? 'Please wait...' : mode === 'signup' ? 'Create account' : 'Sign in'}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
};

export default Login;

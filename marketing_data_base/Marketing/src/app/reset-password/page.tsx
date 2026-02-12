
"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { resetPassword } from '@/actions/auth';
import { Suspense } from 'react';

function ResetPasswordForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get('token');

    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!token) {
            setStatus('error');
            setMessage('Missing reset token.');
            return;
        }

        if (password !== confirmPassword) {
            setStatus('error');
            setMessage('Passwords do not match.');
            return;
        }

        if (password.length < 6) {
            setStatus('error');
            setMessage('Password must be at least 6 characters.');
            return;
        }

        setStatus('loading');
        setMessage('');

        try {
            const result = await resetPassword(token, password);
            if (result.error) {
                setStatus('error');
                setMessage(result.error);
            } else {
                setStatus('success');
                setMessage('Password successfully reset!');
                setTimeout(() => router.push('/'), 3000);
            }
        } catch (error) {
            setStatus('error');
            setMessage('An unexpected error occurred.');
        }
    };

    if (!token) {
        return (
            <div className="card" style={{ maxWidth: '400px', width: '100%', textAlign: 'center' }}>
                <div style={{ color: '#fca5a5', marginBottom: '1rem' }}>Invalid or missing reset token.</div>
                <Link href="/forgot-password" className="btn btn-primary">Request New Link</Link>
            </div>
        );
    }

    return (
        <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
            <h1 className="heading" style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Set New Password</h1>

            {status === 'success' ? (
                <div style={{ textAlign: 'center' }}>
                    <div style={{ color: '#86efac', marginBottom: '1rem', padding: '1rem', background: 'rgba(34,197,94,0.1)', borderRadius: '6px' }}>
                        {message}
                    </div>
                    <p style={{ color: '#a1a1aa', marginBottom: '1rem' }}>Redirecting to login...</p>
                    <Link href="/" className="btn btn-primary" style={{ width: '100%', display: 'inline-block', textAlign: 'center' }}>
                        Login Now
                    </Link>
                </div>
            ) : (
                <form onSubmit={handleSubmit}>
                    {status === 'error' && (
                        <div style={{ color: '#fca5a5', marginBottom: '1rem', padding: '0.5rem', background: 'rgba(239,68,68,0.1)', borderRadius: '4px' }}>
                            {message}
                        </div>
                    )}

                    <div className="input-group">
                        <label className="label">New Password</label>
                        <input
                            type="password"
                            className="input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                            minLength={6}
                        />
                    </div>

                    <div className="input-group">
                        <label className="label">Confirm Password</label>
                        <input
                            type="password"
                            className="input"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                            minLength={6}
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%', marginBottom: '1rem' }}
                        disabled={status === 'loading'}
                    >
                        {status === 'loading' ? 'Resetting...' : 'Reset Password'}
                    </button>
                </form>
            )}
        </div>
    );
}

export default function ResetPasswordPage() {
    return (
        <main className="container flex-center" style={{ minHeight: '100vh' }}>
            <Suspense fallback={<div className="text-white">Loading...</div>}>
                <ResetPasswordForm />
            </Suspense>
        </main>
    );
}

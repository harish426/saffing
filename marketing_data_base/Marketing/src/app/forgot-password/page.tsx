
"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { forgotPassword } from '@/actions/auth';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus('loading');
        setMessage('');

        try {
            await forgotPassword(email);
            setStatus('success');
            setMessage('If an account exists with this email, you will receive a password reset link shortly.');
        } catch (error) {
            setStatus('error');
            setMessage('Something went wrong. Please try again.');
        }
    };

    return (
        <main className="container flex-center" style={{ minHeight: '100vh' }}>
            <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
                <h1 className="heading" style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Reset Password</h1>

                {status === 'success' ? (
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ color: '#86efac', marginBottom: '1rem', padding: '1rem', background: 'rgba(34,197,94,0.1)', borderRadius: '6px' }}>
                            {message}
                        </div>
                        <Link href="/" className="btn btn-primary" style={{ width: '100%', display: 'inline-block', textAlign: 'center' }}>
                            Return to Login
                        </Link>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit}>
                        <p style={{ color: '#a1a1aa', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                            Enter your email address and we'll send you a link to reset your password.
                        </p>

                        {status === 'error' && (
                            <div style={{ color: '#fca5a5', marginBottom: '1rem', padding: '0.5rem', background: 'rgba(239,68,68,0.1)', borderRadius: '4px' }}>
                                {message}
                            </div>
                        )}

                        <div className="input-group">
                            <label className="label">Email Address</label>
                            <input
                                type="email"
                                className="input"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="you@example.com"
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            style={{ width: '100%', marginBottom: '1rem' }}
                            disabled={status === 'loading'}
                        >
                            {status === 'loading' ? 'Sending...' : 'Send Reset Link'}
                        </button>

                        <Link href="/" style={{ display: 'block', textAlign: 'center', color: '#a1a1aa', fontSize: '0.9rem', textDecoration: 'none' }}>
                            ← Back to Login
                        </Link>
                    </form>
                )}
            </div>
        </main>
    );
}

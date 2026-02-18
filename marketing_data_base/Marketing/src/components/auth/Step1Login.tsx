
import React from 'react';
import { useRouter } from 'next/navigation';
import { loginUser, registerUser } from '@/actions/auth';

interface Step1Props {
    formData: any;
    setFormData: (data: any) => void;
    nextStep: () => void;
    isLogin: boolean;
    setIsLogin: (isLogin: boolean) => void;
}

export default function Step1Login({ formData, setFormData, nextStep, isLogin, setIsLogin }: Step1Props) {
    const router = useRouter();
    const [error, setError] = React.useState<string | null>(null);
    const [loading, setLoading] = React.useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            if (isLogin) {
                const result = await loginUser(formData);
                if (result?.error) {
                    setError(result.error);
                } else if (result?.success) {
                    router.refresh();
                    router.push('/dashboard');
                }
            } else {
                const result = await registerUser(formData);
                if (result?.error) {
                    setError(result.error);
                } else if (result?.success) {
                    nextStep();
                }
            }
        } catch (err) {
            setError("An unexpected error occurred");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card" style={{ maxWidth: '400px', width: '100%', margin: '0 auto' }}>
            <h2 className="heading" style={{ fontSize: '2rem', marginBottom: '1rem' }}>
                {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>

            {error && (
                <div style={{ padding: '0.5rem', background: 'rgba(239,68,68,0.2)', color: '#fca5a5', borderRadius: '4px', marginBottom: '1rem', textAlign: 'center' }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                {!isLogin && (
                    <div className="input-group">
                        <label className="label">Full Name</label>
                        <input
                            type="text"
                            name="name"
                            className="input"
                            value={formData.name || ''}
                            onChange={handleChange}
                            required={!isLogin}
                            placeholder="John Doe"
                        />
                    </div>
                )}

                <div className="input-group">
                    <label className="label">Email Address</label>
                    <input
                        type="email"
                        name="email"
                        className="input"
                        value={formData.email || ''}
                        onChange={handleChange}
                        required
                        placeholder="you@example.com"
                    />
                </div>

                <div className="input-group">
                    <label className="label">Password</label>
                    <input
                        type="password"
                        name="password"
                        className="input"
                        value={formData.password || ''}
                        onChange={handleChange}
                        required
                        placeholder="••••••••"
                    />
                </div>

                {isLogin && (
                    <div style={{ textAlign: 'right', marginBottom: '1rem', marginTop: '-0.5rem' }}>
                        <a href="/forgot-password" style={{ color: '#6366f1', fontSize: '0.8rem', textDecoration: 'none' }}>
                            Forgot Password?
                        </a>
                    </div>
                )}

                <button type="submit" className="btn btn-primary" style={{ width: '100%', marginBottom: '1rem' }} disabled={loading}>
                    {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
                </button>

                <p style={{ textAlign: 'center', color: '#a1a1aa', fontSize: '0.9rem' }}>
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button
                        type="button"
                        onClick={() => { setIsLogin(!isLogin); setError(null); }}
                        style={{ background: 'none', border: 'none', color: '#6366f1', cursor: 'pointer', textDecoration: 'underline' }}
                    >
                        {isLogin ? 'Sign Up' : 'Sign In'}
                    </button>
                </p>
            </form>
        </div>
    );
}


import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { saveEmailSettings } from '@/actions/onboarding';

interface Step3Props {
    formData: any;
    setFormData: (data: any) => void;
    prevStep: () => void;
}

export default function Step3Email({ formData, setFormData, prevStep }: Step3Props) {
    const router = useRouter();
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setError(null);

        try {
            const result = await saveEmailSettings(formData);
            if (result?.error) {
                setError(result.error);
            } else {
                router.push('/dashboard');
            }
        } catch (err) {
            setError("Failed to save settings.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="card" style={{ maxWidth: '500px', width: '100%', margin: '0 auto' }}>
            <h2 className="heading" style={{ fontSize: '2rem', marginBottom: '1rem' }}>Email Setup</h2>
            <p style={{ textAlign: 'center', color: '#a1a1aa', marginBottom: '2rem' }}>
                Connect your job application email to automate tracking.
            </p>

            {error && (
                <div style={{ padding: '0.5rem', background: 'rgba(239,68,68,0.2)', color: '#fca5a5', borderRadius: '4px', marginBottom: '1rem', textAlign: 'center' }}>
                    {error}
                </div>
            )}

            <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                <p style={{ color: '#fca5a5', fontSize: '0.9rem' }}>
                    <strong>Note:</strong> Please use an App Password, not your main password.
                    <br />
                    <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>
                        Get Google App Password
                    </a>
                </p>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="input-group">
                    <label className="label">Job Email Address</label>
                    <input
                        type="email"
                        name="jobEmail"
                        className="input"
                        value={formData.jobEmail || formData.email || ''} // Default to login email
                        onChange={handleChange}
                        required
                        placeholder="jobs@example.com"
                    />
                </div>

                <div className="input-group">
                    <label className="label">Google App Password</label>
                    <input
                        type="password"
                        name="appPassword"
                        className="input"
                        value={formData.appPassword || ''}
                        onChange={handleChange}
                        required
                        placeholder="abcd efgh ijkl mnop"
                    />
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button type="button" onClick={prevStep} className="btn btn-outline" style={{ flex: 1 }} disabled={saving}>
                        Back
                    </button>
                    <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
                        {saving ? 'Saving...' : 'Complete Setup'}
                    </button>
                </div>
            </form>
        </div>
    );
}

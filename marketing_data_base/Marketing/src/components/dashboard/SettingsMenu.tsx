
"use client";

import React, { useState, useEffect, useRef } from 'react';
import { getUserSettings, saveEmailSettings, replaceResume } from '@/actions/onboarding';
import { changePassword } from '@/actions/user';

export default function SettingsMenu() {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState<'profile' | 'security'>('profile');
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [replacingResume, setReplacingResume] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [resumeInfo, setResumeInfo] = useState<{ filename: string; createdAt: Date } | null>(null);

    const [formData, setFormData] = useState({
        jobEmail: '',
        appPassword: '',
    });

    const [passwordData, setPasswordData] = useState({
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const menuRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Toggle menu and fetch data on open
    const toggleMenu = async () => {
        if (!isOpen) {
            setLoading(true);
            const result = await getUserSettings();
            if (result.success && result.data) {
                setFormData({
                    jobEmail: result.data.jobEmail || result.data.email || '',
                    appPassword: result.data.appPassword || ''
                });
                if (result.data.resume) {
                    setResumeInfo({
                        filename: result.data.resume.filename,
                        createdAt: new Date(result.data.resume.createdAt)
                    });
                }
            }
            setLoading(false);
        }
        setIsOpen(!isOpen);
        setError(null);
        setSuccess(null);
        setActiveTab('profile');
        setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
    };

    // Close on click outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [menuRef]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
    };

    const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setReplacingResume(true);
            setError(null);
            setSuccess(null);

            const data = new FormData();
            data.append("resume", file);

            try {
                const result = await replaceResume(data);
                if (result?.error) {
                    setError(result.error);
                } else {
                    setSuccess("Resume replaced successfully!");
                    setResumeInfo({
                        filename: file.name,
                        createdAt: new Date()
                    });
                }
            } catch (err) {
                setError("Failed to replace resume.");
            } finally {
                setReplacingResume(false);
                if (fileInputRef.current) fileInputRef.current.value = '';
            }
        }
    };


    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setError(null);
        setSuccess(null);

        try {
            const result = await saveEmailSettings(formData);
            if (result?.error) {
                setError(result.error);
            } else {
                setSuccess("Settings saved successfully!");
                setTimeout(() => setIsOpen(false), 2000);
            }
        } catch (err) {
            setError("Failed to save.");
        } finally {
            setSaving(false);
        }
    };

    const handlePasswordSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setError(null);
        setSuccess(null);

        if (passwordData.newPassword !== passwordData.confirmPassword) {
            setError("New passwords do not match");
            setSaving(false);
            return;
        }

        try {
            const result = await changePassword(passwordData);
            if (result?.error) {
                setError(result.error);
            } else {
                setSuccess("Password changed successfully!");
                setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
                setTimeout(() => setIsOpen(false), 2000);
            }
        } catch (err) {
            setError("Failed to change password.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div ref={menuRef} style={{ position: 'absolute', top: '1rem', left: '1rem', zIndex: 100 }}>
            {/* Settings Button */}
            <button
                onClick={toggleMenu}
                className="btn btn-outline"
                style={{
                    background: "rgba(0,0,0,0.5)",
                    backdropFilter: "blur(4px)",
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}
                disabled={loading}
            >
                <span>⚙️</span> Settings
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="card" style={{
                    position: 'absolute',
                    top: '110%',
                    left: 0,
                    width: '350px',
                    padding: '0',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
                    overflow: 'hidden'
                }}>
                    <div style={{ padding: '1rem 1.5rem 0.5rem', borderBottom: '1px solid #27272a' }}>
                        <h3 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
                            Settings
                        </h3>
                        {/* Tabs */}
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button
                                onClick={() => { setActiveTab('profile'); setError(null); setSuccess(null); }}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    padding: '0.5rem 0',
                                    color: activeTab === 'profile' ? '#fff' : '#a1a1aa',
                                    borderBottom: activeTab === 'profile' ? '2px solid #6366f1' : '2px solid transparent',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                Profile
                            </button>
                            <button
                                onClick={() => { setActiveTab('security'); setError(null); setSuccess(null); }}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    padding: '0.5rem 0',
                                    color: activeTab === 'security' ? '#fff' : '#a1a1aa',
                                    borderBottom: activeTab === 'security' ? '2px solid #6366f1' : '2px solid transparent',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                Security
                            </button>
                        </div>
                    </div>

                    <div style={{ padding: '1.5rem' }}>
                        {loading ? (
                            <p style={{ color: '#a1a1aa', textAlign: 'center' }}>Loading...</p>
                        ) : (
                            <>
                                {error && <div style={{ color: '#fca5a5', fontSize: '0.8rem', marginBottom: '1rem', padding: '0.5rem', background: 'rgba(239,68,68,0.1)', borderRadius: '4px' }}>{error}</div>}
                                {success && <div style={{ color: '#86efac', fontSize: '0.8rem', marginBottom: '1rem', padding: '0.5rem', background: 'rgba(34,197,94,0.1)', borderRadius: '4px' }}>{success}</div>}

                                {activeTab === 'profile' ? (
                                    <>
                                        {/* Resume Section */}
                                        <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem' }}>
                                            <label className="label" style={{ fontSize: '0.9rem', marginBottom: '0.5rem', display: 'block' }}>Current Resume</label>
                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(255,255,255,0.03)', padding: '0.5rem', borderRadius: '6px' }}>
                                                <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: '0.5rem' }}>
                                                    {resumeInfo ? (
                                                        <span style={{ fontSize: '0.8rem', color: '#fff' }}>📄 {resumeInfo.filename}</span>
                                                    ) : (
                                                        <span style={{ fontSize: '0.8rem', color: '#a1a1aa' }}>No resume found</span>
                                                    )}
                                                </div>

                                                <input
                                                    type="file"
                                                    ref={fileInputRef}
                                                    onChange={handleResumeUpload}
                                                    style={{ display: 'none' }}
                                                    accept=".pdf,.doc,.docx"
                                                />

                                                <button
                                                    onClick={() => fileInputRef.current?.click()}
                                                    className="btn btn-outline"
                                                    style={{ fontSize: '0.7rem', padding: '0.25rem 0.5rem', height: 'auto' }}
                                                    disabled={replacingResume}
                                                >
                                                    {replacingResume ? '...' : (resumeInfo ? 'Replace' : 'Upload')}
                                                </button>
                                            </div>
                                        </div>

                                        {/* Email Form */}
                                        <form onSubmit={handleSubmit}>
                                            <div className="input-group" style={{ marginBottom: '1rem' }}>
                                                <label className="label" style={{ fontSize: '0.8rem' }}>Job Email</label>
                                                <input
                                                    type="email"
                                                    name="jobEmail"
                                                    className="input"
                                                    value={formData.jobEmail}
                                                    onChange={handleChange}
                                                    placeholder="jobs@example.com"
                                                    style={{ padding: '0.5rem' }}
                                                />
                                            </div>

                                            <div className="input-group" style={{ marginBottom: '1.5rem' }}>
                                                <label className="label" style={{ fontSize: '0.8rem' }}>App Password</label>
                                                <input
                                                    type="password"
                                                    name="appPassword"
                                                    className="input"
                                                    value={formData.appPassword}
                                                    onChange={handleChange}
                                                    placeholder="App Password"
                                                    style={{ padding: '0.5rem' }}
                                                />
                                            </div>

                                            <button
                                                type="submit"
                                                className="btn btn-primary"
                                                style={{ width: '100%', padding: '0.5rem' }}
                                                disabled={saving}
                                            >
                                                {saving ? 'Saving...' : 'Update Settings'}
                                            </button>
                                        </form>
                                    </>
                                ) : (
                                    /* Security Tab */
                                    <form onSubmit={handlePasswordSubmit}>
                                        <div className="input-group" style={{ marginBottom: '1rem' }}>
                                            <label className="label" style={{ fontSize: '0.8rem' }}>Current Password</label>
                                            <input
                                                type="password"
                                                name="oldPassword"
                                                className="input"
                                                value={passwordData.oldPassword}
                                                onChange={handlePasswordChange}
                                                placeholder="••••••••"
                                                style={{ padding: '0.5rem' }}
                                                required
                                            />
                                        </div>

                                        <div className="input-group" style={{ marginBottom: '1rem' }}>
                                            <label className="label" style={{ fontSize: '0.8rem' }}>New Password</label>
                                            <input
                                                type="password"
                                                name="newPassword"
                                                className="input"
                                                value={passwordData.newPassword}
                                                onChange={handlePasswordChange}
                                                placeholder="••••••••"
                                                style={{ padding: '0.5rem' }}
                                                required
                                                minLength={6}
                                            />
                                        </div>

                                        <div className="input-group" style={{ marginBottom: '1.5rem' }}>
                                            <label className="label" style={{ fontSize: '0.8rem' }}>Confirm New Password</label>
                                            <input
                                                type="password"
                                                name="confirmPassword"
                                                className="input"
                                                value={passwordData.confirmPassword}
                                                onChange={handlePasswordChange}
                                                placeholder="••••••••"
                                                style={{ padding: '0.5rem' }}
                                                required
                                                minLength={6}
                                            />
                                        </div>

                                        <button
                                            type="submit"
                                            className="btn btn-primary"
                                            style={{ width: '100%', padding: '0.5rem', background: '#dc2626' }}
                                            disabled={saving}
                                        >
                                            {saving ? 'Updating...' : 'Change Password'}
                                        </button>
                                    </form>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}


"use client";

import React, { useState } from 'react';
import { sendGreetingEmails } from '@/actions/vendor';

export default function VendorGreetingButton() {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const handleSend = async () => {
        setLoading(true);
        setMessage(null);
        try {
            const result = await sendGreetingEmails();
            if (result.success) {
                setMessage({ type: 'success', text: result.message || "Greetings are being sent in the background!" });
            } else {
                setMessage({ type: 'error', text: result.error || "Failed to send greetings." });
            }
        } catch (err) {
            setMessage({ type: 'error', text: "An unexpected error occurred." });
        } finally {
            setLoading(false);
            // Clear message after 5 seconds
            setTimeout(() => setMessage(null), 5000);
        }
    };

    return (
        <div
            className="card flex-center"
            style={{
                flexDirection: 'column',
                gap: '1rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                position: 'relative'
            }}
            onClick={!loading ? handleSend : undefined}
        >
            <div style={{ fontSize: '2rem' }}>{loading ? '⏳' : '👋'}</div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>
                {loading ? 'Sending...' : 'Greet Vendors'}
            </h2>
            <p style={{ color: '#a1a1aa', textAlign: 'center' }}>
                Send AI-powered greetings to all unique vendors
            </p>

            {message && (
                <div style={{
                    position: 'absolute',
                    bottom: '-40px',
                    left: '0',
                    right: '0',
                    padding: '0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    textAlign: 'center',
                    backgroundColor: message.type === 'success' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: message.type === 'success' ? '#86efac' : '#fca5a5',
                    border: `1px solid ${message.type === 'success' ? '#22c55e' : '#ef4444'}`,
                    zIndex: 10
                }}>
                    {message.text}
                </div>
            )}
        </div>
    );
}

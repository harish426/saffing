
import React, { useRef, useState } from 'react';
import { uploadResume } from '@/actions/onboarding';

interface Step2Props {
    formData: any;
    setFormData: (data: any) => void;
    nextStep: () => void;
    prevStep: () => void;
}

export default function Step2Resume({ formData, setFormData, nextStep, prevStep }: Step2Props) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFormData({ ...formData, resume: e.target.files[0] });
            setError(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.resume) {
            setError("Please select a resume file");
            return;
        }

        setUploading(true);
        setError(null);

        const data = new FormData();
        data.append("resume", formData.resume);

        try {
            const result = await uploadResume(data);
            if (result?.error) {
                setError(result.error);
            } else {
                nextStep();
            }
        } catch (err: any) {
            setError(err.message || "Upload failed. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="card" style={{ maxWidth: '500px', width: '100%', margin: '0 auto' }}>
            <h2 className="heading" style={{ fontSize: '2rem', marginBottom: '1rem' }}>Upload Resume</h2>
            <p style={{ textAlign: 'center', color: '#a1a1aa', marginBottom: '2rem' }}>
                Please upload your updated resume (PDF or DOCX).
            </p>

            {error && (
                <div style={{ padding: '0.5rem', background: 'rgba(239,68,68,0.2)', color: '#fca5a5', borderRadius: '4px', marginBottom: '1rem', textAlign: 'center' }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div
                    className="input-group"
                    style={{
                        border: '2px dashed var(--card-border)',
                        borderRadius: '12px',
                        padding: '2rem',
                        textAlign: 'center',
                        cursor: 'pointer',
                        background: 'rgba(255,255,255,0.02)'
                    }}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <input
                        type="file"
                        name="resume"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        accept=".pdf,.doc,.docx"
                        style={{ display: 'none' }}
                    />
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📄</div>
                    {formData.resume ? (
                        <div>
                            <p style={{ color: '#fff', fontWeight: 600 }}>{formData.resume.name}</p>
                            <p style={{ color: '#22c55e', fontSize: '0.9rem' }}>Ready to upload</p>
                        </div>
                    ) : (
                        <div>
                            <p style={{ color: '#fff', fontWeight: 600 }}>Click to Upload</p>
                            <p style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>PDF, DOCX up to 10MB</p>
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    {/* Back button disabled during upload to prevent state inconsistency */}
                    <button type="button" onClick={prevStep} className="btn btn-outline" style={{ flex: 1 }} disabled={uploading}>
                        Back
                    </button>
                    <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={uploading}>
                        {uploading ? 'Uploading...' : 'Next'}
                    </button>
                </div>
            </form>
        </div>
    );
}

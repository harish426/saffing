
"use client";

import React, { useState } from 'react';
import Step1Login from './Step1Login';
import Step2Resume from './Step2Resume';
import Step3Email from './Step3Email';

export default function MultiStepForm() {
    const [step, setStep] = useState(1);
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        resume: null,
        jobEmail: '',
        appPassword: ''
    });

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    return (
        <div style={{ width: '100%' }}>
            {/* Progress Indicators - Only show for Signup */}
            {!isLogin && (
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem', gap: '1rem' }}>
                    {[1, 2, 3].map((num) => (
                        <div
                            key={num}
                            style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '50%',
                                background: step >= num ? 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)' : 'rgba(255,255,255,0.1)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 600,
                                color: 'white',
                                opacity: step >= num ? 1 : 0.5,
                                transition: 'all 0.3s ease'
                            }}
                        >
                            {num}
                        </div>
                    ))}
                </div>
            )}

            {step === 1 && (
                <Step1Login
                    formData={formData}
                    setFormData={setFormData}
                    nextStep={nextStep}
                    isLogin={isLogin}
                    setIsLogin={setIsLogin}
                />
            )}
            {step === 2 && (
                <Step2Resume
                    formData={formData}
                    setFormData={setFormData}
                    nextStep={nextStep}
                    prevStep={prevStep}
                />
            )}
            {step === 3 && (
                <Step3Email
                    formData={formData}
                    setFormData={setFormData}
                    prevStep={prevStep}
                />
            )}
        </div>
    );
}

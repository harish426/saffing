"use client";

import Link from "next/link";
import JobForm from "../../components/JobForm";

export default function FillInPage() {

    return (
        <main className="container" style={{ justifyContent: 'flex-start', paddingTop: '4rem' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
                <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', color: '#a1a1aa' }}>
                    ← Back to Home
                </Link>

                <h1 className="heading" style={{ textAlign: 'left', marginBottom: '1rem' }}>New Staffing Entry</h1>
                <p style={{ color: '#a1a1aa', marginBottom: '3rem' }}>Please fill in the details below to create a new requirement.</p>

                <JobForm />
            </div >
        </main >
    );
}


"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import JobForm from "../../../components/JobForm";
import { getJobById } from "../../../../actions/fetchJobs";
import { useParams } from "next/navigation";

export default function ExistingEntryEditPage() {
    const params = useParams();
    const id = params.id as string;
    const [job, setJob] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchJob = async () => {
            if (!id) return;
            setLoading(true);
            const result = await getJobById(id);
            if (result.success) {
                setJob(result.data);
            } else {
                alert("Failed to load job details");
            }
            setLoading(false);
        };
        fetchJob();
    }, [id]);

    if (loading) {
        return <div style={{ color: '#a1a1aa', textAlign: 'center', marginTop: '4rem' }}>Loading...</div>;
    }

    if (!job) {
        return <div style={{ color: '#a1a1aa', textAlign: 'center', marginTop: '4rem' }}>Job not found.</div>;
    }

    return (
        <main className="container" style={{ justifyContent: 'flex-start', paddingTop: '4rem' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
                <Link href="/existing" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', color: '#a1a1aa' }}>
                    ← Back to Existing Entries
                </Link>

                <h1 className="heading" style={{ textAlign: 'left', marginBottom: '1rem' }}>Edit Entry</h1>

                <JobForm initialData={job} isEditMode={true} />
            </div >
        </main >
    );
}

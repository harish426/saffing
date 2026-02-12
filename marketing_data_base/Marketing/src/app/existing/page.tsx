
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getJobDescriptions } from "../../../actions/fetchJobs";
import { deleteJob } from "../../../actions/deleteJob";
import { toggleJobActive } from "../../../actions/toggleActive";
import { sendResume } from "../../../actions/sendResume";
import { updateJobProgress } from "../../../actions/updateJob";

interface JobDescription {
    id: string;
    company: string | null;
    jobRole: string | null;
    jobDescription: string | null;
    vendorName: string | null;
    vendorContact: string | null;
    vendorEmail: string | null;
    careerLink: string | null;
    location: string | null;
    submissionDetails: string | null;
    requirementSource: string | null;
    progress: string;
    isActive: boolean;
    createdAt: Date;
}

export default function ExistingDetailsPage() {
    const [jobs, setJobs] = useState<JobDescription[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'new' | 'progress'>('new');
    const [filters, setFilters] = useState({
        startDate: "",
        endDate: "",
        searchQuery: "",
        filterActive: false,
        filterPhone: false,
        filterEmail: false,
    });

    const [showFilters, setShowFilters] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        const result = await getJobDescriptions(
            filters.startDate || undefined,
            filters.endDate || undefined,
            filters.searchQuery || undefined,
            filters.filterActive,
            filters.filterPhone,
            filters.filterEmail,
            activeTab
        );
        if (result.success && result.data) {
            setJobs(result.data as any);
        } else {
            alert("Failed to load entries");
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchData();
    }, [filters, activeTab]);

    const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;
        setFilters({
            ...filters,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleDelete = async (id: string) => {
        if (confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
            const result = await deleteJob(id);
            if (result.success) {
                setJobs(jobs.filter(job => job.id !== id));
            } else {
                alert(result.message || 'Failed to delete');
            }
        }
    };

    const handleToggle = async (id: string, currentStatus: boolean) => {
        const newStatus = !currentStatus;
        setJobs(jobs.map(job => job.id === id ? { ...job, isActive: newStatus } : job));

        const result = await toggleJobActive(id, newStatus);
        if (result.success) {
            fetchData();
        } else {
            setJobs(jobs.map(job => job.id === id ? { ...job, isActive: currentStatus } : job));
            alert('Failed to update status');
        }
    };

    const handleSend = async (job: JobDescription) => {
        if (confirm(`Are you sure you want to send resume for ${job.jobRole} at ${job.company}?`)) {
            const result = await sendResume({
                vendorEmail: job.vendorEmail,
                jobRole: job.jobRole,
                jobDescription: job.jobDescription,
                vendorName: job.vendorName
            });

            if (result.success) {
                alert(`Email sent successfully! Status: ${result.data.status}`);
            } else {
                alert(`Failed to send email. ${result.message}`);
            }
        }
    };

    const handleProgressChange = async (id: string, newProgress: string) => {
        if (newProgress === 'Vendor Rejected') {
            if (!confirm('Setting status to "Vendor Rejected" will DELETE this entry. Are you sure?')) {
                return;
            }
        }

        // Optimistic update
        if (newProgress === 'Vendor Rejected') {
            setJobs(jobs.filter(job => job.id !== id));
        } else {
            // If moving from None to something else, it should disappear from 'New' tab
            if (activeTab === 'new' && newProgress !== 'None') {
                setJobs(jobs.filter(job => job.id !== id));
            } else {
                setJobs(jobs.map(job => job.id === id ? { ...job, progress: newProgress } : job));
            }
        }

        const result = await updateJobProgress(id, newProgress);

        if (!result.success) {
            alert(result.message || 'Failed to update progress');
            fetchData(); // Revert
        } else {
            // If action was updated, maybe we need to refresh if logic was complex, but optimistic should hold
            if (result.action === 'deleted') {
                // already handled
            }
        }
    };

    return (
        <main className="container" style={{ justifyContent: 'flex-start', paddingTop: '4rem' }}>
            <div style={{ width: '100%' }}>

                {/* Header Section */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                        <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: '#a1a1aa' }}>
                            ← Back to Home
                        </Link>
                        <h1 className="heading" style={{ textAlign: 'left', fontSize: '2.5rem', marginBottom: 0 }}>
                            Existing Entries
                            {!loading && <span style={{ fontSize: '1.5rem', color: '#a1a1aa', marginLeft: '1rem', fontWeight: 400 }}>({jobs.length})</span>}
                        </h1>
                    </div>

                    {/* Filters Section */}
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'end', flexWrap: 'wrap' }}>
                        {/* Search Bar */}
                        <div>
                            <label className="label" htmlFor="searchQuery">Search</label>
                            <input
                                type="text"
                                id="searchQuery"
                                name="searchQuery"
                                className="input"
                                placeholder="Vendor or Company"
                                style={{ padding: '0.5rem', minWidth: '250px' }}
                                value={filters.searchQuery}
                                onChange={handleFilterChange}
                            />
                        </div>
                        <div className="card" style={{ padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'end' }}>
                            <div>
                                <label className="label" htmlFor="startDate">From Date</label>
                                <input
                                    type="date"
                                    id="startDate"
                                    name="startDate"
                                    className="input"
                                    style={{ padding: '0.5rem' }}
                                    value={filters.startDate}
                                    onChange={handleFilterChange}
                                />
                            </div>
                            <div>
                                <label className="label" htmlFor="endDate">To Date</label>
                                <input
                                    type="date"
                                    id="endDate"
                                    name="endDate"
                                    className="input"
                                    style={{ padding: '0.5rem' }}
                                    value={filters.endDate}
                                    onChange={handleFilterChange}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Advanced Filters Button and Popover */}
                    <div style={{ position: 'relative' }}>
                        <button
                            className="btn-secondary"
                            onClick={() => setShowFilters(!showFilters)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '0.75rem 1.25rem',
                                backgroundColor: showFilters ? '#333' : '#18181b',
                                border: '1px solid #3f3f46',
                                borderRadius: '8px',
                                color: '#e4e4e7',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                            }}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
                            </svg>
                            Filters
                            {(filters.filterActive || filters.filterPhone || filters.filterEmail) && (
                                <span style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    backgroundColor: '#6366f1',
                                    color: 'white',
                                    borderRadius: '50%',
                                    width: '20px',
                                    height: '20px',
                                    fontSize: '0.75rem',
                                    marginLeft: '0.5rem'
                                }}>
                                    {[filters.filterActive, filters.filterPhone, filters.filterEmail].filter(Boolean).length}
                                </span>
                            )}
                        </button>

                        {showFilters && (
                            <div style={{
                                position: 'absolute',
                                top: 'calc(100% + 0.5rem)',
                                right: 0,
                                zIndex: 50,
                                backgroundColor: '#18181b',
                                border: '1px solid #3f3f46',
                                borderRadius: '12px',
                                padding: '1.5rem',
                                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                                minWidth: '300px',
                            }}>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#e4e4e7', fontSize: '1rem', fontWeight: 600 }}>Filter Entries</h4>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    {/* Active Filter Switch */}
                                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', userSelect: 'none' }}>
                                        <span style={{ color: '#d4d4d8' }}>Active Only</span>
                                        <div style={{ position: 'relative', width: '44px', height: '24px' }}>
                                            <input
                                                type="checkbox"
                                                name="filterActive"
                                                checked={filters.filterActive}
                                                onChange={handleFilterChange}
                                                style={{ opacity: 0, width: 0, height: 0 }}
                                            />
                                            <span style={{
                                                position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                                                backgroundColor: filters.filterActive ? '#6366f1' : '#3f3f46',
                                                borderRadius: '34px',
                                                transition: '0.3s'
                                            }}></span>
                                            <span style={{
                                                position: 'absolute', content: '""', height: '18px', width: '18px',
                                                left: filters.filterActive ? '23px' : '3px', bottom: '3px',
                                                backgroundColor: 'white', borderRadius: '50%', transition: '0.3s'
                                            }}></span>
                                        </div>
                                    </label>

                                    {/* Phone Filter Switch */}
                                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', userSelect: 'none' }}>
                                        <span style={{ color: '#d4d4d8' }}>Has Phone Number</span>
                                        <div style={{ position: 'relative', width: '44px', height: '24px' }}>
                                            <input
                                                type="checkbox"
                                                name="filterPhone"
                                                checked={filters.filterPhone}
                                                onChange={handleFilterChange}
                                                style={{ opacity: 0, width: 0, height: 0 }}
                                            />
                                            <span style={{
                                                position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                                                backgroundColor: filters.filterPhone ? '#6366f1' : '#3f3f46',
                                                borderRadius: '34px',
                                                transition: '0.3s'
                                            }}></span>
                                            <span style={{
                                                position: 'absolute', content: '""', height: '18px', width: '18px',
                                                left: filters.filterPhone ? '23px' : '3px', bottom: '3px',
                                                backgroundColor: 'white', borderRadius: '50%', transition: '0.3s'
                                            }}></span>
                                        </div>
                                    </label>

                                    {/* Email Filter Switch */}
                                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', userSelect: 'none' }}>
                                        <span style={{ color: '#d4d4d8' }}>Has Email</span>
                                        <div style={{ position: 'relative', width: '44px', height: '24px' }}>
                                            <input
                                                type="checkbox"
                                                name="filterEmail"
                                                checked={filters.filterEmail}
                                                onChange={handleFilterChange}
                                                style={{ opacity: 0, width: 0, height: 0 }}
                                            />
                                            <span style={{
                                                position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                                                backgroundColor: filters.filterEmail ? '#6366f1' : '#3f3f46',
                                                borderRadius: '34px',
                                                transition: '0.3s'
                                            }}></span>
                                            <span style={{
                                                position: 'absolute', content: '""', height: '18px', width: '18px',
                                                left: filters.filterEmail ? '23px' : '3px', bottom: '3px',
                                                backgroundColor: 'white', borderRadius: '50%', transition: '0.3s'
                                            }}></span>
                                        </div>
                                    </label>

                                    <div style={{ height: '1px', backgroundColor: '#3f3f46', margin: '0.5rem 0' }}></div>

                                    <button
                                        onClick={() => setFilters({ ...filters, filterActive: false, filterPhone: false, filterEmail: false })}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            color: '#a1a1aa',
                                            fontSize: '0.875rem',
                                            cursor: 'pointer',
                                            textAlign: 'center',
                                            textDecoration: 'underline'
                                        }}
                                    >
                                        Clear Filters
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Tabs */}
                <div style={{ display: 'flex', borderBottom: '1px solid #3f3f46', marginBottom: '2rem' }}>
                    <button
                        onClick={() => setActiveTab('new')}
                        style={{
                            padding: '0.75rem 1.5rem',
                            background: 'none',
                            border: 'none',
                            borderBottom: activeTab === 'new' ? '2px solid #6366f1' : '2px solid transparent',
                            color: activeTab === 'new' ? '#fff' : '#a1a1aa',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            fontWeight: 500,
                            transition: 'all 0.2s',
                        }}
                    >
                        New Entries
                    </button>
                    <button
                        onClick={() => setActiveTab('progress')}
                        style={{
                            padding: '0.75rem 1.5rem',
                            background: 'none',
                            border: 'none',
                            borderBottom: activeTab === 'progress' ? '2px solid #6366f1' : '2px solid transparent',
                            color: activeTab === 'progress' ? '#fff' : '#a1a1aa',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            fontWeight: 500,
                            transition: 'all 0.2s',
                        }}
                    >
                        In Progress
                    </button>
                </div>

                {/* Content Section */}
                {loading ? (
                    <div style={{ textAlign: 'center', color: '#a1a1aa', marginTop: '4rem' }}>Loading entries...</div>
                ) : jobs.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#a1a1aa', marginTop: '4rem' }}>No entries found for the selected criteria.</div>
                ) : (
                    <div style={{ display: 'grid', gap: '1.5rem' }}>
                        {jobs.map((job) => (
                            <JobCard key={job.id} job={job} onDelete={handleDelete} onToggle={handleToggle} onSend={handleSend} onProgressChange={handleProgressChange} />
                        ))}
                    </div>
                )}
            </div>
        </main>
    );
}

function JobCard({ job, onDelete, onToggle, onSend, onProgressChange }: { job: JobDescription, onDelete: (id: string) => void, onToggle: (id: string, status: boolean) => void, onSend: (job: JobDescription) => void, onProgressChange: (id: string, status: string) => void }) {
    const [expanded, setExpanded] = useState(false);
    const description = job.jobDescription || 'No description provided.';
    const isLong = description.length > 150;

    const progressOptions = [
        'None',
        'RTR filed',
        'Prime Vendor filed RTR',
        'Interview in progress',
        'Finally Approved',
        'Vendor Rejected'
    ];

    return (
        <div className={`card ${!job.isActive ? 'opacity-50' : ''}`} style={{ display: 'grid', gridTemplateColumns: 'min-content minmax(200px, 1fr) 2fr min-content', gap: '2rem', alignItems: 'start', transition: 'opacity 0.3s' }}>

            <div style={{ paddingTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <button
                    onClick={() => onDelete(job.id)}
                    style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#ef4444',
                        padding: '0.5rem',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'background 0.2s'
                    }}
                    className="delete-btn"
                    title="Delete Entry"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>

                <Link
                    href={`/edit/${job.id}`}
                    style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#fbbf24', // Amber/Yellow for edit
                        padding: '0.5rem',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'background 0.2s'
                    }}
                    title="Edit Entry"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </Link>
            </div>

            <div style={{ borderRight: '1px solid rgba(255,255,255,0.1)', paddingRight: '1rem' }}>
                <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: '#fff' }}>{job.company || 'N/A'}</h3>
                <div style={{ color: '#a1a1aa', fontWeight: 500, marginBottom: '0.25rem' }}>
                    {job.jobRole || 'N/A'}
                    {job.location && <span style={{ marginLeft: '0.5rem', fontSize: '0.875rem', color: '#71717a' }}>• {job.location}</span>}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6366f1', marginBottom: '1rem' }}>
                    {new Date(job.createdAt).toLocaleDateString()}
                </div>

                <div style={{ fontSize: '0.875rem', color: '#71717a' }}>
                    <div><span style={{ color: '#a1a1aa' }}>Vendor:</span> {job.vendorName || '-'}</div>
                    <div><span style={{ color: '#a1a1aa' }}>Phone:</span> {job.vendorContact || '-'}</div>
                    <div><span style={{ color: '#a1a1aa' }}>Email:</span> {job.vendorEmail || '-'}</div>
                    {job.submissionDetails && (
                        <div style={{ marginTop: '0.5rem', color: '#818cf8' }}>
                            <span style={{ color: '#a1a1aa' }}>Submitted:</span> {job.submissionDetails}
                        </div>
                    )}
                    {job.requirementSource && (
                        <div style={{ color: '#34d399' }}>
                            <span style={{ color: '#a1a1aa' }}>Source:</span> {job.requirementSource}
                        </div>
                    )}

                    <div style={{ marginTop: '1rem' }}>
                        <label style={{ display: 'block', color: '#a1a1aa', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Status</label>
                        <select
                            value={job.progress || 'None'}
                            onChange={(e) => onProgressChange(job.id, e.target.value)}
                            className="input"
                            style={{ padding: '0.25rem', fontSize: '0.8rem', width: '100%', backgroundColor: '#27272a', borderColor: '#3f3f46' }}
                        >
                            {progressOptions.map(option => (
                                <option key={option} value={option}>{option}</option>
                            ))}
                        </select>
                    </div>

                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                    <h4 style={{ fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#a1a1aa', marginBottom: '0.5rem' }}>Description</h4>
                    <p style={{ color: '#d4d4d8', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                        {expanded ? description : (isLong ? description.slice(0, 150) + '...' : description)}
                    </p>
                    {isLong && (
                        <button
                            onClick={() => setExpanded(!expanded)}
                            style={{ color: '#6366f1', background: 'none', border: 'none', padding: 0, marginTop: '0.5rem', cursor: 'pointer', fontSize: '0.875rem', textDecoration: 'underline' }}
                        >
                            {expanded ? 'Show Less' : 'Show More'}
                        </button>
                    )}
                </div>

                {job.careerLink && (
                    <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
                        <a href={job.careerLink} target="_blank" rel="noopener noreferrer" className="btn btn-primary" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
                            View Portal ↗
                        </a>
                    </div>
                )}
            </div>

            <div style={{ paddingTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
                <label style={{ position: 'relative', display: 'inline-block', width: '40px', height: '20px', cursor: 'pointer' }}>
                    <input
                        type="checkbox"
                        checked={job.isActive}
                        onChange={() => onToggle(job.id, job.isActive)}
                        style={{ opacity: 0, width: 0, height: 0 }}
                    />
                    <span style={{
                        position: 'absolute',
                        cursor: 'pointer',
                        top: 0, left: 0, right: 0, bottom: 0,
                        backgroundColor: job.isActive ? '#10b981' : '#3f3f46',
                        transition: '.4s',
                        borderRadius: '34px'
                    }}></span>
                    <span style={{
                        position: 'absolute',
                        content: '""',
                        height: '16px', width: '16px',
                        left: job.isActive ? '22px' : '2px',
                        bottom: '2px',
                        backgroundColor: 'white',
                        transition: '.4s',
                        borderRadius: '50%'
                    }}></span>
                </label>

                {job.isActive && (
                    <button
                        onClick={() => onSend(job)}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#3b82f6', // Telegram-ish blue
                            padding: '0.5rem',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'background 0.2s, transform 0.1s'
                        }}
                        className="send-btn"
                        title="Send Info"
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                )}
            </div>
        </div>
    );
}

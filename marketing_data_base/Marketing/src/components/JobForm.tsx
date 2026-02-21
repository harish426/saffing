"use client";

import { useState, FormEvent, useEffect } from "react";
import { saveJobDescription } from "../../actions/formsubmit";
import { useRouter } from "next/navigation";

interface JobFormProps {
    initialData?: any;
    isEditMode?: boolean;
}

export default function JobForm({ initialData, isEditMode = false }: JobFormProps) {
    const router = useRouter();
    const [formData, setFormData] = useState({
        id: "",
        company: "",
        jobRole: "",
        jobDescription: "",
        location: "",
        vendorName: "",
        vendorContact: "",
        vendorEmail: "",
        careerLink: "",
        submissionDetails: "",
        requirementSource: "",
        isActive: true,
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (initialData) {
            setFormData({
                id: initialData.id || "",
                company: initialData.company || "",
                jobRole: initialData.jobRole || "",
                jobDescription: initialData.jobDescription || "",
                location: initialData.location || "",
                vendorName: initialData.vendorName || "",
                vendorContact: initialData.vendorContact || "",
                vendorEmail: initialData.vendorEmail || "",
                careerLink: initialData.careerLink || "",
                submissionDetails: initialData.submissionDetails || "",
                requirementSource: initialData.requirementSource || "",
                isActive: initialData.isActive ?? true,
            });
        }
    }, [initialData]);

    const [downloadableResume, setDownloadableResume] = useState<{ base64: string, filename: string } | null>(null);

    const handleDownload = () => {
        if (!downloadableResume) return;

        // Convert Base64 to Blob
        const byteCharacters = atob(downloadableResume.base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = downloadableResume.filename;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // Disable button after download
        setDownloadableResume(null);
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setDownloadableResume(null); // Reset previous download

        try {
            const result = await saveJobDescription(formData);

            if (result.success) {
                // Check if we received a downloadable resume
                if (result.emailResult && result.emailResult.resumeBase64) {
                    setDownloadableResume({
                        base64: result.emailResult.resumeBase64,
                        filename: result.emailResult.filename || "resume.docx"
                    });
                    alert("Entry saved! Resume is ready for download.");
                }
                else if (result.emailResult && !result.emailResult.success) {
                    alert("Data saved but email not sent. " + (result.emailResult.message || ""));
                } else {
                    alert(isEditMode ? "Entry updated successfully!" : "Entry saved successfully!");
                }

                if (isEditMode) {
                    router.push("/existing");
                } else {
                    // Reset form only in create mode
                    // BUT keep the ID if we want to allow editing? 
                    // Actually standard behavior is reset. 
                    // If we have a download, we might want to keep the form state or at least the download button active?
                    // The user said: "after user download it just disable it again"
                    // If I reset the form, the download button might disappear if it depends on form state? 
                    // No, download button state is separate.

                    setFormData({
                        id: "",
                        company: "",
                        jobRole: "",
                        jobDescription: "",
                        location: "",
                        vendorName: "",
                        vendorContact: "",
                        vendorEmail: "",
                        careerLink: "",
                        submissionDetails: "",
                        requirementSource: "",
                        isActive: true,
                    });
                }
            } else {
                alert("Error: " + result.message);
            }
        } catch (err) {
            console.error(err);
            alert("An unexpected error occurred.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    return (
        <form onSubmit={handleSubmit} className="card" style={{ padding: '3rem', position: 'relative' }}>
            {/* Download Resume Button (Only visible when resume is ready) */}
            <button
                type="button"
                onClick={handleDownload}
                disabled={!downloadableResume}
                className="btn"
                style={{
                    position: "absolute",
                    top: "1rem",
                    right: "1rem",
                    padding: "0.5rem 1rem",
                    fontSize: "0.9rem",
                    zIndex: 100,
                    backgroundColor: downloadableResume ? "#22c55e" : "#52525b", // Green if ready, Gray if disabled
                    color: "white",
                    cursor: downloadableResume ? "pointer" : "not-allowed",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    transition: "all 0.2s"
                }}
            >
                <span>⬇️</span>
                {downloadableResume ? "Download Resume" : "Resume Not Ready"}
            </button>

            <div className="grid-2" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Left Column: Job Details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>Job Details</h3>

                    <div>
                        <label className="label" htmlFor="company">Company</label>
                        <input className="input" type="text" id="company" name="company" value={formData.company} onChange={handleChange} placeholder="e.g. Acme Corp" />
                    </div>

                    <div>
                        <label className="label" htmlFor="jobRole">Job Role</label>
                        <input className="input" type="text" id="jobRole" name="jobRole" value={formData.jobRole} onChange={handleChange} placeholder="e.g. Senior Developer" />
                    </div>

                    <div>
                        <label className="label" htmlFor="careerLink">Job Career Portal Link</label>
                        <input type="url" className="input" id="careerLink" name="careerLink" value={formData.careerLink} onChange={handleChange} placeholder="https://..." />
                    </div>

                    <div>
                        <label className="label" htmlFor="location">Location</label>
                        <input className="input" type="text" id="location" name="location" value={formData.location} onChange={handleChange} placeholder="e.g. New York, Remote" />
                    </div>

                    <div>
                        <label className="label" htmlFor="jobDescription">Job Description</label>
                        <textarea className="textarea" id="jobDescription" name="jobDescription" value={formData.jobDescription} onChange={handleChange} rows={5} placeholder="Brief description..." />
                    </div>
                </div>

                {/* Right Column: Vendor Details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>Vendor Details</h3>

                    <div>
                        <label className="label" htmlFor="vendorName">Vendor Name</label>
                        <input className="input" type="text" id="vendorName" name="vendorName" value={formData.vendorName} onChange={handleChange} placeholder="Vendor Company Name" />
                    </div>

                    <div>
                        <label className="label" htmlFor="vendorContact">Vendor Phone Number</label>
                        <input className="input" type="text" id="vendorContact" name="vendorContact" value={formData.vendorContact} onChange={handleChange} placeholder="e.g. +1 234 567 890" />
                    </div>

                    <div>
                        <label className="label" htmlFor="vendorEmail">Vendor Email</label>
                        <input type="email" className="input" id="vendorEmail" name="vendorEmail" value={formData.vendorEmail} onChange={handleChange} placeholder="name@vendor.com" />
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                <div>
                    <label className="label" htmlFor="submissionDetails">Submission Details</label>
                    <input
                        className="input"
                        type="text"
                        id="submissionDetails"
                        name="submissionDetails"
                        value={formData.submissionDetails}
                        onChange={handleChange}
                        placeholder="e.g. Submitted by recruiter"
                    />
                </div>

                <div>
                    <label className="label" htmlFor="requirementSource">Requirement Source</label>
                    <select
                        className="input"
                        id="requirementSource"
                        name="requirementSource"
                        value={formData.requirementSource}
                        onChange={handleChange}
                        style={{ width: '100%', padding: '0.75rem', backgroundColor: '#27272a', border: '1px solid #3f3f46', borderRadius: '8px', color: '#fff' }}
                    >
                        <option value="" disabled>Select Source</option>
                        <option value="Me">Me</option>
                        <option value="Reqruiters">Reqruiter</option>
                    </select>
                </div>
            </div>

            <div style={{ marginTop: '3rem', display: 'flex', justifyContent: 'flex-end' }}>
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : (isEditMode ? "Update Entry" : "Submit Entry")}
                </button>
            </div>

        </form>
    );
}

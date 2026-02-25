'use server';

import { verifySession } from '../src/lib/auth';

export async function sendResume(jobData: {
    vendorEmail: string | null;
    jobRole: string | null;
    jobDescription: string | null;
    vendorName: string | null;
}) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized: Please log in' };
        }

        const { vendorEmail, jobRole, jobDescription, vendorName } = jobData;
        console.log("Server Action sendResume called with:", { vendorEmail, vendorName, userId: session.id });

        // Basic validation - vendorEmail and vendorName are now OPTIONAL for download flow
        if (!jobRole || !jobDescription) {
            return { success: false, message: 'Missing required fields (Job Role or Description)' };
        }

        const params = new URLSearchParams({
            user_id: session.id,
            vendorEmail: vendorEmail || '',
            jobRole: jobRole,
            jobDescription: jobDescription,
            vendorName: vendorName || ''
        });

        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8001';
        const url = `${backendUrl}/send_resume?${params.toString()}`;
        console.log("Fetching URL:", url);

        const response = await fetch(url, {
            method: 'GET',
            cache: 'no-store'
        });

        if (response.status != 404) {
            // Check content type to see if it's JSON or File
            const contentType = response.headers.get("content-type");

            if (contentType && contentType.includes("application/json")) {
                const result = await response.json();
                return { success: true, data: result };
            } else {
                // Assume it's a file (blob)
                console.log("Received binary response from backend");
                const arrayBuffer = await response.arrayBuffer();
                const buffer = Buffer.from(arrayBuffer);
                const base64 = buffer.toString('base64');

                // Get filename from header if possible
                const disposition = response.headers.get('content-disposition');
                let filename = 'resume.docx';
                if (disposition && disposition.includes('filename=')) {
                    filename = disposition.split('filename=')[1].replace(/"/g, '');
                }

                return {
                    success: true,
                    resumeBase64: base64,
                    filename: filename
                };
            }

        } else {
            return { success: false, message: `Backend returned ${response.status}` };
        }
    } catch (error: any) {
        console.error('Failed to trigger backend:', error);
        return { success: false, message: error.message };
    }
}

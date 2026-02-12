'use server'

export async function sendResume(jobData: {
    vendorEmail: string | null;
    jobRole: string | null;
    jobDescription: string | null;
    vendorName: string | null;
}) {
    try {
        const { vendorEmail, jobRole, jobDescription, vendorName } = jobData;
        console.log("Server Action sendResume called with:", { vendorEmail, vendorName });

        // Basic validation
        if (!vendorEmail || !jobRole || !jobDescription || !vendorName) {
            return { success: false, message: 'Missing required fields (Vendor Email, Job Role, Description, or Vendor Name)' };
        }

        const params = new URLSearchParams({
            vendorEmail: vendorEmail,
            jobRole: jobRole,
            jobDescription: jobDescription,
            vendorName: vendorName
        });

        const url = `http://127.0.0.1:8001/send_resume?${params.toString()}`;
        console.log("Fetching URL:", url);

        const response = await fetch(url, {
            method: 'GET',
            cache: 'no-store'
        });
        if (response.status != 404) {
            const result = await response.json();
            return { success: true, data: result };
        } else {
            return { success: false, message: `Backend returned ${response.status}` };
        }
    } catch (error: any) {
        console.error('Failed to trigger backend:', error);
        return { success: false, message: error.message };
    }
}

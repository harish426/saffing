
'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'
import { verifySession } from '@/lib/auth'

export async function saveJobDescription(formData: any) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized' };
        }

        const {
            company,
            jobRole,
            jobDescription,
            location,
            vendorName,
            vendorContact,
            vendorEmail,
            careerLink,
            submissionDetails,
            requirementSource,
            isActive,
        } = formData


        if (formData.id) {
            // Update existing entry - Ensure Ownership
            const result = await prisma.jobDescription.updateMany({
                where: {
                    id: formData.id,
                    userId: session.id
                },
                data: {
                    company,
                    jobRole,
                    jobDescription,
                    location,
                    vendorName,
                    vendorContact,
                    vendorEmail,
                    careerLink,
                    submissionDetails,
                    requirementSource,
                    isActive: isActive ?? true,
                },
            });

            if (result.count === 0) {
                return { success: false, message: 'Job not found or unauthorized' };
            }

            const newJob = await prisma.jobDescription.findUnique({ where: { id: formData.id } });

            revalidatePath('/');
            revalidatePath('/fillin');
            revalidatePath('/existing');

            return { success: true, data: newJob };
        } else {
            // Create new entry - Link to User
            const newJob = await prisma.jobDescription.create({
                data: {
                    company,
                    jobRole,
                    jobDescription,
                    location,
                    vendorName,
                    vendorContact,
                    vendorEmail,
                    careerLink,
                    submissionDetails,
                    requirementSource,
                    isActive: isActive ?? true,
                    userId: session.id, // <--- Link to User
                },
            });

            let emailResult = { status: 'unknown', message: '' };

            try {
                const params = new URLSearchParams({
                    vendorEmail: vendorEmail || '',
                    jobRole: jobRole || '',
                    jobDescription: jobDescription || '',
                    vendorName: vendorName || ''
                });
                const response = await fetch(`http://127.0.0.1:8000/send_resume?${params.toString()}`, {
                    method: 'GET',
                    cache: 'no-store'
                });
                if (response.ok) {
                    emailResult = await response.json();
                } else {
                    emailResult = { status: 'error', message: `Backend returned ${response.status}` };
                }
            } catch (error: any) {
                console.error('Failed to trigger backend:', error);
                emailResult = { status: 'error', message: error.message };
            }

            revalidatePath('/');
            revalidatePath('/fillin');
            revalidatePath('/existing');

            return { success: true, data: newJob, emailResult };
        }


    } catch (error: any) {
        console.error('Failed to save job description:', error)
        console.log(error)
        return { success: false, message: 'Failed to save entry: ' + error.message }
    }
}

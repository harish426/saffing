'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function saveJobDescription(formData: any) {
    try {
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

        // Basic validation relaxed
        // if (!company || !jobRole || !jobDescription || !vendorName || !vendorContact || !vendorEmail) {
        //     return { success: false, message: 'Missing required fields' }
        // }

        if (formData.id) {
            // Update existing entry
            const newJob = await prisma.jobDescription.update({
                where: { id: formData.id },
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




            revalidatePath('/');
            revalidatePath('/fillin');
            revalidatePath('/existing');
            return { success: true, data: newJob };
        } else {
            // Create new entry
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
                },
            });
            let emailResult = { status: 'unknown', message: '' };
            try {
                const params = new URLSearchParams({
                    vendorEmail: vendorEmail,
                    jobRole: jobRole,
                    jobDescription: jobDescription,
                    vendorName: vendorName
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

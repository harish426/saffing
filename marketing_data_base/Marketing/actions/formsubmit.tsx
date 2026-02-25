
'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'
import { verifySession } from '@/lib/auth'
import { sendResume } from './sendResume'

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

            let emailResult: { success: boolean; data?: any; message?: any; resumeBase64?: any; filename?: any } = { success: false, message: 'Pending' };

            emailResult = await sendResume({
                vendorEmail: vendorEmail || '',
                jobRole: jobRole || '',
                jobDescription: jobDescription || '',
                vendorName: vendorName || ''
            });

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

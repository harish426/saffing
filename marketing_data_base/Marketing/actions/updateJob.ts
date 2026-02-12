
'use server'

import prisma from '@/lib/prisma'
import { verifySession } from '@/lib/auth'
import { revalidatePath } from 'next/cache'

export async function updateJobProgress(id: string, progress: string) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized' };
        }

        // Verify ownership
        const job = await prisma.jobDescription.findFirst({
            where: { id, userId: session.id }
        });

        if (!job) {
            return { success: false, message: 'Job not found or access denied' };
        }

        if (progress === 'Vendor Rejected') {
            await prisma.jobDescription.delete({
                where: { id }
            });
            revalidatePath('/existing');
            return { success: true, action: 'deleted', message: 'Job entry deleted (Vendor Rejected)' };
        } else {
            await prisma.jobDescription.update({
                where: { id },
                data: { progress }
            });
            revalidatePath('/existing');
            return { success: true, action: 'updated', message: 'Progress updated' };
        }

    } catch (error) {
        console.error('Failed to update job progress:', error);
        return { success: false, message: 'Failed to update progress' };
    }
}


'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'
import { verifySession } from '@/lib/auth'

export async function toggleJobActive(id: string, isActive: boolean) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized' };
        }

        // Update verify ownership via where clause
        // updateMany is safer for this pattern than update
        const result = await prisma.jobDescription.updateMany({
            where: {
                id,
                userId: session.id
            },
            data: { isActive },
        })

        if (result.count === 0) {
            return { success: false, message: 'Job not found or unauthorized' }
        }

        revalidatePath('/existing')
        return { success: true }
    } catch (error) {
        console.error('Failed to toggle job status:', error)
        return { success: false, message: 'Failed to update status' }
    }
}

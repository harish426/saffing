
'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'
import { verifySession } from '@/lib/auth'

export async function deleteJob(id: string) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized' };
        }

        // Use deleteMany with userId + id to safely delete only own records
        // standard delete throws if record not found, deleteMany returns count
        const result = await prisma.jobDescription.deleteMany({
            where: {
                id,
                userId: session.id
            },
        })

        if (result.count === 0) {
            // Either doesn't exist or belongs to another user
            // We can return success to be idempotent or error
            return { success: false, message: 'Job not found or unauthorized' }
        }

        revalidatePath('/existing')
        return { success: true }
    } catch (error: any) {
        console.error('Failed to delete job:', error)
        return { success: false, message: 'Failed to delete entry' }
    }
}

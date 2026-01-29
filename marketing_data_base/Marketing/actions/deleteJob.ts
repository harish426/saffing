'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function deleteJob(id: string) {
    try {
        await prisma.jobDescription.delete({
            where: { id },
        })

        revalidatePath('/existing')
        return { success: true }
    } catch (error: any) {
        if (error.code === 'P2025') {
            // Record already deleted
            revalidatePath('/existing')
            return { success: true }
        }
        console.error('Failed to delete job:', error)
        return { success: false, message: 'Failed to delete entry' }
    }
}

'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function toggleJobActive(id: string, isActive: boolean) {
    try {
        await prisma.jobDescription.update({
            where: { id },
            data: { isActive },
        })

        revalidatePath('/existing')
        return { success: true }
    } catch (error) {
        console.error('Failed to toggle job status:', error)
        return { success: false, message: 'Failed to update status' }
    }
}

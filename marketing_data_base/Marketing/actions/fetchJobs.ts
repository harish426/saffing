
'use server'

import prisma from '@/lib/prisma'
import { verifySession } from '@/lib/auth'

export async function getJobDescriptions(
    startDate?: string,
    endDate?: string,
    searchQuery?: string,
    filterActive?: boolean,
    filterPhone?: boolean,
    filterEmail?: boolean,
    filterTab?: 'new' | 'progress'
) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized' };
        }

        const where: any = {
            userId: session.id
        }

        if (startDate && endDate) {
            where.createdAt = {
                ...where.createdAt,
                gte: new Date(`${startDate}T00:00:00`),
                lte: new Date(`${endDate}T23:59:59.999`),
            }
        } else if (startDate) {
            where.createdAt = {
                ...where.createdAt,
                gte: new Date(`${startDate}T00:00:00`),
                lte: new Date(`${startDate}T23:59:59.999`),
            }
        }

        if (searchQuery) {
            where.OR = [
                { vendorName: { contains: searchQuery, mode: 'insensitive' } },
                { company: { contains: searchQuery, mode: 'insensitive' } },
            ]
        }

        if (filterActive) {
            where.isActive = true;
        }

        if (filterPhone) {
            where.AND = [
                ...(where.AND || []),
                { vendorContact: { not: null } },
                { vendorContact: { not: '' } }
            ];
        }

        if (filterEmail) {
            where.AND = [
                ...(where.AND || []),
                { vendorEmail: { not: null } },
                { vendorEmail: { not: '' } }
            ];
        }

        if (filterTab === 'new') {
            where.progress = 'None';
        } else if (filterTab === 'progress') {
            where.progress = { not: 'None' };
        }

        const jobs = await prisma.jobDescription.findMany({
            where,
            orderBy: [
                { isActive: 'desc' },
                { createdAt: 'desc' },
            ],
        })

        return { success: true, data: jobs }
    } catch (error) {
        console.error('Failed to fetch job descriptions:', error)
        return { success: false, message: 'Failed to fetch entries' }
    }
}

export async function getJobById(id: string) {
    try {
        const session = await verifySession();
        if (!session) {
            return { success: false, message: 'Unauthorized' };
        }

        // Use findFirst to enforce userId check since id is the only unique field
        const job = await prisma.jobDescription.findFirst({
            where: {
                id,
                userId: session.id
            },
        });

        if (!job) {
            return { success: false, message: 'Job not found' };
        }

        return { success: true, data: job };
    } catch (error) {
        console.error('Failed to fetch job by id:', error);
        return { success: false, message: 'Failed to fetch entry' };
    }
}

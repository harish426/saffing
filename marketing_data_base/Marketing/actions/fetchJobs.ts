'use server'

import prisma from '@/lib/prisma'

export async function getJobDescriptions(
    startDate?: string,
    endDate?: string,
    searchQuery?: string,
    filterActive?: boolean,
    filterPhone?: boolean,
    filterEmail?: boolean
) {
    try {
        const where: any = {}

        if (startDate && endDate) {
            // Range filter
            where.createdAt = {
                gte: new Date(`${startDate}T00:00:00`),
                lte: new Date(`${endDate}T23:59:59.999`),
            }
        } else if (startDate) {
            // Single day filter (start date to end of that day)
            where.createdAt = {
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

        // Apply additional filters
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
// Append new function
export async function getJobById(id: string) {
    try {
        const job = await prisma.jobDescription.findUnique({
            where: { id },
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

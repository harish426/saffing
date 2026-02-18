
"use server";

import prisma from "@/lib/prisma";
import { verifySession } from "@/lib/auth";
import { revalidatePath } from "next/cache";


export async function uploadResume(formData: FormData) {
    try {
        const session = await verifySession();
        if (!session) return { error: "Unauthorized" };

        const file = formData.get("resume") as File;
        if (!file) return { error: "No file uploaded" };

        // Basic validation
        if (file.size > 10 * 1024 * 1024) {
            return { error: "File size exceeds 10MB limit" };
        }

        const buffer = Buffer.from(await file.arrayBuffer());

        await prisma.resume.create({
            data: {
                userId: session.id,
                filename: file.name,
                mimeType: file.type,
                content: buffer,
            },
        });
        return { success: true };
    } catch (error: any) {
        console.error("Resume upload fatal error:", error);
        return { error: `Upload failed: ${error.message || "Unknown error"}` };
    }
}

export async function replaceResume(formData: FormData) {
    try {
        const session = await verifySession();
        if (!session) return { error: "Unauthorized" };

        const file = formData.get("resume") as File;
        if (!file) return { error: "No file uploaded" };

        // Basic validation
        if (file.size > 10 * 1024 * 1024) {
            return { error: "File size exceeds 10MB limit" };
        }

        const buffer = Buffer.from(await file.arrayBuffer());

        // Transaction: Delete old -> Create new
        const [_, newResume] = await prisma.$transaction([
            prisma.resume.deleteMany({ where: { userId: session.id } }),
            prisma.resume.create({
                data: {
                    userId: session.id,
                    filename: file.name,
                    mimeType: file.type,
                    content: buffer,
                },
            }),
        ]);

        // Trigger parsing efficiently (fire and forget or await depending on need)
        // We'll await it to ensure it starts processing
        try {
            await fetch(`http://127.0.0.1:8001/convert_resume_to_json?resume_id=${newResume.id}`, {
                method: "POST",
            });
            console.log("Triggered resume parsing for:", newResume.id);
        } catch (parseError) {
             console.error("Failed to trigger resume parsing:", parseError);
             // We don't fail the upload if parsing trigger fails, but we log it.
        }

        return { success: true };
    } catch (error: any) {
        console.error("Resume replace failed:", error);
        return { error: `Replace failed: ${error.message || "Unknown error"}` };
    }
}

export async function saveEmailSettings(formData: any) {
    try {
        const session = await verifySession();
        if (!session) return { error: "Unauthorized" };

        const { jobEmail, appPassword } = formData;

        await prisma.user.update({
            where: { id: session.id },
            data: {
                jobEmail,
                appPassword, // Note: Should be encrypted in production
            },
        });
        return { success: true };
    } catch (error: any) {
        console.error("Save settings error:", error);
        return { error: "Failed to save settings: " + error.message };
    }
}

export async function getUserSettings() {
    try {
        const session = await verifySession();
        if (!session) return { error: "Unauthorized" };

        const user = await prisma.user.findUnique({
            where: { id: session.id },
            select: { jobEmail: true, appPassword: true, email: true }
        });

        // Also fetch resume info
        const resume = await prisma.resume.findFirst({
            where: { userId: session.id },
            orderBy: { createdAt: 'desc' },
            select: { filename: true, createdAt: true }
        });

        if (!user) return { error: "User not found" };

        return { success: true, data: { ...user, resume } };
    } catch (error: any) {
        return { error: "Failed to fetch settings" };
    }
}

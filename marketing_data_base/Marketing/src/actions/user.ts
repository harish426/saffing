
"use server";

import { PrismaClient } from "@prisma/client";
import { verifySession, verifyPassword, hashPassword } from "@/lib/auth";

const prisma = new PrismaClient();

export async function changePassword(formData: any) {
    try {
        const session = await verifySession();
        if (!session) return { error: "Unauthorized" };

        const { oldPassword, newPassword, confirmPassword } = formData;

        if (!oldPassword || !newPassword || !confirmPassword) {
            return { error: "All fields are required" };
        }

        if (newPassword !== confirmPassword) {
            return { error: "New passwords do not match" };
        }

        if (newPassword.length < 6) {
            return { error: "Password must be at least 6 characters" };
        }

        // Fetch user to get current password hash
        const user = await prisma.user.findUnique({
            where: { id: session.id },
        });

        if (!user) return { error: "User not found" };

        // Verify old password
        const isValid = await verifyPassword(oldPassword, user.password);
        if (!isValid) {
            return { error: "Incorrect current password" };
        }

        // Hash new password and update
        const hashedPassword = await hashPassword(newPassword);

        await prisma.user.update({
            where: { id: session.id },
            data: { password: hashedPassword },
        });

        return { success: true };
    } catch (error: any) {
        console.error("Change password error:", error);
        return { error: "Failed to update password" };
    }
}

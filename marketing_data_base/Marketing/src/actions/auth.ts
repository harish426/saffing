
"use server";

import prisma from "@/lib/prisma";
import { hashPassword, verifyPassword, createSession, logout } from "@/lib/auth";



export async function registerUser(formData: any) {
    const { name, email, password } = formData;

    if (!name || !email || !password) {
        return { error: "Missing required fields" };
    }

    // Check if user exists
    const existingUser = await prisma.user.findUnique({
        where: { email },
    });

    if (existingUser) {
        return { error: "Email already in use" };
    }

    const hashedPassword = await hashPassword(password);

    const newUser = await prisma.user.create({
        data: {
            name,
            email,
            password: hashedPassword,
        },
    });

    await createSession(newUser.id);
    // Return success to let client handle transition
    return { success: true };
}

export async function loginUser(formData: any) {
    const { email, password } = formData;

    const user = await prisma.user.findUnique({
        where: { email },
    });

    if (!user || !(await verifyPassword(password, user.password))) {
        return { error: "Invalid credentials" };
    }

    await createSession(user.id);
    // Return success instead of redirecting to avoid try/catch issues
    return { success: true };
}


export async function logoutUser() {
    await logout();
    return { success: true };
}

import { SignJWT, jwtVerify } from "jose";
import { sendPasswordResetEmail } from "@/lib/mail";

const SECRET_KEY = process.env.JWT_SECRET || "super-secret-key-change-this";
const key = new TextEncoder().encode(SECRET_KEY);

export async function forgotPassword(email: string) {
    const user = await prisma.user.findUnique({
        where: { email },
    });

    if (!user) {
        // Return success even if user not found to prevent enumeration
        return { success: true };
    }

    // Generate a signed JWT token valid for 1 hour
    const token = await new SignJWT({ email, type: 'reset' })
        .setProtectedHeader({ alg: 'HS256' })
        .setIssuedAt()
        .setExpirationTime('1h')
        .sign(key);

    await sendPasswordResetEmail(email, token);
    return { success: true };
}

export async function resetPassword(token: string, newPassword: string) {
    try {
        const { payload } = await jwtVerify(token, key, {
            algorithms: ['HS256'],
        });

        if (payload.type !== 'reset' || !payload.email) {
            return { error: "Invalid token" };
        }

        const email = payload.email as string;

        const hashedPassword = await hashPassword(newPassword);

        await prisma.user.update({
            where: { email },
            data: { password: hashedPassword },
        });

        return { success: true };
    } catch (error) {
        return { error: "Invalid or expired token" };
    }
}

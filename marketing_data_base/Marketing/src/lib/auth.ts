
import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";
import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";

const prisma = new PrismaClient();
const SECRET_KEY = process.env.JWT_SECRET || "super-secret-key-change-this";
const key = new TextEncoder().encode(SECRET_KEY);

export async function hashPassword(password: string) {
    return await bcrypt.hash(password, 10);
}

export async function verifyPassword(password: string, hash: string) {
    return await bcrypt.compare(password, hash);
}

export async function createSession(userId: string) {
    const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
    const sessionToken = await new SignJWT({ userId })
        .setProtectedHeader({ alg: "HS256" })
        .setIssuedAt()
        .setExpirationTime("7d")
        .sign(key);

    // Store session in DB
    await prisma.session.create({
        data: {
            userId,
            sessionToken,
            expires,
        },
    });

    // Set Cookie
    const cookieStore = await cookies();
    cookieStore.set("session", sessionToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        expires,
        sameSite: "lax",
        path: "/",
    });
}

export async function verifySession() {
    const cookieStore = await cookies();
    const sessionToken = cookieStore.get("session")?.value;

    if (!sessionToken) return null;

    try {
        const { payload } = await jwtVerify(sessionToken, key, {
            algorithms: ["HS256"],
        });

        // Check DB for active session
        const session = await prisma.session.findUnique({
            where: { sessionToken },
            include: { user: true },
        });

        if (!session || session.expires < new Date()) {
            return null;
        }

        return session.user;
    } catch (error) {
        return null;
    }
}

export async function logout() {
    const cookieStore = await cookies();
    const sessionToken = cookieStore.get("session")?.value;

    if (sessionToken) {
        await prisma.session.deleteMany({
            where: { sessionToken },
        });
    }

    cookieStore.delete("session");
}

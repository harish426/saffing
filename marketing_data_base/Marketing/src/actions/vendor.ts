
"use server";

import { verifySession } from "@/lib/auth";

export async function sendGreetingEmails() {
    try {
        const user = await verifySession();
        if (!user) {
            return { error: "Unauthorized. Please log in again." };
        }

        const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
        const url = `${backendUrl}/send-greeting-to-all-vendors?user_email=${encodeURIComponent(user.email)}`;

        const response = await fetch(url);
        const data = await response.json();

        if (response.ok && data.status === "success") {
            return { success: true, message: data.message };
        } else {
            return { error: data.message || "Failed to trigger greeting emails." };
        }
    } catch (error: any) {
        console.error("sendGreetingEmails error:", error);
        return { error: "Connection to backend failed. Please ensure the backend server is running." };
    }
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { logoutUser } from "@/actions/auth";

export default function LogoutButton() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);

    const handleLogout = async () => {
        try {
            setLoading(true);
            await logoutUser();
            router.refresh(); // Clear server component cache
            router.push("/"); // Navigate to home
        } catch (error) {
            console.error("Logout failed:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleLogout}
            disabled={loading}
            className="btn btn-outline"
            style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                padding: "0.5rem 1rem",
                fontSize: "0.9rem",
                zIndex: 100,
                background: "rgba(0,0,0,0.5)",
                backdropFilter: "blur(4px)"
            }}
        >
            {loading ? "Signing out..." : "Sign Out"}
        </button>
    );
}


"use client";

import { logoutUser } from "@/actions/auth";

export default function LogoutButton() {
    return (
        <button
            onClick={() => logoutUser()}
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
            Sign Out
        </button>
    );
}

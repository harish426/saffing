
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
    const path = request.nextUrl.pathname;

    // Define protected routes
    const isProtectedRoute = path.startsWith('/dashboard') || path.startsWith('/onboarding');

    const sessionToken = request.cookies.get('session')?.value;

    if (isProtectedRoute && !sessionToken) {
        return NextResponse.redirect(new URL('/', request.url));
    }

    // NOTE: We intentionally do NOT redirect logged-in users away from '/'
    // because the signup flow is multi-step and creates a session after Step 1.
    // The page component itself handles redirect to /dashboard if already logged in.

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};

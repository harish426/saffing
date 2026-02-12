
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

    if (path === '/' && sessionToken) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};

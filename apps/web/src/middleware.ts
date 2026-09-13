import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const sessionCookie = request.cookies.get('kogniq_session');
  
  const requestHeaders = new Headers(request.headers);
  if (sessionCookie?.value && !requestHeaders.has('Authorization')) {
    requestHeaders.set('Authorization', `Bearer ${sessionCookie.value}`);
  }

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: '/api/:path*',
};

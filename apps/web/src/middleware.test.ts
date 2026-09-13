import { NextRequest, NextResponse } from 'next/server';
import { middleware, config } from './middleware';
import { describe, it, expect } from 'vitest';

describe('middleware', () => {
  it('adds Authorization header if session cookie exists and no auth header present', () => {
    const request = new NextRequest('http://localhost:3000/api/v1/test');
    request.cookies.set('kogniq_session', 'mock-session-token');
    
    const response = middleware(request);
    expect(response.headers.get('x-middleware-request-authorization')).toBe('Bearer mock-session-token');
  });

  it('does not add Authorization header if no session cookie exists', () => {
    const request = new NextRequest('http://localhost:3000/api/v1/test');
    
    const response = middleware(request);
    expect(response.headers.has('x-middleware-request-authorization')).toBe(false);
  });

  it('preserves existing Authorization header', () => {
    const request = new NextRequest('http://localhost:3000/api/v1/test', {
      headers: { 'Authorization': 'Bearer existing-token' }
    });
    request.cookies.set('kogniq_session', 'mock-session-token');
    
    const response = middleware(request);
    expect(response.headers.get('x-middleware-request-authorization')).toBe('Bearer existing-token');
  });

  it('has correct matcher configuration', () => {
    expect(config.matcher).toBe('/api/:path*');
  });
});

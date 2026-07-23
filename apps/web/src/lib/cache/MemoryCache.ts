import type { ICache } from "./ICache";

interface CacheEntry<T> {
  value: T;
  expiry?: number;
}

export class MemoryCache implements ICache {
  private cache = new Map<string, CacheEntry<unknown>>();

  get<T>(key: string): T | undefined {
    const entry = this.cache.get(key);
    if (!entry) return undefined;

    if (entry.expiry && Date.now() > entry.expiry) {
      this.cache.delete(key);
      return undefined;
    }

    return entry.value as T;
  }

  set<T>(key: string, value: T, ttlMs?: number): void {
    const expiry = ttlMs ? Date.now() + ttlMs : undefined;
    this.cache.set(key, { value, expiry });
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;
    
    if (entry.expiry && Date.now() > entry.expiry) {
      this.cache.delete(key);
      return false;
    }
    return true;
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }
}

export const globalCache = new MemoryCache();

import { describe, it, expect, vi, beforeEach, afterEach, Mock } from 'vitest';
import { AnalyticsDeliveryQueue } from "./AnalyticsDeliveryQueue";
import { EventBatchItem } from "../interfaces/IAnalyticsService";

describe('AnalyticsDeliveryQueue', () => {
  let transport: Mock;
  let queue: AnalyticsDeliveryQueue;

  beforeEach(() => {
    vi.useFakeTimers();
    transport = vi.fn().mockResolvedValue(undefined);
    queue = new AnalyticsDeliveryQueue(transport as unknown as (events: EventBatchItem[], options?: { signal?: AbortSignal, keepalive?: boolean }) => Promise<void>);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    queue.dispose();
  });

  const createEvent = (id: string): EventBatchItem => ({
    event_id: id,
    event_type: 'resource_viewed',
    resource_id: 'doc-1',
    data: {}
  });

  it('enforces 200 event capacity limit, dropping oldest pending events', () => {
    queue.initialize('user1');
    
    // Add 250 events
    for (let i = 0; i < 250; i++) {
      queue.enqueueEvent(createEvent(`ev-${i}`));
    }

    const pending = queue.getPendingEvents();
    expect(pending.length).toBe(200);
    
    // The first 50 were dropped. So the oldest in queue should be ev-50
    expect(pending[0].event.event_id).toBe('ev-50');
    expect(pending[199].event.event_id).toBe('ev-249');
  });

  it('respects UTF-8 byte limit bisection', async () => {
    queue.initialize('user1');
    
    // Make very large events to exceed 60kb easily.
    // 50 events of 2000 bytes = 100,000 bytes (which exceeds 60,000 bytes)
    const largeData = 'a'.repeat(2000);
    for (let i = 0; i < 50; i++) {
      queue.enqueueEvent({
        ...createEvent(`ev-${i}`),
        data: { payload: largeData }
      });
    }

    // Fast-forward flush timer
    await vi.runAllTimersAsync();
    
    // Transport should have been called, but NOT with all 50 events at once.
    // Given 60k bytes max, and each is ~2000 bytes, maybe ~25 events per batch.
    expect(transport).toHaveBeenCalled();
    const firstCallArgs = transport.mock.calls[0][0];
    
    expect(firstCallArgs.length).toBeLessThan(50);
    expect(firstCallArgs.length).toBeGreaterThan(0);
    
    // Verify total events sent after multiple flushes
    await vi.runAllTimersAsync();
    await vi.runAllTimersAsync();
    
    const totalSent = transport.mock.calls.reduce((sum: number, call: unknown[]) => sum + (call[0] as unknown[]).length, 0);
    expect(totalSent).toBe(50);
  });

  it('drops events completely on permanent errors (400, 422)', async () => {
    queue.initialize('user1');
    
    transport.mockRejectedValueOnce(new Error("Request failed with 422 Unprocessable Entity"));
    
    queue.enqueueEvent(createEvent('ev-bad'));
    await vi.runAllTimersAsync();
    
    expect(transport).toHaveBeenCalledTimes(1);
    
    // Should NOT be requeued
    expect(queue.getPendingEvents().length).toBe(0);
    expect(queue.getInFlightEvents()).toBeNull();
  });

  it('requeues events up to 3 attempts on transient errors', async () => {
    queue.initialize('user1');
    
    // Mock failing 3 times with transient error (e.g. TypeError from fetch)
    transport
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockRejectedValueOnce(new TypeError("Failed to fetch"));
      
    queue.enqueueEvent(createEvent('ev-transient'));
    
    // Attempt 1
    await vi.advanceTimersByTimeAsync(3000);
    expect(transport).toHaveBeenCalledTimes(1);
    expect(queue.getPendingEvents().length).toBe(1);
    expect(queue.getPendingEvents()[0].attempts).toBe(1);
    
    // Attempt 2
    await vi.advanceTimersByTimeAsync(3000);
    expect(transport).toHaveBeenCalledTimes(2);
    expect(queue.getPendingEvents().length).toBe(1);
    expect(queue.getPendingEvents()[0].attempts).toBe(2);
    
    // Attempt 3 (Final attempt fails, so it drops)
    await vi.advanceTimersByTimeAsync(3000);
    expect(transport).toHaveBeenCalledTimes(3);
    
    // Dropped permanently
    expect(queue.getPendingEvents().length).toBe(0);
  });

  it('drops in-flight events and ignores them if generation changes (user switch)', async () => {
    queue.initialize('user1');
    
    let resolveTransport: (v?: unknown) => void;
    transport.mockImplementationOnce(() => {
      return new Promise(resolve => {
        resolveTransport = resolve;
      });
    });
    
    queue.enqueueEvent(createEvent('ev-1'));
    await vi.runOnlyPendingTimersAsync(); // trigger flush
    
    expect(transport).toHaveBeenCalledTimes(1);
    expect(queue.getInFlightEvents()?.length).toBe(1);
    
    // User switches mid-flight!
    queue.initialize('user2');
    
    // The queue should immediately clear pending/inFlight
    expect(queue.getPendingEvents().length).toBe(0);
    expect(queue.getInFlightEvents()).toBeNull();
    
    // The previous request finishes
    resolveTransport!();
    await vi.runAllTimersAsync();
    
    // Generation guard prevented it from touching state or rescheduling flush for user1's event
    expect(queue.getPendingEvents().length).toBe(0);
  });
});

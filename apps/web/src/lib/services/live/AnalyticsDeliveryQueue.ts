import { EventBatchItem } from "../interfaces/IAnalyticsService";

export interface PendingEvent {
  event: EventBatchItem;
  attempts: number;
}

export class AnalyticsDeliveryQueue {
  private pending: PendingEvent[] = [];
  private inFlight: PendingEvent[] | null = null;
  private activeUserId: string | null = null;
  private generation: number = 0;
  private abortController: AbortController | null = null;
  
  // Application safety limit for JSON blob (UTF-8 bytes)
  private readonly MAX_BYTES = 60000;
  private readonly MAX_CAPACITY = 200;
  
  private flushTimeout: ReturnType<typeof setTimeout> | null = null;
  private isFlushing: boolean = false;

  constructor(
    private readonly transport: (events: EventBatchItem[], options?: { signal?: AbortSignal, keepalive?: boolean }) => Promise<void>
  ) {
    if (typeof window !== 'undefined') {
      window.addEventListener('visibilitychange', this.handleVisibilityChange);
    }
  }

  public dispose() {
    if (typeof window !== 'undefined') {
      window.removeEventListener('visibilitychange', this.handleVisibilityChange);
    }
    this.clearFlushTimer();
    if (this.abortController) {
      this.abortController.abort("disposed");
      this.abortController = null;
    }
    this.pending = [];
    this.inFlight = null;
    this.activeUserId = null;
  }

  private handleVisibilityChange = () => {
    if (document.visibilityState === 'hidden') {
      // Best-effort keepalive flush
      if (!this.isFlushing && this.pending.length > 0) {
        this.flush(true).catch(console.error);
      }
    }
  };

  public initialize(userId: string | null) {
    if (this.activeUserId !== userId) {
      if (this.abortController) {
        this.abortController.abort("User switch");
        this.abortController = null;
      }
      this.pending = [];
      this.inFlight = null;
      this.generation++;
      this.activeUserId = userId;
      this.clearFlushTimer();
      this.isFlushing = false;
    }
  }

  public getTotalQueuedEventCount(): number {
    const inFlightCount = this.inFlight ? this.inFlight.length : 0;
    return this.pending.length + inFlightCount;
  }

  private enforceCapacity() {
    while (this.getTotalQueuedEventCount() > this.MAX_CAPACITY) {
      if (this.pending.length > 0) {
        this.pending.shift();
      } else {
        // If pending is empty, inFlight occupies everything. We cannot evict inFlight.
        break;
      }
    }
  }

  public enqueueEvent(event: EventBatchItem): void {
    if (!this.activeUserId) return; // Ignore events if no user session

    this.pending.push({ event, attempts: 0 });
    
    // Explicitly enforce capacity, which will shift the oldest pending events
    this.enforceCapacity();
    
    this.scheduleFlush();
  }

  private clearFlushTimer() {
    if (this.flushTimeout) {
      clearTimeout(this.flushTimeout);
      this.flushTimeout = null;
    }
  }

  private scheduleFlush() {
    if (this.isFlushing || this.pending.length === 0) return;
    this.clearFlushTimer();
    this.flushTimeout = setTimeout(() => {
      this.flushTimeout = null;
      this.flush().catch(console.error);
    }, 3000);
  }

  private getBlobSize(obj: unknown): number {
    return new Blob([JSON.stringify(obj)]).size;
  }

  private async flush(keepalive: boolean = false): Promise<void> {
    if (this.isFlushing || this.pending.length === 0) return;
    
    this.isFlushing = true;
    const currentGeneration = this.generation;
    
    // Take up to 50 events for a batch
    let batchEvents = this.pending.splice(0, 50);
    
    // Check byte size
    while (batchEvents.length > 0 && this.getBlobSize(batchEvents.map(p => p.event)) > this.MAX_BYTES) {
      if (batchEvents.length === 1) {
        console.warn("AnalyticsDeliveryQueue: Dropping single oversized event", batchEvents[0].event.event_id);
        batchEvents = [];
        break;
      }
      const mid = Math.floor(batchEvents.length / 2);
      const left = batchEvents.slice(0, mid);
      const right = batchEvents.slice(mid);
      
      // Put right half back at the front of pending
      this.pending.unshift(...right);
      batchEvents = left;
    }
    
    if (batchEvents.length === 0) {
      this.isFlushing = false;
      this.scheduleFlush();
      return;
    }
    
    this.inFlight = batchEvents;
    this.abortController = new AbortController();
    
    try {
      await this.transport(this.inFlight.map(p => p.event), {
        signal: this.abortController.signal,
        keepalive
      });
      // Success, drop them permanently
    } catch (err: unknown) {
      if (this.generation !== currentGeneration) {
        return; // Orphaned
      }
      
      this.handleError(err);
    } finally {
      if (this.generation === currentGeneration) {
        this.inFlight = null;
        this.abortController = null;
        this.isFlushing = false;
        this.scheduleFlush();
      }
    }
  }

  private handleError(err: unknown) {
    if (!this.inFlight) return;
    
    // Determine if it is a permanent error
    // fetch throws TypeError for network disconnection
    let isPermanent = false;
    
    if (err instanceof DOMException && err.name === "AbortError") {
      // Typically we don't abort unless user switches (which is caught by generation).
      // If it is a network timeout abort, it's transient.
      isPermanent = false;
    } else if (err instanceof Error && (
      err.message.includes("400") || 
      err.message.includes("401") || 
      err.message.includes("403") || 
      err.message.includes("404") || 
      err.message.includes("409") || 
      err.message.includes("422")
    )) {
      isPermanent = true;
    }

    if (isPermanent) {
      // Drop batch entirely
      return;
    }

    // Transient: requeue items with attempts < 3
    const toRequeue = [];
    // attempts starts at 0. First attempt failed -> becomes 1.
    // If it fails when attempts=2 -> becomes 3. So we only requeue if attempts < 3.
    for (const item of this.inFlight) {
      item.attempts++;
      if (item.attempts < 3) {
        toRequeue.push(item);
      }
    }
    
    // Prepend to pending (retry priority)
    if (toRequeue.length > 0) {
      this.pending.unshift(...toRequeue);
      this.enforceCapacity();
    }
  }

  // Exposed for tests
  public getPendingEvents(): PendingEvent[] {
    return this.pending;
  }
  public getInFlightEvents(): PendingEvent[] | null {
    return this.inFlight;
  }
}

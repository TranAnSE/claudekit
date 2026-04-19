---
name: background-jobs
description: >
  Use when implementing background task processing, job queues, or async work outside the request/response cycle. Trigger for keywords like Celery, BullMQ, Bull, task queue, background job, worker, cron job, scheduled task, async task, delayed job, or any mention of processing work outside the HTTP request lifecycle. Also activate when sending emails, generating reports, processing uploads, or handling webhooks asynchronously.
---

# Background Jobs

## When to Use

- Sending emails or notifications after an API response
- Processing file uploads (resize images, parse CSVs)
- Generating reports or exports
- Webhook delivery with retries
- Scheduled/cron tasks (cleanup, aggregation)
- Any work that would make an API response too slow (>500ms)

## When NOT to Use

- Simple in-request work under 200ms — just do it inline
- One-off scripts — use a CLI command instead
- Real-time bidirectional communication — use WebSockets or SSE

---

## Python: Celery

### Setup

```python
# src/core/celery.py
from celery import Celery

app = Celery('myapp')
app.config_from_object({
    'broker_url': 'redis://localhost:6379/1',
    'result_backend': 'redis://localhost:6379/2',
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'task_track_started': True,
    'task_acks_late': True,           # Re-deliver if worker crashes
    'worker_prefetch_multiplier': 1,  # Fair scheduling
})
```

### Define tasks

```python
# src/tasks/email.py
from src.core.celery import app

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60s between retries
)
def send_welcome_email(self, user_id: str):
    try:
        user = get_user(user_id)
        mailer.send(to=user.email, template='welcome', context={'name': user.name})
    except MailerError as exc:
        self.retry(exc=exc)

@app.task(bind=True, max_retries=5, default_retry_delay=300)
def process_upload(self, upload_id: str):
    try:
        upload = get_upload(upload_id)
        result = parse_csv(upload.file_path)
        save_results(upload_id, result)
    except Exception as exc:
        self.retry(exc=exc)
```

### Dispatch from FastAPI

```python
from fastapi import APIRouter, status
from src.tasks.email import send_welcome_email

router = APIRouter()

@router.post("/api/users", status_code=status.HTTP_201_CREATED)
async def create_user(body: CreateUserRequest):
    user = await save_user(body)
    send_welcome_email.delay(str(user.id))   # Fire and forget
    return user
```

### Scheduled tasks (Celery Beat)

```python
# In celery config
app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'src.tasks.cleanup.cleanup_sessions',
        'schedule': 3600.0,  # Every hour
    },
    'daily-report': {
        'task': 'src.tasks.reports.generate_daily',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC
    },
}
```

### Run workers

```bash
# Worker
celery -A src.core.celery worker --loglevel=info --concurrency=4

# Beat scheduler
celery -A src.core.celery beat --loglevel=info

# Both (development only)
celery -A src.core.celery worker --beat --loglevel=info
```

---

## TypeScript: BullMQ

### Setup

```typescript
// src/core/queue.ts
import { Queue, Worker } from 'bullmq';
import Redis from 'ioredis';

const connection = new Redis(process.env.REDIS_URL!, { maxRetriesPerRequest: null });

export function createQueue(name: string) {
  return new Queue(name, { connection });
}

export function createWorker<T>(
  name: string,
  processor: (job: { data: T }) => Promise<void>,
) {
  return new Worker<T>(name, async (job) => processor(job), {
    connection,
    concurrency: 5,
  });
}
```

### Define queues and workers

```typescript
// src/queues/email.queue.ts
import { createQueue, createWorker } from '../core/queue';

interface WelcomeEmailJob {
  userId: string;
  email: string;
  name: string;
}

export const emailQueue = createQueue('email');

export const emailWorker = createWorker<WelcomeEmailJob>('email', async (job) => {
  await mailer.send({
    to: job.data.email,
    template: 'welcome',
    context: { name: job.data.name },
  });
});

emailWorker.on('failed', (job, err) => {
  console.error(`Email job ${job?.id} failed:`, err.message);
});
```

### Dispatch from NestJS

```typescript
// src/users/users.service.ts
import { Injectable } from '@nestjs/common';
import { emailQueue } from '../queues/email.queue';

@Injectable()
export class UsersService {
  async create(dto: CreateUserDto) {
    const user = await this.prisma.user.create({ data: dto });

    await emailQueue.add('welcome', {
      userId: user.id,
      email: user.email,
      name: user.name,
    }, {
      attempts: 3,
      backoff: { type: 'exponential', delay: 60_000 },
    });

    return user;
  }
}
```

### Scheduled/repeatable jobs

```typescript
// Run every hour
await emailQueue.add('digest', { type: 'hourly' }, {
  repeat: { every: 3600_000 },
});

// Cron pattern — daily at 2 AM UTC
await emailQueue.add('daily-report', {}, {
  repeat: { pattern: '0 2 * * *' },
});
```

### NestJS module integration

```typescript
// src/queues/queues.module.ts
import { Module, OnModuleDestroy } from '@nestjs/common';
import { emailQueue, emailWorker } from './email.queue';

@Module({
  providers: [
    { provide: 'EMAIL_QUEUE', useValue: emailQueue },
  ],
  exports: ['EMAIL_QUEUE'],
})
export class QueuesModule implements OnModuleDestroy {
  async onModuleDestroy() {
    await emailWorker.close();
    await emailQueue.close();
  }
}
```

---

## Job Design Patterns

### Idempotent jobs

Jobs may be retried. Design for idempotency:

```python
# BAD — sends duplicate emails on retry
@app.task
def send_email(user_id):
    send(user_id)

# GOOD — check before sending
@app.task
def send_email(user_id):
    if already_sent(user_id, 'welcome'):
        return
    send(user_id)
    mark_sent(user_id, 'welcome')
```

### Small payloads

```typescript
// BAD — large payload in queue
await queue.add('process', { csvData: '...10MB of CSV...' });

// GOOD — pass a reference
await queue.add('process', { uploadId: 'upload_123' });
```

### Dead letter queues

```typescript
// After max retries, move to DLQ for investigation
await emailQueue.add('welcome', data, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 60_000 },
  removeOnComplete: true,
  removeOnFail: false,  // Keep failed jobs for inspection
});
```

---

## Testing

### Python (Celery)

```python
# Always run tasks eagerly in tests
@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

def test_welcome_email_sent(mock_mailer):
    send_welcome_email("user_123")
    mock_mailer.send.assert_called_once()
```

### TypeScript (BullMQ)

```typescript
describe('email worker', () => {
  it('should send welcome email', async () => {
    const sendSpy = vi.spyOn(mailer, 'send');

    // Process job directly (skip queue)
    await emailWorker.run({ data: { userId: '1', email: 'a@b.com', name: 'Test' } });

    expect(sendSpy).toHaveBeenCalledWith(expect.objectContaining({ to: 'a@b.com' }));
  });
});
```

---

## Common Pitfalls

1. **Non-idempotent tasks.** Retries will duplicate side effects. Always check before acting.
2. **Large payloads in queue.** Store data in DB/S3, pass only IDs through the queue.
3. **No retry limits.** Always set `max_retries` / `attempts`. Infinite retries waste resources.
4. **Missing dead letter handling.** Failed jobs need investigation. Don't silently discard them.
5. **Blocking the event loop (Node.js).** CPU-heavy work in BullMQ workers blocks other jobs. Use `worker threads` or separate processes.
6. **Not monitoring queue depth.** Queue buildup indicates workers can't keep up. Alert on queue size.

---

## Related Skills

- `redis` — Redis as the message broker for both Celery and BullMQ
- `docker` — Running workers as separate containers
- `fastapi` — Dispatching Celery tasks from FastAPI endpoints
- `nestjs` — BullMQ integration with NestJS modules
- `logging` — Structured logging for job execution tracking

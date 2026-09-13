# Kafka Events & Messaging Specification

## Topics

### 1. `listing_events`
Emitted by `core-api` when properties are created or updated.

**Payload Schema:**
```json
{
  "event_type": "LISTING_CREATED | LISTING_UPDATED | LISTING_DELETED",
  "listing_id": "uuid",
  "title": "Modern Studio in Downtown",
  "city": "San Francisco",
  "price": 2400.00,
  "timestamp": "2026-09-13T11:00:00Z"
}
```

### 2. `application_events`
Emitted when rental applications undergo status updates.

**Payload Schema:**
```json
{
  "event_type": "APPLICATION_SUBMITTED | APPLICATION_APPROVED | APPLICATION_REJECTED",
  "application_id": "uuid",
  "listing_id": "uuid",
  "applicant_id": "uuid",
  "landlord_id": "uuid",
  "timestamp": "2026-09-13T11:00:00Z"
}
```

### 3. `review_events`
Emitted when reviews are published.

### 4. `notification_events`
Target topic for notification worker consumption.

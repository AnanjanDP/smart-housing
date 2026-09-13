# Database Schema Documentation

## Core Tables & Relations

### 1. `users_user`
- `id` (UUID, Primary Key)
- `email` (VarChar(255), Unique)
- `username` (VarChar(150), Unique)
- `first_name`, `last_name` (VarChar)
- `role` (Enum: `TENANT`, `LANDLORD`, `ADMIN`)
- `phone_number` (VarChar(20))
- `bio` (Text)
- `avatar_url` (VarChar)
- `created_at`, `updated_at` (Timestamp)

### 2. `listings_listing`
- `id` (UUID, Primary Key)
- `owner_id` (FK -> `users_user.id`)
- `title` (VarChar(255))
- `description` (Text)
- `address`, `city`, `state`, `zip_code` (VarChar)
- `price` (Decimal(10, 2))
- `bedrooms`, `bathrooms` (Integer / Decimal)
- `is_available` (Boolean)
- `amenities` (JSONB)
- `created_at`, `updated_at` (Timestamp)

### 3. `roommates_roommateprofile`
- `id` (UUID, Primary Key)
- `user_id` (FK -> `users_user.id`, Unique)
- `budget_min`, `budget_max` (Decimal)
- `move_in_date` (Date)
- `cleanliness_level` (Integer 1-5)
- `sleep_schedule` (Enum: `EARLY_BIRD`, `NIGHT_OWL`, `FLEXIBLE`)
- `smoking_allowed`, `pets_allowed` (Boolean)
- `preferred_location` (VarChar)

### 4. `applications_application`
- `id` (UUID, Primary Key)
- `listing_id` (FK -> `listings_listing.id`)
- `applicant_id` (FK -> `users_user.id`)
- `status` (Enum: `PENDING`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`)
- `move_in_date` (Date)
- `notes` (Text)

### 5. `reviews_review`
- `id` (UUID, Primary Key)
- `reviewer_id` (FK -> `users_user.id`)
- `listing_id` (FK -> `listings_listing.id`, Optional)
- `target_user_id` (FK -> `users_user.id`, Optional)
- `rating` (Integer 1-5)
- `comment` (Text)

### 6. `interactions_interaction`
- `id` (UUID, Primary Key)
- `user_id` (FK -> `users_user.id`)
- `listing_id` (FK -> `listings_listing.id`)
- `action` (Enum: `VIEW`, `SAVE`, `CLICK`, `APPLY`)
- `timestamp` (Timestamp)

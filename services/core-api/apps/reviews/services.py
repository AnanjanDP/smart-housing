from django.db import transaction
from common.kafka import publish_event


class ReviewService:
    @staticmethod
    def announce_created(review):
        """Tell the person being reviewed (the user, or the listing's owner). Call inside the saving transaction."""
        recipient = review.target_user or (review.listing.owner if review.listing_id else None)
        if recipient is None:
            return
        publish_event("review_events", {
            "event_type": "REVIEW_CREATED",
            "review_id": str(review.id),
            "rating": review.rating,
            "reviewer_id": str(review.reviewer_id),
            "listing_id": str(review.listing_id) if review.listing_id else None,
            "listing_title": review.listing.title if review.listing_id else None,
            "recipient_id": str(recipient.id),
            "recipient_email": recipient.email,
        })

    @staticmethod
    def create_review(serializer, reviewer):
        with transaction.atomic():
            review = serializer.save(reviewer=reviewer)
            ReviewService.announce_created(review)
            return review

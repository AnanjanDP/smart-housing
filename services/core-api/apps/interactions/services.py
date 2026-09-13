from apps.interactions.models import Interaction

class InteractionService:
    @staticmethod
    def record_interaction(user, listing, action):
        return Interaction.objects.create(user=user, listing=listing, action=action)

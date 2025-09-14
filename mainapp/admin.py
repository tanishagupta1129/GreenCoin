from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count, Q
from .models import UserData, SubmitProof, RedeemedReward


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')


@admin.register(RedeemedReward)
class RedeemedRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_name', 'cost', 'redeemed_at')
    search_fields = ('user__name', 'reward_name')
    list_filter = ('redeemed_at',)


@admin.register(SubmitProof)
class SubmitProofAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'activity_type',
        'plant_stage',
        'status',
        'submission_date',
        'proof_preview',
        'action_preview',
        'after_planting_preview',
        'views_actions'
    )
    list_filter = ('activity_type', 'status', 'plant_stage')
    search_fields = ('user__name', 'activity_type')

    # === Image Previews ===
    def proof_preview(self, obj):
        if obj.proof_image and hasattr(obj.proof_image, 'url'):
            return format_html('<img src="{}" width="100" height="100" />', obj.proof_image.url)
        return "No Image"
    proof_preview.short_description = 'Proof Image'

    # def empty_spot_preview(self, obj):
    #     try:
    #         if obj.image_empty_spot and hasattr(obj.image_empty_spot, 'url'):
    #             return format_html('<img src="{}" width="100" height="100" />', obj.image_empty_spot.url)
    #     except:
    #         return "Image Error"
    #     return "No Image"
    # empty_spot_preview.short_description = 'Empty Spot'

    def action_preview(self, obj):
        try:
            if obj.image_action and hasattr(obj.image_action, 'url'):
                return format_html('<img src="{}" width="100" height="100" />', obj.image_action.url)
        except:
            return "Image Error"
        return "No Image"
    action_preview.short_description = 'Action Photo'

    def after_planting_preview(self, obj):
        try:
            if obj.image_after_planting and hasattr(obj.image_after_planting, 'url'):
                return format_html('<img src="{}" width="100" height="100" />', obj.image_after_planting.url)
        except:
            return "Image Error"
        return "No Image"
    after_planting_preview.short_description = 'After Planting'

    # === Action Buttons ===
    def views_actions(self, obj):
        return format_html(
            '<a class="button" href="approve/{}/">✅ Accept</a>&nbsp;'
            '<a class="button" href="reject/{}/">❌ Reject</a>',
            obj.pk, obj.pk
        )
    views_actions.short_description = 'Actions'

    # === Custom URLs for Approve/Reject ===
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:proof_id>/', self.admin_site.admin_view(self.approve_proof), name='approve-proof'),
            path('reject/<int:proof_id>/', self.admin_site.admin_view(self.reject_proof), name='reject-proof'),
        ]
        return custom_urls + urls

    # === Leaderboard Update Logic ===
    def update_leaderboard(self):
        users = UserData.objects.annotate(
            total_submissions=Count('submitproof'),
            solar_panel_count=Count('submitproof', filter=Q(submitproof__activity_type='Solar Panel Installation'))
        ).order_by('-earned_coins', '-total_submissions', '-solar_panel_count', 'id')

        rank = 1
        for user in users:
            user.rank = rank
            user.save()
            rank += 1

    # === Approve Handler ===
    def approve_proof(self, request, proof_id):
        proof = SubmitProof.objects.get(pk=proof_id)
        proof.status = 'Accepted'
        proof.save()
        self.update_leaderboard()
        messages.success(request, f"Proof by {proof.user.name} accepted.")
        return redirect(request.META.get('HTTP_REFERER'))

    # === Reject Handler ===
    def reject_proof(self, request, proof_id):
        proof = SubmitProof.objects.get(pk=proof_id)
        proof.status = 'Rejected'
        proof.save()
        messages.warning(request, f"Proof by {proof.user.name} rejected.")
        return redirect(request.META.get('HTTP_REFERER'))

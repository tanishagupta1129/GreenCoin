from django.db import models
from django.contrib.auth.models import User

# UserData model
class UserData(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    earned_coins = models.IntegerField(default=0)
    spent_coins = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    def accepted_submissions_count(self):
        return SubmitProof.objects.filter(user=self, status='Accepted').count()

    def solar_panel_submissions_count(self):
        return SubmitProof.objects.filter(user=self, status='Accepted', activity_type='Solar Panel Installation').count()

    def coins_left(self):
        print(f"Earned Coins: {self.earned_coins}, Spent Coins: {self.spent_coins}")
        return self.earned_coins - self.spent_coins

    def __str__(self):
        return self.name

class SubmitProof(models.Model):
    ACTIVITY_CHOICES = [
        ('Tree Plantation', 'Tree Plantation'),
        ('Solar Panel Installation', 'Solar Panel Installation'),
        ('Public Transport Usage', 'Public Transport Usage'),
        ('Use of Electric Vehicle', 'Use of Electric Vehicle'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100, choices=ACTIVITY_CHOICES)

    # General proof image (for non-plantation activities)
    proof_image = models.FileField(upload_to='proofs/', blank=True, null=True)

    # Tree Plantation Stage 1 - Multiple steps
    # image_empty_spot = models.ImageField(upload_to='proofs/tree_stages/', blank=True, null=True)
    image_action = models.ImageField(upload_to='proofs/tree_stages/', blank=True, null=True)
    image_after_planting = models.ImageField(upload_to='proofs/tree_stages/', blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)

    image_hash = models.CharField(max_length=100, blank=True, null=True)
    coins_given = models.BooleanField(default=False)
    earned_coins = models.IntegerField(null=True, blank=True)

    plant_stage = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = SubmitProof.objects.get(pk=self.pk)
            if old_instance.status != 'Accepted' and self.status == 'Accepted' and not self.coins_given:
                self.give_coins()
        elif self.status == 'Accepted' and not self.coins_given:
            self.give_coins()

        super().save(*args, **kwargs)

    def give_coins(self):
        coins = self.get_coin_amount()
        self.user.earned_coins += coins
        self.user.save()
        self.coins_given = True
        self.earned_coins = coins

    def get_coin_amount(self):
        if self.activity_type == 'Tree Plantation':
            return 50
        elif self.activity_type == 'Public Transport Usage':
            return 25
        elif self.activity_type == 'Solar Panel Installation':
            return 45
        elif self.activity_type == 'Use of Electric Vehicle':
            return 35
        return 0

    def __str__(self):
        return f"{self.user.name} - {self.activity_type}"



    
# Reward model
class Reward(models.Model):
    name = models.CharField(max_length=100)
    cost = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# RedeemedReward model
class RedeemedReward(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    reward_name = models.CharField(max_length=200)
    cost = models.IntegerField()
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} redeemed {self.reward_name}"
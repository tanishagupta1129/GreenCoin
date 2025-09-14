# import json
# import imagehash
# import random
# from django.core.mail import send_mail
# from django.conf import settings
# from PIL import Image
# from django.core.files.storage import default_storage
# import os
# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse, JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.cache import never_cache
# from django.utils.decorators import method_decorator
# from django.contrib import messages
# from django.contrib.auth.hashers import make_password, check_password
# from django.contrib.auth.models import User
# from django.db.models import Count, Q
# from .models import UserData, SubmitProof, Reward, RedeemedReward  # Add SubmitProof model here

# from .forms import SubmitProofForm  # Import the form for proof submission
# from django.conf import settings


# def logout_view(request):
#     # Clear all session data including user_id, user_name, etc.
#     request.session.flush()
#     messages.success(request, "You have been logged out.")
#     return redirect('login')


# @csrf_exempt
# def check_email(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         exists = UserData.objects.filter(email=email).exists()
#         return JsonResponse({"exists": exists})
#     return JsonResponse({"error": "Invalid request"}, status=400)

# # Index Page
# def index(request):
    
#     return render(request, 'mainapp/index.html')


# def login_page(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']

#         try:
#             user = UserData.objects.get(email=email)
#             if check_password(password, user.password):  # Check hashed password
#                 request.session.clear()  # Use this instead of flush()
#   # Clear old session completely

#                 request.session['user_email'] = email
#                 request.session['user_id'] = user.id
#                 request.session['user_name'] = user.name
#                 messages.success(request, f" Welcome, {user.name}!")

#                 return redirect('profile')
#             else:
#                 error = "Invalid credentials.Please try again"
#                 return render(request, 'mainapp/login.html', {'error': error})
#         except UserData.DoesNotExist:
#             error = "You are not registered yet. Please register first."
#             return render(request, 'mainapp/login.html', {'error': error})

#     return render(request, 'mainapp/login.html')


# def signup_page(request):
#     if request.method == 'POST':
#         if 'send_otp' in request.POST:
#             name = request.POST.get('fullname')
#             email = request.POST.get('email')
#             password = request.POST.get('password')

#             # Check if email already exists
#             if UserData.objects.filter(email=email).exists():
#                 messages.error(request, "This email is already registered.")
#                 return redirect('signup')

#             # Generate OTP
#             otp = random.randint(100000, 999999)
#             request.session['temp_user'] = {
#                 'fullname': name,
#                 'email': email,
#                 'password': password,
#                 'otp': str(otp),
#             }
#             request.session.set_expiry(50)  # OTP valid for 5 min

#             # Send OTP via email
#             send_mail(
#                 'Green Coin Registration OTP',
#                 f'Your OTP for Green Coin Registration is: {otp}',
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 fail_silently=False,
#             )

#             messages.success(request, f"OTP sent to {email}. Please check your email.")
#             return redirect('signup')

#         elif 'verify_otp' in request.POST:
#             entered_otp = request.POST.get('otp')
#             temp_user = request.session.get('temp_user')

#             if not temp_user:
#                 messages.error(request, "Session expired. Please start again.")
#                 return redirect('signup')

#             if str(entered_otp) == str(temp_user.get('otp')):
#                 # Create user
#                 new_user = UserData.objects.create(
#                     name=temp_user['fullname'],
#                     email=temp_user['email'],
#                     password=make_password(temp_user['password']),
#                 )

#                 del request.session['temp_user']
#                 request.session['user_id'] = new_user.id

#                 # Show welcome message on profile page
#                 messages.success(request, f"Registration Succesful. Thank you for joining Green Coin 🌱. Please first login to access services")

#                 return redirect('login')

#             else:
#                 messages.error(request, "Invalid OTP. Please try again.")
#                 return redirect('signup')

#     return render(request, 'mainapp/signup.html')

# # Submit Proof Page
# def submit_proof(request):
#     email = request.session.get('user_email')
#     if not email:
#         messages.error(request, "Please log in first to submit proof.")
#         return redirect('login')

#     try:
#         user = UserData.objects.get(email=email)
#     except UserData.DoesNotExist:
#         messages.error(request, "User not found. Please log in again.")
#         return redirect('login')

#     if request.method == 'POST':
#         form = SubmitProofForm(request.POST, request.FILES)
#         if form.is_valid():
#             proof = form.save(commit=False)
#             proof.user = user  # Attach logged-in user
#             proof.save()
#             messages.success(request, "Proof submitted successfully! Please wait for approval.")
#             return redirect('submit_proof')  # Reload the proof submission page
#         else:
#             # messages.error(request, "Please correct the errors below.")
#             messages.error(request,"Proof submission failed due to validation errors.")
#     else:
#         form = SubmitProofForm()

#     return render(request, 'mainapp/proof_sub.html', {'form': form})



# def update_leaderboard():
#     users = UserData.objects.annotate(
#         total_submissions=Count('submitproof'),  # correct
#         solar_panel_count=Count(
#             'submitproof',
#             filter=Q(submitproof__activity_type='Solar Panel Installation')  # ✅ correct value
#         )
#     ).order_by(
#         '-earned_coins',
#         'total_submissions',
#         '-solar_panel_count',
#         'id'
#     )

#     rank = 1
#     for user in users:
#         user.rank = rank
#         user.save()
#         rank += 1




# # Leaderboard Page
# def leaderboard(request):
#     update_leaderboard()

#     # users = UserData.objects.all().order_by('-earned_coins')
#     users = UserData.objects.all().order_by('rank')  # ✅ use rank, not earned_coins
#     return render(request, 'mainapp/leaderboard.html', {'users': users})


# @never_cache
# def profile(request):
#     # Check if user is logged in via session
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return redirect('login')

#     try:
#         # Fetch user from database
#         user = UserData.objects.get(id=user_id)
#     except UserData.DoesNotExist:
#         # If user not found in DB, clear session and redirect
#         request.session.flush()
#         return redirect('login')

#     # Get all users ordered by earned_coins for ranking
#     all_users = UserData.objects.order_by('-earned_coins')
#     rank = list(all_users).index(user) + 1

#     # Format coin display
#     earned_coins = f"🪙 {user.earned_coins}"
#     spent_coins = f"🔻 {user.spent_coins}"
#     coins_left = f"✅ {user.coins_left()}"

#     # Fetch submitted proofs by this user
#     submitted_proofs = SubmitProof.objects.filter(user=user).order_by('-submission_date')

#     # Context for template rendering
#     context = {
#         'user': user,
#         'earned_coins': earned_coins,
#         'spent_coins': spent_coins,
#         'coins_left': coins_left,
#         'rank': rank,
#         'submitted_proofs': submitted_proofs,
#     }

#     return render(request, 'mainapp/profile.html', context)


# # @login_required
# def resubmit_proof(request, submission_id):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return redirect('login')
#     submission = get_object_or_404(SubmitProof, id=submission_id)

#     if submission.status != 'Rejected' :
#        messages.error(request,"Only rejected proofs can be submitted.")
#        return redirect('profile')

#     if request.method == 'POST' and request.FILES.get('proof_file'):
#         new_proof_file = request.FILES['proof_file']
#         old_proof_path = submission.proof_image.path

#         # Save new file temporarily for comparison
#         temp_filename = 'temp/' + new_proof_file.name
#         temp_file_path = default_storage.save(temp_filename, new_proof_file)
#         full_temp_path = os.path.join(default_storage.location, temp_file_path)

#         try:
#             # Generate perceptual hashes
#             old_hash = imagehash.average_hash(Image.open(old_proof_path))
#             new_hash = imagehash.average_hash(Image.open(full_temp_path))

#             if old_hash == new_hash:
#                 messages.error(
#                     request,
#                     "This image appears to be the same as the previously rejected one. Please upload a different image."
#                 )
#                 default_storage.delete(temp_file_path)
#                 return redirect('resubmit_proof', submission_id=submission.id)

#             # If image is different, update the submission
#             submission.proof_image = new_proof_file
#             submission.status = 'Pending'
#             submission.rejection_reason = None
#             submission.save()

#             messages.success(request, 'Proof resubmitted successfully!')

#         except Exception as e:
#             messages.error(request, f"Error processing image: {e}")

#         finally:
#             # Always clean up temporary file
#             if default_storage.exists(temp_file_path):
#                 default_storage.delete(temp_file_path)

#         return redirect('profile')

#     return render(request, 'mainapp/resubmit_form.html', {'submission': submission})





# def reward(request):
#     return render(request, 'mainapp/reward.html')


# @csrf_exempt
# def redeem_reward(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')
#         if not user_id:
#             return JsonResponse({'success': False, 'message': 'User not logged in'})

#         try:
#             data = json.loads(request.body)
#             reward_name = data.get('reward')
#             reward_cost = int(data.get('cost'))

#             user = UserData.objects.get(id=user_id)
#             if user.coins_left() >= reward_cost:
#                 user.spent_coins += reward_cost
#                 user.save()

#                 RedeemedReward.objects.create(
#                     user=user,
#                     reward_name=reward_name,
#                     cost=reward_cost
#                 )

#                 return JsonResponse({'success': True, 'remaining_coins': user.coins_left()})
#             else:
#                 return JsonResponse({'success': False, 'message': 'Not enough coins'})
#         except Exception as e:
#             import traceback
#             traceback_str = traceback.format_exc()
#             print(traceback_str)  # Full error in terminal
#             return JsonResponse({'success': False, 'message': str(e)})

#     return JsonResponse({'success': False, 'message': 'Invalid request method'})

# def awareness_page(request):
#     return render(request, 'mainapp/awareness.html')

import json
import imagehash
import random
import os
import numpy as np
from PIL import Image
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count, Q

from .models import UserData, SubmitProof, Reward, RedeemedReward
from .forms import SubmitProofForm

# TensorFlow AI model import
import tensorflow as tf
from tensorflow.keras.preprocessing import image

# Load model once globally
MODEL_PATH = os.path.join(settings.BASE_DIR, 'plant_stage_model.h5')
model = tf.keras.models.load_model(MODEL_PATH)

def predict_stage(img_path):
    img = image.load_img(img_path, target_size=(150, 150))  # match model input
    img_array = image.img_to_array(img)
    
    if img_array.shape[-1] == 4:  # remove alpha if present
        img_array = img_array[:, :, :3]

    img_array = np.expand_dims(img_array, axis=0) / 255.0
    prediction = model.predict(img_array)

    predicted_class = np.argmax(prediction)
    classes = ['stage1', 'stage2', 'stage3', 'stage4']  # ✅ match model output
    return classes[predicted_class]

def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('login')


@csrf_exempt
def check_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        exists = UserData.objects.filter(email=email).exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"error": "Invalid request"}, status=400)


def index(request):
    return render(request, 'mainapp/index.html')


def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = UserData.objects.get(email=email)
            if check_password(password, user.password):
                request.session.clear()
                request.session['user_email'] = email
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                messages.success(request, f"Welcome, {user.name}!")
                return redirect('profile')
            else:
                return render(request, 'mainapp/login.html', {'error': "Invalid credentials."})
        except UserData.DoesNotExist:
            return render(request, 'mainapp/login.html', {'error': "Please register first."})
    return render(request, 'mainapp/login.html')


def signup_page(request):
    if request.method == 'POST':
        if 'send_otp' in request.POST:
            name = request.POST.get('fullname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            if UserData.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
                return redirect('signup')
            otp = random.randint(100000, 999999)
            request.session['temp_user'] = {'fullname': name, 'email': email, 'password': password, 'otp': str(otp)}
            request.session.set_expiry(50)
            send_mail(
                'Green Coin Registration OTP',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, f"OTP sent to {email}.")
            return redirect('signup')

        elif 'verify_otp' in request.POST:
            entered_otp = request.POST.get('otp')
            temp_user = request.session.get('temp_user')
            if not temp_user:
                messages.error(request, "Session expired.")
                return redirect('signup')
            if str(entered_otp) == temp_user.get('otp'):
                new_user = UserData.objects.create(
                    name=temp_user['fullname'],
                    email=temp_user['email'],
                    password=make_password(temp_user['password']),
                )
                del request.session['temp_user']
                request.session['user_id'] = new_user.id
                messages.success(request, "Registration successful. Please log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP.")
                return redirect('signup')
    return render(request, 'mainapp/signup.html')


# def submit_proof(request):
#     email = request.session.get('user_email')
#     if not email:
#         messages.error(request, "Please log in.")
#         return redirect('login')

#     try:
#         user = UserData.objects.get(email=email)
#     except UserData.DoesNotExist:
#         messages.error(request, "User not found.")
#         return redirect('login')

#     if request.method == 'POST':
#         form = SubmitProofForm(request.POST, request.FILES)
#         activity = request.POST.get('activity_type')

#         if activity == 'Tree Plantation':
#             # Handle multi-step image proof
#             # img1 = request.FILES.get('image_empty_spot')
#             img1 = request.FILES.get('image_action')
#             img2 = request.FILES.get('image_after_planting')
#             desc = request.POST.get('description', '')

#             if not all([img1, img2]):
#                 messages.error(request, "All two plantation step images are required.")
#                 return render(request, 'mainapp/proof_sub.html', {'form': form})

#             SubmitProof.objects.create(
#                 user=user,
#                 activity_type=activity,
#                 image_action=img1,
#                 image_after_planting=img2,
#                 description=desc,
#                 plant_stage='stage1'
#             )
#             messages.success(request, "Tree plantation proof submitted!")
#             return redirect('submit_proof')

#         else:
#             if 'proof_image' not in request.FILES:
#                 messages.error(request, "Please upload a proof image.")
#                 return render(request, 'mainapp/proof_sub.html', {'form': form})

#             if form.is_valid():
#                 proof = form.save(commit=False)
#                 proof.user = user
#                 file = request.FILES['proof_image']
#                 temp_path = default_storage.save('temp/' + file.name, file)
#                 full_path = os.path.join(default_storage.location, temp_path)

#                 try:
#                     stage = predict_stage(full_path)
#                     proof.plant_stage = stage
#                 except Exception as e:
#                     messages.error(request, f"AI model failed: {e}")
#                     default_storage.delete(temp_path)
#                     return redirect('submit_proof')

#                 proof.save()
#                 default_storage.delete(temp_path)
#                 messages.success(request, "Proof submitted successfully!")
#                 return redirect('submit_proof')
#             else:
#                 messages.error(request, "Proof form is invalid.")
#     else:
#         form = SubmitProofForm()

#     return render(request, 'mainapp/proof_sub.html', {'form': form})
def submit_proof(request):
    email = request.session.get('user_email')
    if not email:
        messages.error(request, "Please log in.")
        return redirect('login')

    try:
        user = UserData.objects.get(email=email)
    except UserData.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    if request.method == 'POST':
        form = SubmitProofForm(request.POST, request.FILES)
        activity = request.POST.get('activity_type')

        if activity == 'Tree Plantation':
            img1 = request.FILES.get('image_action')
            img2 = request.FILES.get('image_after_planting')
            desc = request.POST.get('description', '')

            if not all([img1, img2]):
                messages.error(request, "All two plantation step images are required.")
                return render(request, 'mainapp/proof_sub.html', {'form': form})

            SubmitProof.objects.create(
                user=user,
                activity_type=activity,
                image_action=img1,
                image_after_planting=img2,
                description=desc,
                plant_stage='Stage 1'  # ✅ Capital S
            )
            messages.success(request, "Proof submitted successfully!. Please wait for approval")
            return redirect('submit_proof')

        else:
            if 'proof_image' not in request.FILES:
                messages.error(request, "Please upload a proof image.")
                return render(request, 'mainapp/proof_sub.html', {'form': form})

            if form.is_valid():
                proof = form.save(commit=False)
                proof.user = user
                file = request.FILES['proof_image']
                temp_path = default_storage.save('temp/' + file.name, file)
                full_path = os.path.join(default_storage.location, temp_path)

                try:
                    stage = predict_stage(full_path)
                    proof.plant_stage = stage
                except Exception as e:
                    messages.error(request, f"AI model failed: {e}")
                    default_storage.delete(temp_path)
                    return redirect('submit_proof')

                # ✅ This is where we insert your condition
                if form.cleaned_data['activity_type'] == "Tree Plantation":
                    proof.plant_stage = "Stage 1"
                else:
                    proof.plant_stage = None

                proof.save()
                default_storage.delete(temp_path)
                messages.success(request, "Proof submitted successfully!. Please wait for approval")
                return redirect('submit_proof')
            else:
                messages.error(request, "Proof form is invalid.")
    else:
        form = SubmitProofForm()

    return render(request, 'mainapp/proof_sub.html', {'form': form})


def update_leaderboard():
    users = UserData.objects.annotate(
        total_submissions=Count('submitproof'),
        solar_panel_count=Count('submitproof', filter=Q(submitproof__activity_type='Solar Panel Installation'))
    ).order_by('-earned_coins', 'total_submissions', '-solar_panel_count', 'id')

    rank = 1
    for user in users:
        user.rank = rank
        user.save()
        rank += 1


def leaderboard(request):
    update_leaderboard()
    users = UserData.objects.all().order_by('rank')
    return render(request, 'mainapp/leaderboard.html', {'users': users})


@never_cache
def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
        request.session.flush()
        return redirect('login')

    all_users = UserData.objects.order_by('-earned_coins')
    rank = list(all_users).index(user) + 1
    context = {
        'user': user,
        'earned_coins': f"🪙 {user.earned_coins}",
        'spent_coins': f"🔻 {user.spent_coins}",
        'coins_left': f"✅ {user.coins_left()}",
        'rank': rank,
        'submitted_proofs': SubmitProof.objects.filter(user=user).order_by('-submission_date')
    }
    return render(request, 'mainapp/profile.html', context)


def resubmit_proof(request, submission_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    submission = get_object_or_404(SubmitProof, id=submission_id)
    if submission.status != 'Rejected':
        messages.error(request, "Only rejected proofs can be resubmitted.")
        return redirect('profile')
    if request.method == 'POST' and request.FILES.get('proof_file'):
        new_file = request.FILES['proof_file']
        old_path = submission.proof_image.path
        temp_filename = 'temp/' + new_file.name
        temp_path = default_storage.save(temp_filename, new_file)
        full_temp_path = os.path.join(default_storage.location, temp_path)
        try:
            old_hash = imagehash.average_hash(Image.open(old_path))
            new_hash = imagehash.average_hash(Image.open(full_temp_path))
            if old_hash == new_hash:
                messages.error(request, "Same image as before.")
                default_storage.delete(temp_path)
                return redirect('resubmit_proof', submission_id=submission.id)

            # Run prediction again
            stage = predict_stage(full_temp_path)
            submission.proof_image = new_file
            submission.status = 'Pending'
            submission.rejection_reason = None
            submission.plant_stage = stage
            submission.save()
            messages.success(request, 'Resubmitted successfully!')
        except Exception as e:
            messages.error(request, f"Error: {e}")
        finally:
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)
        return redirect('profile')
    return render(request, 'mainapp/resubmit_form.html', {'submission': submission})


def reward(request):
    return render(request, 'mainapp/reward.html')


@csrf_exempt
def redeem_reward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'User not logged in'})
        try:
            data = json.loads(request.body)
            reward_name = data.get('reward')
            reward_cost = int(data.get('cost'))
            user = UserData.objects.get(id=user_id)
            if user.coins_left() >= reward_cost:
                user.spent_coins += reward_cost
                user.save()
                RedeemedReward.objects.create(user=user, reward_name=reward_name, cost=reward_cost)
                return JsonResponse({'success': True, 'remaining_coins': user.coins_left()})
            else:
                return JsonResponse({'success': False, 'message': 'Not enough coins'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def awareness_page(request):
    return render(request, 'mainapp/awareness.html')

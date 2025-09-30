# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required, user_passes_test
# from .models import LeaseRequest
# from django.utils import timezone
# from django.conf import settings
# import boto3

# # Home redirect
# @login_required
# def home(request):
#     if request.user.is_staff:
#         return redirect('lease:pending_requests')
#     return redirect('lease:my_requests')

# # Employee: Request Lease
# @login_required
# def request_lease(request):
#     if request.method == 'POST':
#         role = request.POST['role']
#         reason = request.POST['reason']
#         duration = int(request.POST.get('duration', 3600))
#         LeaseRequest.objects.create(user=request.user, role_requested=role, reason=reason, duration_seconds=duration)
#         return redirect('lease:my_requests')
#     return render(request, 'lease/request_lease.html')

# # Employee: My Requests
# @login_required
# def my_requests(request):
#     leases = LeaseRequest.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'lease/my_requests.html', {'leases': leases})

# # Employee: S3 Data
# @login_required
# def s3_data(request):
#     lease = LeaseRequest.objects.filter(user=request.user, status='APPROVED', expiration__gt=timezone.now()).last()
#     data = []
#     if lease:
#         s3 = boto3.client(
#             's3',
#             aws_access_key_id=lease.access_key,
#             aws_secret_access_key=lease.secret_key,
#             aws_session_token=lease.session_token
#         )
#         try:
#             res = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME)
#             data = [obj['Key'] for obj in res.get('Contents',[])]
#         except Exception as e:
#             data = [f"Error: {str(e)}"]
#     return render(request, 'lease/s3_data.html', {'data': data})

# # Admin check
# def is_admin(user): return user.is_staff

# # Admin: Pending
# @login_required
# @user_passes_test(is_admin)
# def pending_requests(request):
#     leases = LeaseRequest.objects.filter(status='PENDING').order_by('created_at')
#     return render(request, 'lease/pending_requests.html', {'leases': leases})

# # Admin: Approved
# @login_required
# @user_passes_test(is_admin)
# def approved_requests(request):
#     leases = LeaseRequest.objects.filter(status='APPROVED').order_by('-approved_at')
#     return render(request, 'lease/approved_requests.html', {'leases': leases})

# # Admin: Rejected
# @login_required
# @user_passes_test(is_admin)
# def rejected_requests(request):
#     leases = LeaseRequest.objects.filter(status='REJECTED').order_by('-approved_at')
#     return render(request, 'lease/rejected_requests.html', {'leases': leases})

# # Admin: Approve / Reject
# @login_required
# @user_passes_test(is_admin)
# def approve_lease(request, lease_id):
#     lease = get_object_or_404(LeaseRequest, id=lease_id)
#     if request.method == 'POST':
#         action = request.POST['action']
#         if action == 'approve':
#             role_arn = settings.READ_ROLE_ARN if lease.role_requested=='READ' else settings.WRITE_ROLE_ARN
#             sts = boto3.client('sts')
#             assumed = sts.assume_role(RoleArn=role_arn, RoleSessionName=f"lease-{lease.id}", DurationSeconds=lease.duration_seconds)
#             creds = assumed['Credentials']
#             lease.status = 'APPROVED'
#             lease.approver = request.user
#             lease.approved_at = timezone.now()
#             lease.assumed_role_arn = assumed['AssumedRoleUser']['Arn']
#             lease.access_key = creds['AccessKeyId']
#             lease.secret_key = creds['SecretAccessKey']
#             lease.session_token = creds['SessionToken']
#             lease.expiration = creds['Expiration']
#             lease.save()
#         else:
#             lease.status = 'REJECTED'
#             lease.approver = request.user
#             lease.approved_at = timezone.now()
#             lease.save()
#         return redirect('lease:pending_requests')






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LeaseRequest
from django.utils import timezone
from django.conf import settings
import boto3
from datetime import datetime

# Home redirect
@login_required
def home(request):
    if request.user.is_staff:
        return redirect('lease:pending_requests')
    return redirect('lease:my_requests')


# Employee: Request Lease
@login_required
def request_lease(request):
    if request.method == 'POST':
        role = request.POST['role']
        reason = request.POST['reason']
        duration = int(request.POST.get('duration', 3600))
        LeaseRequest.objects.create(
            user=request.user,
            role_requested=role,
            reason=reason,
            duration_seconds=duration
        )
        return redirect('lease:my_requests')
    return render(request, 'lease/request_lease.html')


# Employee: My Requests
@login_required
def my_requests(request):
    leases = LeaseRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'lease/my_requests.html', {'leases': leases})


# Employee: S3 Data
@login_required
def s3_data(request):
    lease = LeaseRequest.objects.filter(
        user=request.user,
        status='APPROVED',
        expiration__gt=timezone.now()
    ).last()
    data = []

    if lease:
        # Use LocalStack endpoint if defined
        endpoint_url = getattr(settings, 'AWS_ENDPOINT_URL', None)
        s3 = boto3.client(
            's3',
            aws_access_key_id=lease.access_key,
            aws_secret_access_key=lease.secret_key,
            aws_session_token=lease.session_token,
            endpoint_url=endpoint_url
        )
        try:
            res = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME)
            data = [obj['Key'] for obj in res.get('Contents', [])]
        except Exception as e:
            data = [f"Error: {str(e)}"]
    return render(request, 'lease/s3_data.html', {'data': data})



# @login_required
# def s3_write(request):
#     lease = LeaseRequest.objects.filter(
#         user=request.user,
#         status='APPROVED',
#         role_requested='WRITE',
#         expiration__gt=timezone.now()
#     ).last()
#     print("Lease:", lease)
#     message = ''
#     if request.method == 'POST' and lease:
#         file = request.FILES.get('file')
#         if file:
#             s3 = boto3.client(
#                 's3',
#                 aws_access_key_id=lease.access_key,
#                 aws_secret_access_key=lease.secret_key,
#                 aws_session_token=lease.session_token,
#                 endpoint_url=getattr(settings, 'AWS_ENDPOINT_URL', None)
#             )
#             print("s3",s3)
#             try:
#                 s3.upload_fileobj(file, settings.S3_BUCKET_NAME, file.name)
#                 message = f"File '{file.name}' uploaded successfully!"
#             except Exception as e:
#                 message = f"Error: {str(e)}"
#         else:
#             message = "No file selected."

#     return render(request, 'lease/s3_write.html', {'message': message})


@login_required
def s3_write(request):
    # Get latest approved WRITE lease that hasn’t expired
    lease = LeaseRequest.objects.filter(
        user=request.user,
        status='APPROVED',
        role_requested='WRITE',
        expiration__gt=timezone.now()
    ).last()

    message = ''
    if request.method == 'POST' and lease:
        file = request.FILES.get('file')
        if file:
            s3 = boto3.client(
                's3',
                aws_access_key_id=lease.access_key,
                aws_secret_access_key=lease.secret_key,
                aws_session_token=lease.session_token,
                endpoint_url=getattr(settings, 'AWS_ENDPOINT_URL', None)
            )
            try:
                s3.upload_fileobj(file, settings.S3_BUCKET_NAME, file.name)
                message = f"File '{file.name}' uploaded successfully!"
            except Exception as e:
                message = f"Error: {str(e)}"
        else:
            message = "No file selected."

    # Pass 'lease' to template so the form can display
    return render(request, 'lease/s3_write.html', {'message': message, 'lease': lease})


# Admin check
def is_admin(user):
    return user.is_staff


# Admin: Pending
@login_required
@user_passes_test(is_admin)
def pending_requests(request):
    leases = LeaseRequest.objects.filter(status='PENDING').order_by('created_at')
    return render(request, 'lease/pending_requests.html', {'leases': leases})


# Admin: Approved
@login_required
@user_passes_test(is_admin)
def approved_requests(request):
    leases = LeaseRequest.objects.filter(status='APPROVED').order_by('-approved_at')
    return render(request, 'lease/approved_requests.html', {'leases': leases})


# Admin: Rejected
@login_required
@user_passes_test(is_admin)
def rejected_requests(request):
    leases = LeaseRequest.objects.filter(status='REJECTED').order_by('-approved_at')
    return render(request, 'lease/rejected_requests.html', {'leases': leases})


# Admin: Approve / Reject
@login_required
@user_passes_test(is_admin)
def approve_lease(request, lease_id):
    lease = get_object_or_404(LeaseRequest, id=lease_id)
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'approve':
            # Choose correct role ARN
            role_arn = settings.READ_ROLE_ARN if lease.role_requested == 'READ' else settings.WRITE_ROLE_ARN

            # Use LocalStack endpoint for STS
            sts = boto3.client('sts', endpoint_url=getattr(settings, 'AWS_ENDPOINT_URL', None))

            # Assume role
            assumed = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=f"lease-{lease.id}",
                DurationSeconds=lease.duration_seconds
            )
            creds = assumed['Credentials']

            # Update lease request with temporary credentials
            lease.status = 'APPROVED'
            lease.approver = request.user
            lease.approved_at = timezone.now()
            lease.assumed_role_arn = assumed['AssumedRoleUser']['Arn']
            lease.access_key = creds['AccessKeyId']
            lease.secret_key = creds['SecretAccessKey']
            lease.session_token = creds['SessionToken']
            lease.expiration = creds['Expiration']
            lease.save()

        else:  # Reject
            lease.status = 'REJECTED'
            lease.approver = request.user
            lease.approved_at = timezone.now()
            lease.save()

        return redirect('lease:pending_requests')

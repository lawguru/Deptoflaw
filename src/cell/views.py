from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from staff.models import StaffProfile
from settings.models import Setting
from user.models import User
from .forms import ContactUsForm, NoticeForm
from .models import Notice, Quote

# Create your views here.


def index(request):
    home_heading, created = Setting.objects.get_or_create(key='home_heading')
    
    random_quote = Quote.objects.order_by('?').first()

    if home_heading.value == None:
        home_heading.value = 'Training & Placement Cell'
        home_heading.save()

    home_subheading, created = Setting.objects.get_or_create(
        key='home_subheading')
    if home_subheading.value == None:
        home_subheading.value = 'Assam University, Department of\nComputer Science and Engineering'
        home_subheading.save()

    home_description, created = Setting.objects.get_or_create(
        key='home_description')
    if home_description.value == None:
        home_description.value = 'Training & Placement Cell (TPC) handles all aspects of campus placements for the graduating students of the Department. TPC of Assam University\'s Department of Computer Science and Engineering (CSE) is well equipped with excellent infrastructure to support each and every stage of the placement processes. TPC staff members and student team assist in arranging Pre-Placement Talks, Written Tests, Group Discussions, and Interviews etc. as per the requirements of the Organizations and Recruiters.'
        home_description.save()

    message_from_hod, created = Setting.objects.get_or_create(
        key='message_from_hod')
    if message_from_hod.value == None:
        message_from_hod.value = 'Welcome to the Department of Computer Science and Engineering at Assam University. The Department of Computer Science and Engineering is one of the premier departments in the University. The Department offers B.Tech, M.Tech and Ph.D. programs in Computer Science and Engineering. The Department has a team of highly qualified, experienced and dedicated faculty members. The Department has state-of-the-art laboratories and infrastructure. The Department has a very active Training and Placement Cell (TPC) which takes care of the training and placement of the students. The Department has a very active student community which organizes various technical and cultural events throughout the year.'
        message_from_hod.save()

    message_from_tpc_head, created = Setting.objects.get_or_create(
        key='message_from_tpc_head')
    if message_from_tpc_head.value == None:
        message_from_tpc_head.value = 'Welcome to the Training and Placement Cell (TPC) of the Department of Computer Science'
        message_from_tpc_head.save()

    data = {
        'home_heading': home_heading.value,
        'home_subheading': home_subheading.value.splitlines(),
        'home_description': home_description.value,
        'quote': random_quote,
        'message_from_hod': message_from_hod.value,
        'message_from_tpc_head': message_from_tpc_head.value,
        'hod': StaffProfile.objects.get(is_hod=True) if StaffProfile.objects.filter(is_hod=True).exists() else None,
        'tpc_head': StaffProfile.objects.get(is_tpc_head=True) if StaffProfile.objects.filter(is_tpc_head=True).exists() else None,
        'coordinators': User.objects.filter(groups__name='coordinators') if User.objects.filter(groups__name='coordinators').exists() else None,
    }
    return render(request, 'index.html', data)


def contact(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': form, 'success': 'Your message has been sent successfully!'})
        else:
            return render(request, 'contact.html', {'form': form, 'error': 'Could not send your message. Please try again.'})
    return render(request, 'contact.html', {'form': ContactUsForm})


def notices(request):
    notices = Notice.objects.all()
    return render(request, 'notices.html', {'notices': notices})

@permission_required('cell.add_notice')
def add_notice(request):
    if request.method == 'POSt':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'add_notice.html', {'form': NoticeForm, 'success': 'Notice added successfully!'})
        else:
            return render(request, 'add_notice.html', {'form': NoticeForm, 'error': 'Could not add notice. Please try again.'})
    return render(request, 'add_notice.html', {'form': NoticeForm, })

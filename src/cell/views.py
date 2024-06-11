from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from staff.models import StaffProfile
from settings.models import Setting
from user.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from views import AddUserKeyObject, ChangeUserKeyObject, AddObject, DeleteUserKeyObject
from django.views.generic.base import TemplateView, RedirectView
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, BadRequest
from .forms import *
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


@method_decorator(login_required, name="dispatch")
class ListRecruitmentPost(TemplateView):
    template_name = 'recruitment_posts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = RecruitmentPost.objects.filter(user=kwargs['user'])
        return context


@method_decorator(login_required, name="dispatch")
class AddRecruitmentPost(AddUserKeyObject):
    model = RecruitmentPost
    form = AddRecruitmentPostForm
    template_name = 'add_recruitment_post.html'
    redirect_url_name = 'recruitment_posts'

    def check_permission(self, request, *args, **kwargs):
        if User.objects.get(pk=kwargs['user']).role != 'recruiter':
            return False
        return super().check_permission(request, kwargs['user'], *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not User.objects.filter(pk=kwargs['user']).exists():
            raise ObjectDoesNotExist()
        if not self.check_permission(request, *args, **kwargs):
            raise PermissionDenied()
        if self.template_name and self.form:
            user = User.objects.get(pk=kwargs['user'])
            return render(request, self.template_name, {'form': self.form(initial={'company': user.recruiter_profile.company_name})})
        return redirect(self.get_redirect_url(request, *args, **kwargs))


@method_decorator(login_required, name="dispatch")
class ViewRecruitmentPost(TemplateView):
    template_name = 'recruitment_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = RecruitmentPost.objects.get(pk=kwargs['pk'])
        context['updates'] = [(update, RecruitmentPostUpdateForm(instance=update)) for update in context['post'].updates.all()]
        if context['post'].user == self.request.user or self.request.user.is_superuser or self.request.user.is_coordinator:
            context['update_form'] = RecruitmentPostUpdateForm()
        if self.request.user == context['post'].user:
            context['edit_form'] = RecruiterChangeRecruitmentPostForm(
                instance=context['post'])
        if self.request.user.is_superuser or self.request.user.is_coordinator:
            context['edit_form'] = TPCChangeRecruitmentPostForm(
                instance=context['post'])
        if self.request.user.role == 'student':
            if context['post'].applications.filter(user=self.request.user).exists():
                context['application'] = context['post'].applications.get(user=self.request.user)
            if context['post'].is_active:
                context['apply_form'] = RecruitmentApplicationForm()
        return context

    def get(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().get(request, pk=pk)


@method_decorator(login_required, name="dispatch")
class RecruiterChangeRecruitmentPost(ChangeUserKeyObject):
    model = RecruitmentPost
    form = RecruiterChangeRecruitmentPostForm
    redirect_url_name = 'view_recruitment_post'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [pk]

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class TPCChangeRecruitmentPost(RecruiterChangeRecruitmentPost):
    form = TPCChangeRecruitmentPostForm

    def check_permission(self, request, pk, *args, **kwargs):
        if request.user.is_superuser or request.user.is_coordinator:
            return True
        return RecruiterChangeRecruitmentPost.check_permission(self, request, pk, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ChangeRecruitmentPost(TPCChangeRecruitmentPost):
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_superuser or request.user.is_coordinator:
            self.form = TPCChangeRecruitmentPost.form
            return TPCChangeRecruitmentPost.post(self, request, pk, *args, **kwargs)
        self.form = RecruiterChangeRecruitmentPost.form
        return RecruiterChangeRecruitmentPost.post(self, request, pk, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class AddRecruitmentPostUpdate(AddObject):
    model = RecruitmentPostUpdate
    form = RecruitmentPostUpdateForm
    redirect_url_name = 'view_recruitment_post'

    def check_permission(self, request, *args, **kwargs):
        if kwargs['recruitment_post'].user == request.user or request.user.is_superuser or request.user.is_coordinator:
            return True
        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_params(self, request, *args, **kwargs):
        return f'#updates-last'

    def get_redirect_url_args(self, request, *args, **kwargs):
        return [kwargs['recruitment_post'].pk]

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().post(request, recruitment_post=RecruitmentPost.objects.get(pk=pk), user=request.user)


@method_decorator(login_required, name="dispatch")
class ChangeRecruitmentPostUpdate(ChangeUserKeyObject):
    model = RecruitmentPostUpdate
    form = RecruitmentPostUpdateForm
    redirect_url_name = 'view_recruitment_post'

    def check_permission(self, request, pk, *args, **kwargs):
        obj = self.model.objects.get(pk=pk)
        if obj.user == request.user or obj.recruitment_post.user == request.user or request.user.is_superuser:
            return True
        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_params(self, request, pk, *args, **kwargs):
        return f'#update-{pk}'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [self.model.objects.get(pk=pk).recruitment_post.pk]

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class DeleteRecruitmentPostUpdate(DeleteUserKeyObject):
    model = RecruitmentPostUpdate
    redirect_url_name = 'view_recruitment_post'

    def check_permission(self, request, pk, *args, **kwargs):
        obj = self.model.objects.get(pk=pk)
        if obj.user == request.user or obj.recruitment_post.user == request.user or request.user.is_superuser:
            return True
        return super().check_permission(request, *args, **kwargs)

    def get_redirect_url_params(self, request, pk, *args, **kwargs):
        return '#updates'

    def get_redirect_url_args(self, request, pk, *args, **kwargs):
        return [self.model.objects.get(pk=pk).recruitment_post.pk]

    def get(self, request, pk):
        raise BadRequest()


@method_decorator(login_required, name="dispatch")
class AddRecruitmentApplication(AddObject):
    model = RecruitmentApplication
    form = RecruitmentApplicationForm
    redirect_url_name = 'recruitment_application'

    def check_permission(self, request, *args, **kwargs):
        if not kwargs['recruitment_post'].is_active or kwargs['recruitment_post'].applications.filter(user=request.user).exists() or request.user.role != 'student':
            return False

        return super().check_permission(request, *args, **kwargs)

    def get(self, request, pk):
        raise BadRequest()

    def post(self, request, pk):
        if not RecruitmentPost.objects.filter(pk=pk).exists():
            raise ObjectDoesNotExist()
        return super().post(request, recruitment_post=RecruitmentPost.objects.get(pk=pk), user=request.user)

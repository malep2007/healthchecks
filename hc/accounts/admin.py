from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.urls import reverse
from hc.accounts.models import Profile
from hc.api.models import Channel, Check


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('css/admin/profiles.css',)
        }

    list_display = ("id", "users", "reports_allowed", "next_report_date",
                    "ping_log_limit")
    search_fields = ["id", "user__email"]
    list_filter = ("reports_allowed", "team_access_allowed",
                   "next_report_date")

    def users(self, obj):
        if obj.member_set.count() == 0:
            return obj.user.email
        else:
            return render_to_string("admin/profile_list_team.html", {
                "profile": obj
            })

    users.allow_tags = True


class HcUserAdmin(UserAdmin):
    actions = ["send_report"]
    list_display = ('id', 'email', 'date_joined', 'involvement',
                    'is_staff', 'checks')

    ordering = ["-id"]

    def count_states(self, a, b):
        if a <= 1 and b <= 1:
            return "%d checks, %d channels" % (a, b)
        else:
            return "<strong>%d checks</strong><strong>%d channels</strong>" % (a, b)
        
        

    def involvement(self, user):
        result = ""
        num_checks = Check.objects.filter(user=user).count()
        num_channels = Channel.objects.filter(user=user).count()

        result = self.count_states(num_checks, num_channels)

        return result

    involvement.allow_tags = True

    def checks(self, user):
        url = reverse("hc-switch-team", args=[user.username])
        return "<a href='%s'>Checks</a>" % url

    checks.allow_tags = True

    def send_report(self, request, qs):
        for user in qs:
            user.profile.send_report()

        self.message_user(request, "%d email(s) sent" % qs.count())


admin.site.unregister(User)
admin.site.register(User, HcUserAdmin)

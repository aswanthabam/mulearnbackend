from django.db.models import Sum, Max, Prefetch, F, OuterRef, Subquery, IntegerField
from django.db import connection
from rest_framework.views import APIView

from .serializers import LaunchpadLeaderBoardSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.user import User
from db.organization import UserOrganizationLink
from db.task import KarmaActivityLog

class Leaderboard(APIView):
    def get(self, request):
        total_karma_subquery = KarmaActivityLog.objects.filter(
            user=OuterRef('id'),
            task__event='launchpad',
            appraiser_approved=True,
        ).values('user').annotate(
            total_karma=Sum('karma')
        ).values('total_karma')

        intro_task_completed_users = KarmaActivityLog.objects.filter(
            task__event='launchpad',
            appraiser_approved=True,
            task__hashtag='#lp24-introduction',
        ).values('user')

        allowed_org_types = UserOrganizationLink.objects.filter(
                        org__org_type__in=["College", "School", "Company"])
                    

        users = User.objects.filter(
                karma_activity_log_user__task__event="launchpad",
                karma_activity_log_user__appraiser_approved=True,
                id__in=intro_task_completed_users,
                user_organization_link_org__in=allowed_org_types,
            ).annotate(
                karma=Subquery(total_karma_subquery, output_field=IntegerField()),
                org=F("user_organization_link_user__org__title"),
                district_name=F("user_organization_link_user__org__district__name"),
                state=F("user_organization_link_user__org__district__zone__state__name"),
                time_=Max("karma_activity_log_user__created_at"),
            ).order_by("-karma")
        
        paginated_queryset = CommonUtils.get_paginated_queryset(
            users,
            request,
            ["full_name","karma", "org", "district_name", "state"],
            sort_fields={
                "karma": "karma",
                "time_": "time_",
            },
        )

        serializer = LaunchpadLeaderBoardSerializer(
            paginated_queryset.get("queryset"), many=True
        )
        return CustomResponse().paginated_response(
            data=serializer.data, pagination=paginated_queryset.get("pagination")
        )
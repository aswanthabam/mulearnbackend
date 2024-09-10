from rest_framework import serializers
from db.mu_events import MuEvents, MuEventsKarmaRequest
from db.user import User
from db.task import InterestGroup, Organization, TaskList
from datetime import datetime


class MuEventsCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    assets = serializers.JSONField(required=False)
    location = serializers.CharField()
    task_id = serializers.CharField(required=True)
    org_id = serializers.CharField(required=False)
    lc_id = serializers.CharField(required=False)
    ig_id = serializers.CharField(required=False)
    scheduled_time = serializers.DateTimeField()

    def create(self, validated_data):
        user = User.objects.get(id=self.context.get("user_id"))
        validated_data["created_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_at"] = datetime.now()
        return super().update(instance, validated_data)

    def validate_task_id(self, value):
        task = TaskList.objects.filter(id=value).get()
        if not task:
            raise serializers.ValidationError("Task not found")
        return task

    class Meta:
        model = MuEvents
        fields = [
            "name",
            "description",
            "assets",
            "location",
            "task_id",
            "org_id",
            "lc_id",
            "ig_id",
            "scheduled_time",
        ]


class MuEventsCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    assets = serializers.JSONField(required=False)
    location = serializers.CharField()
    task_id = serializers.CharField(required=True)
    org_id = serializers.CharField(required=False)
    lc_id = serializers.CharField(required=False)
    ig_id = serializers.CharField(required=False)
    scheduled_time = serializers.DateTimeField()

    def create(self, validated_data):
        user = User.objects.get(id=self.context.get("user_id"))
        validated_data["created_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_at"] = datetime.now()
        return super().update(instance, validated_data)

    def validate_task_id(self, value):
        task = TaskList.objects.filter(id=value).get()
        if not task:
            raise serializers.ValidationError("Task not found")
        return task

    class Meta:
        model = MuEvents
        fields = [
            "name",
            "description",
            "assets",
            "location",
            "task_id",
            "org_id",
            "lc_id",
            "ig_id",
            "scheduled_time",
        ]


class MuEventsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField()
    description = serializers.CharField()
    scheduled_time = serializers.DateTimeField()
    assets = serializers.JSONField()
    location = serializers.CharField()
    task_id = serializers.CharField(source="task_id.title")
    suggestions = serializers.CharField()
    is_approved = serializers.BooleanField()
    approved_by = serializers.CharField(source="approved_by.full_name", default=None)
    created_by = serializers.CharField(source="created_by.full_name")
    org_id = serializers.CharField(source="org_id.name", default=None)
    lc_id = serializers.CharField(source="lc_id.name", default=None)
    ig_id = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_ig_id(self, obj):
        return InterestGroup.objects.filter(
            id__in=obj.ig_id if obj.ig_id else []
        ).values("name")

    class Meta:
        model = MuEvents
        fields = [
            "id",
            "name",
            "description",
            "scheduled_time",
            "assets",
            "location",
            "task_id",
            "suggestions",
            "is_approved",
            "approved_by",
            "created_by",
            "org_id",
            "lc_id",
            "ig_id",
            "created_at",
            "updated_at",
        ]


class MuEventsKarmaRequestSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    pow = serializers.JSONField(required=True)
    event_id = serializers.CharField(required=True, write_only=True)
    event_name = serializers.CharField(source="event_id.name", read_only=True)
    role = serializers.ChoiceField(choices=MuEventsKarmaRequest.ROLE_CHOICES)
    karma = serializers.IntegerField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    voucher_id = serializers.CharField(
        source="voucher_id.voucher_code", read_only=True, default=None
    )
    suggestions = serializers.CharField(read_only=True)
    approved_by_id = serializers.CharField(write_only=True, required=False)
    approved_by = serializers.CharField(
        source="approved_by.full_name", read_only=True, default=None
    )
    approved_at = serializers.DateTimeField(read_only=True)
    appraised_by_id = serializers.CharField(write_only=True, required=False)
    appraised_by = serializers.CharField(
        source="appraised_by.full_name",
        read_only=True,
        default=None,
    )
    appraised_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(source="created_by.full_name", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = User.objects.get(id=self.context.get("user_id"))
        validated_data["created_by"] = user
        pre_request = MuEventsKarmaRequest.objects.filter(
            event_id=validated_data["event_id"], created_by=user
        )
        if pre_request:
            raise serializers.ValidationError("Already requested for karma")
        validated_data["created_at"] = datetime.now()
        validated_data["updated_at"] = datetime.now()
        return super().create(validated_data)

    def validate_event_id(self, value):
        event = MuEvents.objects.filter(id=value).first()
        if not event:
            raise serializers.ValidationError("Event not found")
        return event

    def validate_approved_by_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user:
            raise serializers.ValidationError("User not found")
        return user

    def validate_appraised_by_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user:
            raise serializers.ValidationError("User not found")
        return user

    class Meta:
        model = MuEventsKarmaRequest
        fields = [
            "id",
            "pow",
            "event_id",
            "event_name",
            "role",
            "karma",
            "is_approved",
            "voucher_id",
            "suggestions",
            "approved_by_id",
            "approved_by",
            "approved_at",
            "appraised_by_id",
            "appraised_by",
            "appraised_at",
            "created_by",
            "created_at",
            "updated_at",
        ]


class MuEventVerificationSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField(initial=False, required=True)
    suggestions = serializers.CharField(required=False, default=None, max_length=500)
    user_id = serializers.CharField()
    event_id = serializers.CharField()

    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get("is_approved")
        instance.suggestions = validated_data.get("suggestions")
        instance.approved_by = User.objects.filter(
            id=validated_data.get("user_id")
        ).first()
        instance.approved_at = datetime.now()
        instance.save()
        return instance

    def validate_event_id(self, value):
        event = MuEvents.objects.filter(id=value).first()
        if not event:
            raise serializers.ValidationError("Event not found")
        return event

    def validate_user_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user:
            raise serializers.ValidationError("User not found")
        return user

    class Meta:
        fields = [
            "is_approved",
            "suggestions",
            "user_id",
        ]

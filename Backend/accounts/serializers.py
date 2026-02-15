from rest_framework import serializers
import Users.models as user_models


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = user_models.CustomUser
        fields = ["id", "email", "password", "date_of_birth"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = user_models.CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.CustomUser
        fields = ["id", "name", "email", "gender", "date_of_birth", "joined_date", "profile_image"]

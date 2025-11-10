from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'contraseña': {'write_only': True}}  # No mostrar la contraseña en respuestas

    def create(self, validated_data):
        """Crea un User con contraseña encriptada"""
        User = User(**validated_data)
        User.set_password(validated_data['contraseña'])
        User.save()
        return User

    def update(self, instance, validated_data):
        """Actualiza User y encripta la contraseña si se cambia"""
        for attr, value in validated_data.items():
            if attr == 'contraseña':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

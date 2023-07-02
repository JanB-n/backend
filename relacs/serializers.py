# serializers.py
from rest_framework import serializers
from .models import Compound
from django.contrib.auth.models import User
import sys
sys.path.append("..")
from users.serializers import RegistrationSerializer


class CompoundSerializer(serializers.ModelSerializer):
    id_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    #id_user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    name = serializers.CharField(required=True, max_length=50)
    molar_mass = serializers.FloatField(required=True, min_value=0)
    deltaT_actual = serializers.FloatField(required=False, min_value=0)
    deltaH_actual = serializers.FloatField(required=False, min_value=0)

    class Meta:
        model = Compound
        fields = ('id_user', 'name', 'molar_mass', 'deltaT_actual', 'deltaH_actual')

    def validate(self, args):
        name = args.get("name", None)
        molar_mass = args.get("molar_mass", None)
        id_user = args.get("id_user", None)
        print(args)
        print(id_user.email)
        
        
        if Compound.objects.filter(name=name).filter(id_user=id_user):
            raise serializers.ValidationError({"name": ("User already created this compound")})
        if molar_mass <= 0:
             raise serializers.ValidationError({"molar_mass": ("Molar mass <= 0")})
        return super().validate(args)
    
    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

        


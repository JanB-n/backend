from django.db import models
import sys
sys.path.append('../users')
from users.models import User
from django import forms

# Create your models here.

# class Team(models.Model):
#     name = models.CharField(max_length=30)

# class User(models.Model):
#     # id_team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     email = models.EmailField(max_length=30)
#     password = models.CharField(max_length=30)

class Compound(models.Model):
    # id_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    molar_mass = models.FloatField()
    deltaT_actual = models.FloatField()
    deltaH_actual = models.FloatField()

class Experiment(models.Model):
    id_compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.BinaryField()
    mdate = models.DateField()
    probe_mass = models.FloatField()

class Cluster(models.Model):
    id_experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    deltaT = models.FloatField()
    deltaH = models.FloatField()

class Measurement(models.Model):
    id_cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    T = models.FloatField()
    H= models.FloatField()
    ChiPrime = models.FloatField()
    ChiBis = models.FloatField()
    Freq = models.FloatField()
    hidden = models.BooleanField(default=False)

class Fit(models.Model):
    id_compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50)

class StartingParameter(models.Model):
    id_compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    max = models.FloatField()
    min = models.FloatField()

class CopiedMeasurement(models.Model):
    id_cluster = models.ForeignKey(Fit, on_delete=models.CASCADE)
    T = models.FloatField()
    H= models.FloatField()
    ChiPrime = models.FloatField()
    ChiBis = models.FloatField()
    Freq = models.FloatField()
    hidden = models.BooleanField(default=False)

class Relaxation(models.Model):
    id_fit = models.ForeignKey(Fit, on_delete=models.CASCADE)

class Parameter(models.Model):
    id_relaxation = models.ForeignKey(Relaxation, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    value = models.FloatField()
    max = models.FloatField()
    min = models.FloatField()
    error = models.FloatField()
    blocked = models.BooleanField(default=False)

class Fit3D(models.Model):
    id_fit = models.ManyToManyField(Fit)
    display_name = models.CharField(max_length=30)
    value = models.FloatField()
    max = models.FloatField()
    min = models.FloatField()
    error = models.FloatField()
    blocked = models.BooleanField(default=False)
    blockedon0 = models.BooleanField(default=False)





    
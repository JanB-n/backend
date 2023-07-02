from django.contrib import admin
from . models import *

# Register your models here.

# admin.site.register(Team)
#admin.site.register(User)
admin.site.register(Compound)
admin.site.register(Experiment)
admin.site.register(Cluster)
admin.site.register(Measurement)
admin.site.register(Fit)
admin.site.register(StartingParameter)
admin.site.register(CopiedMeasurement)
admin.site.register(Parameter)
admin.site.register(Relaxation)
admin.site.register(Fit3D)
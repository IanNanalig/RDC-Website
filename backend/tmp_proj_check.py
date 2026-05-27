import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rdc_site.settings')
import django
django.setup()
from projects.models import Project

projects = Project.objects.all().order_by('id')
print('COUNT', projects.count())
for p in projects:
    print(p.id, p.name, p.status, repr(p.agency), p.created_by_id, p.created_by.username if p.created_by else None, p.validated, p.archived)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rdc_site.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create_user(username='tmp_employee', password='password', role='staff', email='tmp_employee@example.com')
client = APIClient()
client.force_authenticate(user=user)

payload = {
    'title': 'Test Simplified Project',
    'description': 'Test description',
    'agency': 'MMDA',
    'budget': 1000,
    'completion': 0,
    'status': 'draft',
    'profile_data': {
        'submission_type': 'simplified',
        'templateName': 'RDIP 2023-2028 Simplified',
        'simplified_form': {
            'agencyName': 'MMDA',
            'program': 'Test Program',
            'projectActivity': 'Test Activity',
            'location': 'Test',
            'description': 'Test',
            'objective': 'Test',
            'startYear': '2024',
            'endYear': '2024',
            'fundingRequirementByYear': {'2024': '1000'},
            'actualFundingByYear': {'2024': '1000'},
            'fundingSource': 'NG-Local Funds (GAA)',
            'rdcEndorsed': 'Yes',
            'pipIncluded': 'Yes',
            'arnipapIncluded': 'Yes',
            'ludipIncluded': 'No',
            'ifpsIncluded': 'Yes',
            'pcbIncluded': 'No',
            'developmentSector': 'Infrastructure',
            'rdpMainChapter': '13 Expand and Upgrade Infrastructure Infrastructure',
            'status': 'Completed',
            'physicalAccomplishment': '0',
            'financialAccomplishment': '0',
            'remarks': 'Test',
        }
    }
}
res = client.post('/api/employee/projects/', payload, format='json')
print(res.status_code)
print(getattr(res, 'data', None) or res.content)

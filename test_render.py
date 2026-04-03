import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()
from django.test import RequestFactory
from apps.accounts.views import user_edit
from apps.accounts.models import User
factory = RequestFactory()
request = factory.get('/accounts/users/1/edit/')
user = User.objects.get(id=1)
request.user = user
try:
    response = user_edit(request, 1)
    print("STATUS", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()

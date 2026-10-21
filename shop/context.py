from .models import SiteSetting


def site(request):
    return {'site': SiteSetting.load()}

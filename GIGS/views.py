# Main GIGS views - Import ViewSets from subapps
from .CLIENTS.views import ClientViewSet
from .AUDIO.views import AudioEquipmentViewSet
from .CATERING.views import CateringViewSet
from .CLIENTS_REQUESTS.views import ClientRequestViewSet
from .REPERTORIE.views import RepertorioViewSet
from .EVENT_PHOTOS.views import EventPhotoViewSet
from .CONTRACT.views import ContractViewSet

# All ViewSets are now imported from their respective subapps
# This allows the main GIGS urls.py to register them properly
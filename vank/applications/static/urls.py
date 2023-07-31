from vank.core.config import conf
from vank.core import SubApplication
from vank.applications.static import views

sub = SubApplication("static", prefix=conf.STATIC_URL)
sub.add_route("/{fp:path}", views.StaticView, endpoint=conf.STATIC_ENDPOINT)

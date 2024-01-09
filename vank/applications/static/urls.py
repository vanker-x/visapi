from vank.core.config import conf
from vank.core import SubApplication
from vank.applications.static import views

sub = SubApplication("static", prefix=conf.STATIC_URL)
sub.get("/{fp:path}", endpoint=conf.STATIC_ENDPOINT)(views.handle_static_file)

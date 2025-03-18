# Drop all the routers right here

from .start import start_router
from .add_place import add_router
from .remove_place import remove_router
from .revote_day import revote_day_router
from .revote_time import revote_time_router
from .debug import debug_router
from .ping import ping_router

# NOTE: If you have blocking router, please drop it at the end of the other routers.
# If you don't do so the process will block all further routers

routers = [
    start_router,
    add_router,
    remove_router,
    revote_day_router,
    revote_time_router,
    debug_router,
    ping_router,
]
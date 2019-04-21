# Top level API for the mini-website
import hug
import src.controllers.status

# Global onetime setup when we first get going.
from src.utils.status_mgr import init_status
init_status()


@hug.get('/')
def say_hi():
    return "hi from root"

@hug.extend_api()
def with_other_apis():
    return [src.controllers.status]

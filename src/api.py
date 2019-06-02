# Top level API for the mini-website
import hug
import src.controllers.status
import src.controllers.logs
import src.controllers.dsfiles
import src.controllers.syncedds

@hug.extend_api()
def with_other_apis():
    return [
        src.controllers.status,
        src.controllers.logs,
        src.controllers.dsfiles,
        src.controllers.syncedds
        ]

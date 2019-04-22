# Top level API for the mini-website
import hug
import src.controllers.status
import src.controllers.logs

@hug.get('/')
def say_hi():
    return "hi from root"

@hug.extend_api()
def with_other_apis():
    return [src.controllers.status, src.controllers.logs]

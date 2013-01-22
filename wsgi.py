import os
import sys
from app import app as application


sys.path.append('/home/dotcloud/current')

application.config.update(DEBUG=os.environ.get('DEBUG', False))

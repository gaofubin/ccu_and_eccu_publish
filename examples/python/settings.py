import os
username='input your username'
password='input your password'
notification_email='input your notification email'
endpoint='https://control.akamai.com/webservices/services/PublishECCU'
wsdl_url='file://%s' % os.path.join(os.path.dirname(__file__), 'PublishECCU.wsdl')

print wsdl_url
try:
    from settings_local import *
except ImportError:
    pass

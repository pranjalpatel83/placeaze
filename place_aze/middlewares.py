from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from django.utils.deprecation import MiddlewareMixin


class OneSessionPerUser:
    def __init__(self,get_response):
        self.get_response=get_response
        
    def __call__(self,request):
        if request.user.is_authenticated:
            current_session_key=request.user.logged_in_user.session_key
            
            if current_session_key and current_session_key!=request.session.session_key:
                Session.objects.get(session_key=current_session_key).delete()
            
            request.user.logged_in_user.session_key=request.session.session_key
            request.user.logged_in_user.save()
        response=self.get_response(request)
        
        return response
    
class SessionExpiryMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the current time
        now = datetime.now()
        
        # Iterate over session keys
        keys_to_delete = []
        for key, value in request.session.items():
            if isinstance(value, dict) and 'expiryTime' in value:
                expiry_time_str = value['expiryTime']
                # Convert the expiry time from string to datetime object
                expiry_time = datetime.strptime(expiry_time_str, '%Y-%m-%d %H:%M:%S')
                # Check if the expiry time has passed
                if expiry_time < now:
                    keys_to_delete.append(key)
        
        # Delete expired keys from session
        for key in keys_to_delete:
            del request.session[key]
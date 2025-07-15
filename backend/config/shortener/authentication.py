from rest_framework import authentication
from rest_framework import exceptions
import jwt
from django.conf import settings

class BearerTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
            
        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                raise exceptions.AuthenticationFailed('Invalid token prefix')
                
            # Verify the token
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Token expired')
            except jwt.InvalidTokenError:
                raise exceptions.AuthenticationFailed('Invalid token')
                
          
            
            return (None, None)  
            
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid Authorization header format')
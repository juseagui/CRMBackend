from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, authentication, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ExpiringTokenAuthentication(TokenAuthentication):
    
    def expires_in(self,token):
        # return left time of token
        time_elapsed = timezone.now() - token.created
        left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
        return left_time

    def is_token_expired(self,token):
        # return True if token is alive or False if token is expired
        return self.expires_in(token) < timedelta(seconds = 0)

    def token_expire_handler(self,token):
        is_expire = self.is_token_expired(token)
        if is_expire:
            user = token.user
            token.delete()
            token = self.get_model().objects.create(user=user)
        
        return  token

    def authenticate_credentials(self,key):
        token, user = None, None
        try:
            #token = self.get_model().objects.select_related('user').get(key=key)
            token = self.token_expire_handler(
                self.get_model().objects.select_related('user').get(key=key)
            )
            user = token.user
            #token = self.token_expire_handler(token)
        except self.get_model().DoesNotExist:
            #message = "token inválido"
            #self.expired = True
            pass

        return user

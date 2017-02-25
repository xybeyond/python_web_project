#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xybeyond'

'''
JSON API definition
'''

import json, logging, inspect, functools

class APIError(Exception):
    '''
    the base APIError which contains error(required), data(optional) and message(optional)
    '''
    
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
     indicate the input has error and invaild.The data specifies the error firld of inut form
    '''
    
    def __init__(self, field, message=''):
        super(APIValue, self).__init__('value:invaild', field, message)
 
class APIResourceNotFoundError(APIError):
    
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:not found', field, message)
     
class APIPermissionError(APIError):
    
    def __init__(self, field, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
# Disctionary of the API endpoints
import requests,base64,urlparse

endpoints = {
        'get_carrier':'carriers/getcarrier',
        'list_carriers':'carriers',
        'list_services':'carriers/listservices',
        'list_packages':'carriers/listpackages',
    }

carrier_carrier_map = {
        'code':'code',
        'name':'name',
        'accountNumber':'account_no',
        'requiresFundedAccount':'requires_funded_account',
        'balance':'balance',
        'shippingProviderId':'shipping_provider_id',
        'primary':'primary',
    }

carrier_service_map = {
        'code':'code',
        'name':'name',
        'domestic':'domestic',
        'international':'international',
    }

carrier_package_map = {
        'code':'code',
        'name':'name',
        'domestic':'domestic',
        'international':'international',
    }

def map_field(map,vals):
    # Considering the vals dictioanry has shipstation keys which need to be replaced by the Odoo fields
    return { val:vals[key] for key,val in map.iteritems()}

def get_url(base_url,endpoint=''):
    # qs is a dictionary of querystrings
    url = urlparse.urljoin(base_url,endpoint)
    return url

def get_authorization_token(api_key,api_secret):
    s = ":".join([api_key or 'api_key',api_secret or 'api_secret'])
    return "Basic "+ base64.b64encode(s)

def get_authorization_header(api_key,api_secret):
    return {'Authorization':get_authorization_token(api_key, api_secret)}

def make_request(url,headers,params={}):
    #Takes url header and params and return json format
    response = requests.get(url,headers=headers,params=params)
    return response
    
def get_carrier(api_key,api_secret,code,base_url):
    headers = get_authorization_header(api_key, api_secret)
    endpoint = endpoints['get_carrier']
    url = get_url(base_url,endpoint)
    response = make_request(url,headers,{'carrierCode':code})
    return response

def list_services(api_key,api_secret,code,base_url):
    headers = get_authorization_header(api_key, api_secret)
    endpoint = endpoints['list_services']
    url = get_url(base_url,endpoint)
    response = make_request(url,headers,{'carrierCode':code})
    return response 

def list_packages(api_key,api_secret,code,base_url):
    headers = get_authorization_header(api_key, api_secret)
    endpoint = endpoints['list_packages']
    url = get_url(base_url,endpoint)
    response = make_request(url,headers,{'carrierCode':code})
    return response        
        
    
    
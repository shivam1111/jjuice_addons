import boto3,botocore
import urlparse,os
import base64
import logging
import hashlib
_logger = logging.getLogger(__name__)

def get_url(bucket_location,bucket,key,fname):
    return os.path.join(bucket_location,bucket,key,fname)

def get_bucket_location(self,bucket):
    # This method just takes in bucket name and then joins accesss key and id with bucket to create a standard url
    # accepted by other method
    # accpeted location is -: amazons3://access_key_id:secret_access_key@jjuice-django
    access_key_id = self.env['ir.config_parameter'].get_param('aws_access_id')
    secret_access_key = self.env['ir.config_parameter'].get_param('aws_secret_key')
    return ('').join(['amazons3://',access_key_id,":",secret_access_key,"@",bucket])

def get_s3_client(access_key_id,secret_access_key):
    s3_conn = boto3.client(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
    )
    return s3_conn

def lookup(s3_conn,bucket,key='/'):
    # checks is a bucket exists or not
    try:
        result = s3_conn.get_object(
            Bucket=bucket,
            Key=key # this will add a forward slash if not present
            )
        return True
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        _logger.exception(e)
        return False

def put_object_bucket(location,key,value):
    # location = amazons3://access_key_id:secret_access_key@bucket
    # Example = amazons3://access_key_id:secret_access_key@jjuice-django
    # value = content of the file
    # key = folder path inside bucket
    
    loc_parse = urlparse.urlparse(location)
    assert loc_parse.scheme == 'amazons3', \
        "This method is intended only for amazons3://"

    access_key_id = loc_parse.username
    secret_key = loc_parse.password

    if not access_key_id or not secret_key:
        assert False, \
            "Must define access_key_id and secret_access_key in amazons3:// scheme"
        
    s3_conn = get_s3_client(access_key_id,secret_key)
    bin_value = value.decode('base64')
    fname = hashlib.sha1(bin_value).hexdigest()
    # Checking whether configured folder exist
    # For checking if folder is present it has to end with forward slash
    exists = lookup(s3_conn,loc_parse.hostname,os.path.join(key,'')) # adding slash safely
    if exists:
        s3_conn.put_object(Bucket=loc_parse.hostname, Key = '/'.join([key,fname]),Body=bin_value)
    else:
        assert False, \
            "Probably the root bucket path or key does not exist or invalid"
    return fname

def get_object_bucket(location,key,fname):
    read = None
    if fname:
        loc_parse = urlparse.urlparse(location)
        assert loc_parse.scheme == 'amazons3', \
            "This method is intended only for amazons3://"
    
        access_key_id = loc_parse.username
        secret_key = loc_parse.password
    
        if not access_key_id or not secret_key:
            assert False, \
                "Must define access_key_id and secret_access_key in amazons3:// scheme"
            
        s3_conn = get_s3_client(access_key_id,secret_key)
        exists = lookup(s3_conn,loc_parse.hostname,'/'.join([key,fname])) 
        if exists:
            bin_value  = s3_conn.get_object(Bucket=loc_parse.hostname, Key = '/'.join([key,fname]))
            read = base64.b64encode(bin_value.get('Body').read())
    return read

def delete_object_bucket(location,key,fname):
    delete = None
    if fname:
        loc_parse = urlparse.urlparse(location)
        assert loc_parse.scheme == 'amazons3', \
            "This method is intended only for amazons3://"
    
        access_key_id = loc_parse.username
        secret_key = loc_parse.password
    
        if not access_key_id or not secret_key:
            assert False, \
                "Must define access_key_id and secret_access_key in amazons3:// scheme"
            
        s3_conn = get_s3_client(access_key_id,secret_key)             
        exists = lookup(s3_conn,loc_parse.hostname,'/'.join([key,fname])) 
        if exists:
            delete = s3_conn.delete_object(Bucket=loc_parse.hostname, Key = '/'.join([key,fname]))
        return delete

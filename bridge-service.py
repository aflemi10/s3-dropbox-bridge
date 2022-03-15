import requests
import os
import boto3
import time
from datetime import datetime
import yaml

#reading in config file
with open (r'config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

dropbox_auth = config['dropbox_auth']
temp_dir_name = config['temp_dir_name']
bucket_name = config['bucket_name']
path = config['path']
delay = config['delay']


def main():
    #request to get files available in db
    headers = {
        'Authorization': 'Bearer '+ dropbox_auth,
        'Content-Type': 'application/json',
    }
    json_data = {
        'path': path,
    }
    response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, json=json_data)
    ########################


    #retrieving files in bucket and stripping out unneeded info
    client = boto3.client('s3')
    check_create_bucket()
    res = client.list_objects(Bucket = bucket_name)
    s3_files = []
    s3_hashes = []
    try:
        for fi in res['Contents']:
            s3_files.append({
                'Key':fi['Key'],
                'size':fi['Size'],
                'h': hash(str(fi['Key'])+str(fi['Size']))
                })
            s3_hashes.append(hash(str(fi['Key'])+str(fi['Size'])))
    except KeyError:
        pass
    #########################


    #getting only needed info from dropbox response
    try:
        files = response.json()['entries']
    except KeyError:
        print('Failed to fetch file names from dropbox')
        raise(KeyError)

    dropbox_files = [] 
    db_hashes = []
    for f in files:
        dropbox_files.append({
            'path_display':f['path_display'],
            'id':f['id'],
            'server_modified':f['server_modified'],
            'size':f['size'],
            'Key': f['path_display'].split('/')[-1],
            'h':hash(str(f['path_display'].split('/')[-1])+str(f['size']))
        })
        db_hashes.append(hash(str(f['path_display'].split('/')[-1])+str(f['size'])))
    #########################

 
    #hashing db and strs of db and s3 files
    db_hashes.sort()
    s3_hashes.sort()
    db_hash = hash(str(db_hashes))
    s3_hash = hash(str(s3_hashes))
    print(f'{datetime.now()} - Hash Diff: {db_hash != s3_hash }')
    #######################

    if db_hash != s3_hash:
        diff_hashes = set(s3_hashes).symmetric_difference(set(db_hashes))
        
        for dh in diff_hashes:
            if dh in s3_hashes:
                try:
                    #detect files that are in s3 and not in dropbox 
                    #delete from s3
                    s3_file = None
                    for d in s3_files:
                        if d['h'] == dh:
                            s3_file = d

                    delete_from_s3(s3_file)
                    ############################################
                except Exception as e:
                    print("Failed: s3 upload")
                    print(e)
                    pass

            else:##dh in dropbox files
                # find object associated with hash in dropbox_files and upload
                try:
                    db_file = None
                    for d in dropbox_files:
                        if d['h'] == dh:
                            db_file = d
                    
                    db_to_s3(db_file)
                except Exception as e:
                    print("Failed: s3 delete")
                    print(e)
                    pass
                #detect files that are in dropbox and not in s3
                #download from dropbox and upload to s3
                ############################################



def db_to_s3(file):
    #create temp directory for downloaded images
    try:
        os.mkdir(temp_dir_name)
    except FileExistsError :
        pass

    ###############################
    # calls download script which downloads the specified images
    # arg1 = access token
    # arg2 = path
    # arg3 = file_name to be downloaded
    # arg4 = dir name to be downloaded to 
    file_name = file['path_display'].split('/')[-1]
    os.system(f'./df.sh {dropbox_auth} {path} {file_name} {temp_dir_name}')
    ###############################

    #Uploads file to s3
    file_name = file['path_display'].split('/')[-1]
    client = boto3.client('s3')
    client.upload_file(temp_dir_name+'/'+file_name, bucket_name,file_name)
    ##########################

    #Make uploaded file object public
    s3 = boto3.resource('s3')
    object_acl = s3.ObjectAcl(bucket_name,file_name)
    response = object_acl.put(ACL='public-read')
    ##########################
    
    #delete temp
    os.system('rm -rf '+temp_dir_name)
    #######################
        

def delete_from_s3(s3_file):
    #deletes given file from s3
    client = boto3.client('s3')
    client.delete_object(  Bucket = bucket_name,Key=s3_file['Key'])
    ###########################

def check_create_bucket():
    #Gets list of bucket names
    client = boto3.client('s3')
    res = client.list_buckets()
    ############################

    #Check for bucket name in bucket names
    bucket_names = []
    for x in res['Buckets']:
        if bucket_name == x['Name']:
            return#returns if bucket already exist
    ##############################

    #Create bucket 
    client = boto3.client('s3')
    client.create_bucket(Bucket = bucket_name)
    ##########################

 
if __name__ == '__main__':
    while 1:       
        main()
        time.sleep(delay)
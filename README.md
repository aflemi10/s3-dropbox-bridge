# s3-dropbox-bridge
## Usage 
This is a basic bridge service that will repeatedly fetch files from dropbox and upload them to an s3 bucket.
## Prerequisites
- Curl
- Python3 + pip
- AWS-CLI [Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) [Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [Dropbox api credentials](https://www.dropbox.com/developers/reference/getting-started#app%20console) 
## Configuring
- dropbox_auth: enter your dropbox api token
- temp_dir_name: name of temporary directory
- bucket_name: name of the s3 bucket to send files to
- path: path of directory to download files from
- delay: time in seconds in between trying to update files
## Run
```
python3 bridge-service.py
```

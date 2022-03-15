#! /bin/sh
curl -X POST https://content.dropboxapi.com/2/files/download --header "Authorization: Bearer $1" --header "Dropbox-API-Arg: {\"path\" : \"$2/$3\" }" --output "$3"
mv $3 $4
#!/bin/sh

S=`pwd`

# Generate constants_local.py for flux app.
echo "1. Setup constants for MicrobesFlux"

# Check if constants_local.py exists. This is to make the operation idempotent.
if [[ ! -f microbesflux/constants_local.py ]]; then
  echo '' > flux/constants_local.py
  echo "kegg_database = \"${S}/kegg_database/\" " >> flux/constants_local.py
  echo "baseurl = \"${S}/flux/\" " >> flux/constants_local.py
fi

echo "2. Rewrite settings_local.py under microbesflux"
mkdir -p session
mkdir -p media

# Check if settings.py exists. This is to make the operation idempotent.
if [[ ! -f microbesflux/settings_local.py ]]; then
 touch microbesflux/settings_local.py 
 echo "MEDIA_ROOT " >> microbesflux/settings_local.py 
 echo "SESSION_FILE_PATH " >> microbesflux/settings_local.py 
fi

# Change Django settings.
platform=`uname`
if [[ $platform == 'Darwin' ]]; then
	sed -i "" "s%^MEDIA_ROOT.*\$%MEDIA_ROOT = \'${PWD}/media/\'%g " microbesflux/settings_local.py
	sed -i "" "s%^SESSION_FILE_PATH.*\$%SESSION_FILE_PATH = \'${PWD}/session/\'%g " microbesflux/settings_local.py
else 
	sed -i "s%^MEDIA_ROOT.*\$%MEDIA_ROOT = \'${PWD}/media/\'%g " microbesflux/settings_local.py
	sed -i "s%^SESSION_FILE_PATH.*\$%SESSION_FILE_PATH = \'${PWD}/session/\'%g " microbesflux/settings_local.py
fi
#SESSION_FILE_PATH

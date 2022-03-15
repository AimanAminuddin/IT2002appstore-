# Construct the URI from the .env
DB_HOST=''
DB_NAME=''
DB_USER=''
DB_PORT=''
DB_PASSWORD=''

while IFS= read -r line
do
  if [[ $line == DB_HOST* ]]
  then
    DB_HOST=$(cut -d "=" -f2- <<< $line | tr -d \')
  elif [[ $line == DB_NAME* ]]
  then
    DB_NAME=$(cut -d "=" -f2- <<< $line | tr -d \' )
  elif [[ $line == DB_USER* ]]
  then
    DB_USER=$(cut -d "=" -f2- <<< $line | tr -d \' )
  elif [[ $line == DB_PORT* ]]
  then
    DB_PORT=$(cut -d "=" -f2- <<< $line | tr -d \')
  elif [[ $line == DB_PASSWORD* ]]
  then
    DB_PASSWORD=$(cut -d "=" -f2- <<< $line | tr -d \')
  fi
done < ".env"
a = 1 
URI="postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

# Run the scripts to insert data.
#psql ${URI} -f sql/AppStoreClean.sql
#psql ${URI} -f sql/AppStoreSchema.sql
#psql ${URI} -f sql/AppStoreCustomers.sql
#psql ${URI} -f sql/AppStoreGames.sql
#psql ${URI} -f sql/AppStoreDownloads.sql

psql ${URI} -f sql/AppClean.sql
psql ${URI} -f sql/AirBnbSchema.sql
psql ${URI} -f sql/AppUsers.sql
psql ${URI} -f sql/AppHosts.sql
psql ${URI} -f sql/AppCountries.sql
psql ${URI} -f sql/AppCities.sql
psql ${URI} -f sql/AppPlaces.sql
psql ${URI} -f sql/Appbookings.sql
psql ${URI} -f sql/AppReviews.sql

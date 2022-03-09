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

URI="postgres://balnqengoxsrih:7911cef28045c976a1d63efe2aee90acb43fc1ae71e2231c7e43c251210f51d0@ec2-3-230-238-86.compute-1.amazonaws.com:5432/d45ku2l1gbjbia"

# Run the scripts to insert data.
psql ${URI} -f sql/AppStoreClean.sql
psql ${URI} -f sql/AppStoreSchema.sql
psql ${URI} -f sql/AppStoreCustomers.sql
psql ${URI} -f sql/AppStoreGames.sql
psql ${URI} -f sql/AppStoreDownloads.sql

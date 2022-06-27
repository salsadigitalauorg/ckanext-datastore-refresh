# ckanext-datastore-refresh 
:arrows_clockwise: :clock9:

This extension provides a option to refresh/reupload the datastore data when resource is uploaded by URL. Because there is no mechanism within CKAN core to track the changes in the files after the upload, we need to create cronjob that would call the CLI command to refresh data defined by the configuration panel as CKAN sysadmin.


## Requirements

Works with CKAN 2.9.x and above.

Depends on [ckanext-xloader](https://github.com/ckan/ckanext-xloader)

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9             | yes           |

Suggested values:

* "yes"
* "not tested" - I can't think of a reason why it wouldn't work
* "not yet" - there is an intention to get it working
* "no"


## Installation

To install ckanext-datastore-refresh:

1. Activate your CKAN virtual environment, for example:

     ```
     . /usr/lib/ckan/default/bin/activate
     ```

2. Clone the source and install it on the virtualenv

```
    git clone https://github.com/salsadigitalauorg/ckanext-datastore-refresh.git
    cd ckanext-datastore-refresh
    pip install -e .
	pip install -r requirements.txt
````
3. Add `datastore_refresh` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).
   ```
   ckan.plugins = datastore_config ...
   ````

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload
## Configuration

You will need to execute:

```
ckan db upgrade
```
to execute the database migration script

## CLI


There is CLI command to initialize the table:
```
ckan -c /path/to/ckan.ini datastore_config init_db
```
You can execute refresh datastore using the command `refresh_dataset_datastore` and passing the frequency interval in minutes as parameter. The frequency value must be defined in the `frequency_options.json` configuration file. This will reupload the data from resource to datastore
```
@hourly ckan -c /path/to/ckan.ini datastore_config refresh_dataset_datastore 10
```
10 - frequency  to refresh the datastore  (in minutes)
Cron jobs can be set by the desired frequency of updating. Configurable via frequency_options

Values defined in the `frequency_options` can be listed using the CLI command `available_choices`
```
ckan -c /path/to/ckan.ini datastore_config available_choices
```
## Frequency options

To customize frequency option, we can do it via the 
`frequency_options.json` file that could be set in the `ckan.ini` 

```
ckanext.datastore_refresh.frequency_options = your/frequency/options/path.json
```

Default frequency options is set as this example:
```
{"frequency_options": [
    {"value": "0", "text": "Select frequency"},
    {"value": "2", "text": "2 minutes"},
    {"value": "5", "text": "5 minutes"},
    {"value": "10", "text": "10 minutes"},
    {"value": "20", "text": "20 minutes"},
    {"value": "30", "text": "30 minutes"},
    {"value": "60", "text": "1 hour"},
    {"value": "120", "text": "2 hours"},
    {"value": "180", "text": "3 hours"},
    {"value": "240", "text": "4 hours"},
    {"value": "300", "text": "5 hours"},
    {"value": "360", "text": "6 hours"},
    {"value": "420", "text": "7 hours"},
    {"value": "480", "text": "8 hours"},
    {"value": "540", "text": "9 hours"},
    {"value": "600", "text": "10 hours"},
    {"value": "1440", "text": "Daily"}
]}
```
Values are defined in minutes

## API

There are API endpoints that could be used to interact with the datasets

`refresh_datastore_dataset_create`
----------------------------------
Creates the refreshing record in the database for selected dataset and frequency

`refresh_datastore_dataset_update`
----------------------------------
Updates selected record for the dataset

`refresh_dataset_datastore_list`
--------------------------------
Returns all records for refreshing

`refresh_dataset_datastore_by_frequency`
Returns all records by refreshing frequency

`refresh_dataset_datastore_delete`
----------------------------------
Deletes a refreshing record

`refresh_dataset_datastore_edit_frequency`
------------------------------------------
Edits a frequency for selected record

`refresh_dataset_datastore_show`
Shows refreshing record for the dataset



## Tests

To run the tests, do:
```
pytest --ckan-ini=test.ini ckanext/datastore_refresh/tests
```


## Releasing a new version of ckanext-datastore-refresh

If ckanext-datastore-refresh should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)

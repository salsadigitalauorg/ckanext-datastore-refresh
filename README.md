# ckanext-datastore-refresh 
:arrows_clockwise: :clock9:

This extension provides a option to refresh/reupload the datastore data when resource is uploaded by URL. Because there is no mechanism within CKAN core to track the changes in the files after the upload, we need to create cronjob that would call the CLI command to refresh data defined by the configuration panel as CKAN sysadmin.


## Requirements [TBD]

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

Also there is CLI command to initialize the table:
```
ckan -c /path/to/ckan.ini datastore_config init_db
```
Configuration is done by the CKAN admin menu

```
@hourly datastore_config -c /path/to/ckan.ini refresh_dataset_datastore 10
```
10 - frequency  to refresh the datastore  (in minutes)
Cron jobs can be set by the desired frequency which currently is set to 10 min, 2 hours or 24 hours

#TODO: Make frequencies configurable via ckan.ini file
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

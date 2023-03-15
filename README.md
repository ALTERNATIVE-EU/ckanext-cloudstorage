# ckanext-cloudstorage

CKAN extension that implements support for S3 Cloud Storage. This is a modified version of the <a href="https://github.com/TkTech/ckanext-cloudstorage" target="_blank">ckanext-cloudstorage</a> extension, which uses <a href="https://libcloud.apache.org/" target="_blank">libcloud</a>.

## Setup

1. Install <a href="https://docs.ckan.org/en/2.9/extensions/tutorial.html#installing-ckan" target="_blank">CKAN</a>

2. Clone the repository in the `src` dir (usually located in `/usr/lib/ckan/default/src`)
    ```
    cd /usr/lib/ckan/default/src
    git clone https://github.com/ALTERNATIVE-EU/ckanext-cloudstorage.git
    ```

3. Build the extension
    ```
    . /usr/lib/ckan/default/bin/activate
    cd /usr/lib/ckan/default/src/ckanext-cloudstorage
    sudo python3 setup.py develop
    ```

4. Update the ckan config file (usually `/etc/ckan/default/ckan.ini`)
    - Add the extension to your list of plugins
    ```
    ckan.plugins = stats text_view recline_view cloudstorage
    ```
    - Add settings for the driver that manages the connection to the Cloud; more details on how to set these can be found in [settings.py](ckanext/cloudstorage/settings.py)
    ```
    ckanext.cloudstorage.driver = S3
    ckanext.cloudstorage.container_name = example-bucket
    ckanext.cloudstorage.driver_options = {"key": "key", "secret": "secret"}
    ```

5. Start CKAN
   ```
   . /usr/lib/ckan/default/bin/activate
   sudo ckan -c /etc/ckan/default/ckan.ini run
   ```
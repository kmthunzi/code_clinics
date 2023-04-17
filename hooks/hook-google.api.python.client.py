from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('google-api-python-client')
datas += copy_metadata('google-api-core')
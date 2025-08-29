import importlib.resources as ir
import openwakeword.utils as oww_utils

# Download only if resources/models is missing
with ir.path('openwakeword', 'resources') as res_dir:
    if not res_dir.is_dir():
        oww_utils.download_models()  # downloads all pre-trained models into openwakeword/resources/models

Config File
***********

To make it easier for you to run the APIs as a stand-alone application
without having to define arguments again and again, we have created a
config file based on JSON structure that we parse.

Config File can be downloaded from `here`_

| Keep in mind the following things while creating your own config file:
| 1. ``exec`` will take a valid functionality name.Valid names can be
  checked
  `here <https://github.com/batra-mlp-lab/pcloudcv/wiki#functionalities>`__
| 2. ``path`` takes full path to the input folder where the images are
  present.
| 3. ``output`` takes full path to the output directory where the output
  will be saved.
| 4. For *Image Stitching* warp can take the following values.
| 5. For *VOCRelease5*, models take comma seperated values in the
  following format 

    * For Pascal categories: prefix the name with ``PAS_``, for example: ``PAS_aeroplane``
    
    * For ImageNet categories:prefix the name with ``ImNet_``
    * However if you want to run all the models, just mention ``all``.

.. _here: https://github.com/batra-mlp-lab/pcloudcv/blob/master/pcloudcv/config.json.example
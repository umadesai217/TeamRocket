
pokemoncarddetector - v2 2025-08-10 5:06pm
==============================

This dataset was exported via roboflow.com on August 11, 2025 at 12:09 AM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 841 images.
Card are annotated in YOLOv8 format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)

The following augmentation was applied to create 3 versions of each source image:
* Random Gaussian blur of between 0 and 2.5 pixels
* Salt and pepper noise was applied to 1.6 percent of pixels

The following transformations were applied to the bounding boxes of each image:
* Random rotation of between -15 and +15 degrees
* Random shear of between -10° to +10° horizontally and -10° to +10° vertically



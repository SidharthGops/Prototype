# Module: Catalog Generation Engine

## Purpose
Transforms a flat garment image into professional, studio-style catalog
images, including AI avatars wearing the garment.

## Owner
Member 2

## Inputs
- garment_image (ImageReference): photo of the garment
- style (str): desired catalog/studio style

## Outputs
- catalog_images (List[ImageReference]): generated catalog images

## Dependencies
- shared/schemas: ImageReference, JobRequest, JobResponse
- shared/interfaces: BaseModuleService
- shared/image_utils, shared/model_loader

## API
POST /catalog/generate
Request / Response: see `schemas/schemas.py`

## Future Improvements
- Add configurable avatar styles / backgrounds.

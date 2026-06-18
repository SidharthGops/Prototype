# Module: Virtual Try-On Engine

## Purpose
Generates a cinematic virtual try-on image from a person image, a garment
image, and a style prompt.

## Owner
Member 1

## Inputs
- person_image (ImageReference): photo of the person
- garment_image (ImageReference): photo of the garment
- prompt (str): style/scene guidance for the final image

## Outputs
- output_image (ImageReference): the generated cinematic try-on image

## Dependencies
- shared/schemas: ImageReference, JobRequest, JobResponse
- shared/interfaces: BaseModuleService
- shared/image_utils, shared/prompt_templates, shared/model_loader

## API
POST /vton/generate
Request / Response: see `schemas/schemas.py`

## Future Improvements
- Swap underlying try-on model (e.g. CatVTON -> IDM-VTON) without
  changing this README's API contract.

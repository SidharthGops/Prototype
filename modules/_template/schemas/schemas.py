"""
Define this module's specific request/response shapes here.
Extend the shared base types so the rest of the platform can treat
every module's job consistently (status, metadata, etc.).
"""

from shared.schemas.base_schemas import JobRequest, JobResponse


class TemplateRequest(JobRequest):
    # TODO: add this module's input fields, e.g.:
    # input_image: ImageReference
    # prompt: str
    pass


class TemplateResponse(JobResponse):
    # TODO: add this module's output fields, e.g.:
    # output_image: ImageReference
    pass

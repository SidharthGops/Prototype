# Frontend

Calls module APIs through the Core API Gateway only. No AI logic
(prompt construction, model calls, image generation) should live here —
keeping this true is what lets frontend and backend ship independently.

Suggested pages, one per module:
/mirror   -> vton
/catalog  -> catalog
/saree    -> saree (future)
/textile  -> textile (future)
/video    -> video (future)

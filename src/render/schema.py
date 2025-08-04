from pydantic import BaseModel

class RenderResponse(BaseModel):
    render_id: str
    output_path: str
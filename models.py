from pydantic import BaseModel

class UpdateCompanyInfoModel(BaseModel):
    updated_info: str

#### 1. Could not get S3FileLoader to work properly
    Work around:
    - Using .txt file 'TextLoader'

#### 2. Could not get Model with List[Upload] File to work properly
```
from typing import List
from fastapi import UploadFile, File

class EmailGenerationRequest(BaseModel):
    prospect_info: List[UploadFile]
    ...

```

- Work Around
    - Just explicilty declared:

    ```
    async def generate_email(
        prospect_file: List[UploadFile] = File(...),
        company_info: str = Form(...),
        company_name: str = Form(...),
        sales_rep: str = Form(...),
        prospect_name: str = Form(...)
        ):
    ```

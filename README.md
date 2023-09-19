# AI - Sales Marketing Email Generator
## Langchain and OpenAi API

## Next:
#### Currently not AWS integrated.

For AWS:
- Need to incorporate Mangum wrapper for FastApi
- Would be great if I could get S3FileLoader to work properly
- Would be able to store/ read info in S3 Bucket
    Current Work-around:
    - Upload company_info and prospect_info as .txt files 
    - Save tmp

    <br>
    For AWS - would need to create /tmp directory:

    ```
        prospect_info: List[UploadFile] = File(...),
        company_info: List[UploadFile] = File(...)

        # for AWS Lambda
        # would need to create a temporary file in /tmp directory

        for file in prospect_info:
            with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as temp_file:
                temp_file.write(await file.read())
                file_path = temp_file.name
                ...
    ```

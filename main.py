import os
from typing import List
from dotenv import load_dotenv
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from models import UpdateCompanyInfoModel
from langchain.document_loaders import TextLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Create a FastAPI instance
app = FastAPI()

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")

# Define file paths for company and prospect info
prospect_info_path = './example_data/prospect_info.txt'
company_info_path = './example_data/company_info.txt'
prospect_info_save = './example_data/prospect_save.txt'
company_info_save = './example_data/company_save.txt'


# Health check endpoint
@app.get('/')
async def health_check():
    return {"message": "health check status 200"}

# Get company_save.txt
@app.get('/company_save')
async def get_company_save():
    return FileResponse(company_info_save)

# Get company_info.txt
@app.get('/company_info')
async def get_company_info():
    return FileResponse(company_info_path)

# Update company_info.txt
@app.post('/company_info')
async def update_company_info(data: UpdateCompanyInfoModel):
    try:
        new_content = data.updated_info
        with open(company_info_path, 'w') as file:
            file.write(new_content)
        return {"message": "company_info.txt updated succesfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to update company_info.txt")

# Get prospect_save.txt
@app.get('/prospect_save')
async def get_prospect_save():
    return FileResponse(prospect_info_save)

# Get prospect_info.txt
@app.get('/prospect_info')
async def get_prospect_info():
    return FileResponse(prospect_info_path)

# Update prospect_info.txt
@app.post('/prospect_info')
async def update_prospect_info(data: UpdateCompanyInfoModel):
    try:
        new_content = data.updated_info
        with open(prospect_info_path, 'w') as file:
            file.write(new_content)
        return {"message": "prospect_info.txt updated succesfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to update prospect_info.txt")


# Helper function to chunk a document
def chunk_document(data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0
    )
    return text_splitter.split_documents(data)


# Map prompt used during initial processing of split documents
map_prompt = """ 
    % MAP PROMPT

    Below is a section of a website about {prospect}

    Write a concise summary about {prospect}. If the information is not about {prospect}, exclude it from your summary.

    {text} 
    """

# Combine prompt used when combining outputs of the map pass
combine_prompt = """
    % COMBINE PROMPT
    
    Your goal is to write a personalized outbound email from {sales_rep}, a sales rep at {company} to {prospect}.
    
    A good email is personalized and combines information about the two companies on how they can help each other.
    Be sure to use value selling: A sales methodology that focuses on how your product or service will provide value to the customer instead of focusing on price or solution.

    % INFORMATION ABOUT {company}:
    {company_information}

    % INFORMATION ABOUT {prospect}:
    {text}
    
    % INCLUDE THE FOLLOWING PIECES IN YOUR RESPONSE:
        - Start the email with the sentence: "We love that {prospect} helps teams..." then insert what they help teams do.
        - The sentence: "We can help you do XYZ by ABC" Replace XYZ with what {prospect} does and ABC with what {company} does 
        - A 1-2 sentence description about {company}, be brief
        - End your email with a call-to-action such as asking them to set up time to talk more 
    """

# Generate email endpoint
@app.post('/generate_email')
async def generate_email(
    prospect_file: List[UploadFile] = File(...),
    company_info: str = Form(...),
    company_name: str = Form(...),
    sales_rep: str = Form(...),
    prospect_name: str = Form(...)
    ):
    try:
        data = []
        # Load prospect_file.txt
        for file in prospect_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await file.read())
                file_path = temp_file.name
                loader = TextLoader(file_path)
                data = loader.load()           
                print(data)
        
        # Split the document into chunks
        docs =  chunk_document(data)

        # Map_prompt: This prompt is used during initial processing of individual split documents.
        map_prompt_template = PromptTemplate(
            template=map_prompt,
            input_variables=["text", "prospect"])

        # Combine_prompt: This prompt is used when combining the outputs of the map pass.
        combine_prompt_template = PromptTemplate(
            template=combine_prompt,
            input_variables=["company", "company_information", "sales_rep", "prospect", "text"])

        # Initialize OpenAI language model
        llm = OpenAI(temperature=.5)

        # Define a text generation chain
        # Even though we're not summarizing, we use the load_summarize_chain for efficient map-reduce processing.
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt_template,
            combine_prompt=combine_prompt_template,
            verbose=False
        )

        # Generate text based on provided documents and prompts
        output = chain({
            "input_documents": docs,
            "company": company_name,
            "company_information": company_info,
            "sales_rep": sales_rep,
            "prospect": prospect_name
        })

        # Print the generated output
        return {"output_text": output['output_text']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
    # prospect_info: List[UploadFile] = File(...),
    # company_info: List[UploadFile] = File(...)):

    for AWS Lambda
    for file in prospect_info:
        # Create a temporary file in /tmp directory
        with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as temp_file:
            temp_file.write(await file.read())
            file_path = temp_file.name
        ...
        # Clean up the temporary file
        os.remove(file_path)
"""

import azure.functions as func
from markitdown import MarkItDown, FileConversionException, UnsupportedFormatException
from openai import AzureOpenAI
import os
import logging
import tempfile

default_supported_extensions = (
    '.pptx', '.docx', '.xlsx', '.pdf', '.csv', '.zip', '.html', '.htm'
    ".xml", ".rss", ".atom",'.ipynb', # not working
)
llm_supported_image_extensions = ('.jpg', '.jpeg', '.png')

use_llm = True if os.environ.get('markitdown_azureopenai_key') else False
if use_llm:
    # create an instance of the AzureOpenAI class
    client = AzureOpenAI(
        azure_endpoint=os.environ.get('markitdown_azureopenai_endpoint'),
        api_key=os.environ.get('markitdown_azureopenai_key'),
        api_version=os.environ.get('markitdown_azureopenai_apiversion'),
    )
    md = MarkItDown(llm_client=client, llm_model="gpt-4o")
    supported_extensions = default_supported_extensions + llm_supported_image_extensions
else:
    md = MarkItDown()
    supported_extensions = default_supported_extensions

app = func.FunctionApp()
@app.blob_trigger(
    arg_name="input", path="input/{blobname}", connection="markitdown_blobstorage"
)
@app.blob_output(arg_name="outputblob", path="output/{blobname}.md", connection="markitdown_blobstorage")
def blob_trigger(input: func.InputStream, outputblob: func.Out[str]):

    # input.name will be "input/{blobname}" e.g. "input/test.docx"
    blobname = input.name.split("/")[-1]

    logging.info(f"New blob provided: {blobname}")
    if not blobname.endswith(supported_extensions):
        logging.info(f"Unsupported file type: {blobname}")
        return
    with tempfile.NamedTemporaryFile(suffix=blobname, delete=True) as temp_file:
        temp_file.write(input.read())
        temp_file.flush()
        try:
            result = md.convert(temp_file.name)
        except FileConversionException as fce:
            logging.error(f"Error converting {blobname}: {fce}")
            return
        except UnsupportedFormatException as ufe:
            logging.error(f"Error converting {blobname}: {ufe}")
            return
        except Exception as e:
            logging.error(f"Error converting {blobname}: {e}")
            return
        outputblob.set(result.text_content)
        logging.info(f"Successfully converted {blobname} to markdown")
        # logging.info(f"Output: {result.text_content}")

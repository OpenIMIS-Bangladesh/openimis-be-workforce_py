import os
from pathlib import Path
import mimetypes
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
import uuid
from django.urls import reverse


def save_uploaded_file(file, name):
    if not name:
        return None, None, {'error': 'Name is required'}
    if not file:
        return None, None, {'error': 'File is required'}
    try:
        generated_file_name = uuid.uuid4().hex + Path(file.name).suffix
        file_path = os.path.join('content', 'workforce', generated_file_name)
        file_name = default_storage.save(file_path, file)
        file_path = default_storage.url(file_name)
        file_url = reverse(
            'document-view', kwargs={'filename': generated_file_name})
        
        # TODO - add document table insertion logic here

        return file_url, file_path, None
    except Exception as e:
        return None, None, {'error': str(e)}


def retrieve_file_response(filename):
    try:
        file_path = os.path.join('content', 'workforce', filename)
        if not default_storage.exists(file_path):
            raise Http404("File does not exist")
        file = default_storage.open(file_path)
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        response = FileResponse(file, content_type=mime_type)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except Exception as e:
        raise Http404(f"Error retrieving file: {str(e)}")

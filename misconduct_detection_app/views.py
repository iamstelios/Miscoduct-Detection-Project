import shutil

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, MemoryFileUploadHandler, TemporaryFileUploadHandler
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import os


# Create your views here.
# ------------------------------------Custom File Handler------------------------------------


class CustomInMemoryUploadedFile(InMemoryUploadedFile):
    def __init__(self, file, field_name, name, content_type, size, charset, content_type_extra=None):
        super().__init__(file, field_name, name, content_type, size, charset, content_type_extra)
        self.original_path = name[:name.rfind('/')] + "/"


class CustomMemoryFileUploadHandler(MemoryFileUploadHandler):
    def file_complete(self, file_size):
        """Return a file object if this handler is activated."""
        if not self.activated:
            return

        self.file.seek(0)
        return CustomInMemoryUploadedFile(
            file=self.file,
            field_name=self.field_name,
            name=self.file_name,
            content_type=self.content_type,
            size=file_size,
            charset=self.charset,
            content_type_extra=self.content_type_extra
        )


class CustomTemporaryUploadedFile(TemporaryUploadedFile):
    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        super().__init__(name, content_type, size, charset, content_type_extra)
        self.original_path = name[:name.rfind('/')] + "/"


class CustomTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = CustomTemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset,
                                                self.content_type_extra)


# ------------------------------------Index------------------------------------


def index(request):
    """The index page
    
    :param request: request
    :type request: HttpRequest
    :return: render
    :rtype: render
    """

    return render(request, 'misconduct_detection_app/welcome.html')


def upload_index(request):
    return render(request, 'misconduct_detection_app/upload.html')


def examine_index(request):
    path_file = "misconduct_detection_app/uploads/singlefiles/"
    path_folder = "misconduct_detection_app/uploads/folders/"
    local_files = os.listdir(path_file)
    local_folders = os.listdir(path_folder)
    context = {
        'local_files': local_files,
        'local_folders': local_folders,
    }
    return render(request, 'misconduct_detection_app/examine.html', context)


def select_index(request):
    path_file = "misconduct_detection_app/uploads/singlefiles/"
    local_files = os.listdir(path_file)

    f = open(path_file + local_files[0], 'r')
    file_content = f.read()
    f.close()
    context = {
        "file_content": file_content,
    }

    return render(request, 'misconduct_detection_app/select.html', context)


def results_index(request):
    return render(request, 'misconduct_detection_app/results.html')


# ------------------------------------Uploading single file------------------------------------

def upload_file(request):
    """Single file upload function

    Accept a single file from uploading and store it.
    
    :param request: request
    :type request: HttpRequest
    :return: HttpResponse
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        handle_upload_file(request.FILES['file'], str(request.FILES['file']))
        return HttpResponse('Uploading Success')
    else:
        return HttpResponse('Uploading Failed')


def handle_upload_file(file, filename):
    """Store the file from memory to disk
    
    :param file: the file to store
    :type file: HttpRequest.FILES
    :param filename: the file name of the file
    :type filename: str
    """

    path = 'misconduct_detection_app/uploads/singlefiles/'
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + filename, 'wb+')as destination:
        for chunk in file.chunks():
            destination.write(chunk)


# ------------------------------------Uploading folder------------------------------------


def upload_folder(request):
    """Folder upload function

    Accept a whole folder uploading and store the files into disk
    
    :param request: request
    :type request: HttpRequest
    :return: HttpResponse
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        files = request.FILES.getlist('file')
        for f in files:
            file_name, file_extension = os.path.splitext(str(f))
            original_path = f.original_path
            # if file_extension == '.c':
            handle_upload_folder(f, file_name, file_extension, original_path)
        return HttpResponse('Upload Success')
    else:
        return HttpResponse('Uploading Failed')


"""
TODO: merge these two file handler function.
"""


def handle_upload_folder(file, file_name, file_extension, original_path):
    """handle the folder uploading and store the files to disk
    
    :param file: one file 
    :type file: HttpRequest.FILES
    :param file_name: the name of the file
    :type file_name: str
    :param file_extension: the extension of the file
    :type file_extension: str
    """

    path = 'misconduct_detection_app/uploads/folders/' + original_path
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + file_name + file_extension, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


# ------------------------------------Examination Page------------------------------------


def examine_file(request, name):
    path_file = "misconduct_detection_app/uploads/singlefiles/"
    f = open(path_file + name, 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type="text/plain")


def examine_folder(request, name):
    path_folder = "misconduct_detection_app/uploads/folders/" + name
    local_folders = os.listdir(path_folder)
    return render(request, 'misconduct_detection_app/examine.html', {"local_folders": local_folders})

def examine_folder_files(request, name):
    path_file = "misconduct_detection_app/uploads/folders/"
    f = open(path_file + name, 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type="text/plain")


# ------------------------------------Select Code------------------------------------


def select_code(request):
    path = "misconduct_detection_app/uploads/temp/"

    if request.method == 'POST':
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + 'target' + '.c', 'w+') as f:
            f.write(request.POST['inputCode'])
        return HttpResponse('Selection Succeeded')
    else:
        return HttpResponse('Selection Failed') 


# ------------------------------------Run the Jplag jar------------------------------------


def run_jar(request):
    """Run the .jar type detection plugin

    TODO: NOT FINISHED YET!!
    
    :param request: request
    :type request: HttpRequest
    :return: HttpResponse
    :rtype: HttpResponse
    """

    detection_plugin_path = "%cd%\\detetion_libs\\jplag-2.11.9-SNAPSHOT-jar-with-dependencies.jar"
    results_path = "%cd%\\results\\"
    upload_file_path = "%cd%\\uploads\\folders"
    os.system("java -jar {0} -m 999 -l c/c++ -r {1} {2}".format(detection_plugin_path, results_path, upload_file_path))
    return HttpResponse("Running Finished")


def run_detection(request):
    return render(request, 'misconduct_detection_app/running.html')


def run_detection_core(request):
    path_folder = "misconduct_detection_app/uploads/folders/"
    des_folder = "misconduct_detection_app/uploads/temp/"
    local_folders = os.listdir(path_folder)
    # Temp used for debuging
    # local_folders = os.listdir(path_folder + local_folders[0])
    for file_name in local_folders:
        if not os.path.exists(des_folder + file_name):
            shutil.copytree(path_folder + file_name, des_folder + file_name)

    detection_plugin_path = "%cd%\\misconduct_detection_app\\detection_libs\\jplag-2.11.9-SNAPSHOT-jar-with-dependencies.jar"
    results_path = "%cd%\\misconduct_detection_app\\results\\"
    upload_file_path = "%cd%\\misconduct_detection_app\\uploads\\temp"
    os.system("java -jar {0} -m 999 -l c/c++ -s -r {1} {2}".format(detection_plugin_path, results_path, upload_file_path))

    path_res = "misconduct_detection_app/results/"
    file_content = os.listdir(path_res)

    context = {
        'file_content': file_content
    }

    return render(request, 'misconduct_detection_app/results.html', context)
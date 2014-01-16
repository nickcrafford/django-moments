import os, datetime

from random                   import randint
from django.shortcuts         import render_to_response
from django.template          import RequestContext
from django.http              import HttpResponseRedirect
from django.core.files        import File
from moments                  import settings
from moments.apps.base.models import Moment
from moments.apps.base.forms  import UploadZipFileForm
from django.forms.util        import ErrorList

# Custom Exceptions

class InvalidFileType(Exception):
	pass

# Filesystem Ops
def unzip(file_path, dest):
	os.system("unzip " + file_path + " -d " + dest)

def remove_dir(path):
	os.system("rm -rf " + path)

def save_file(t_file, dest_path):
	with open(dest_path, 'wb+') as destination:
		for chunk in t_file.chunks():
			destination.write(chunk)

def mkdir(path):
	os.makedirs(path)

# Util
def rand_str():
	return str(randint(1,99999))

def get_random_prefix():
	return rand_str() + "_" + rand_str()

def is_valid_filename(fname):
	for ext in settings.VALID_IMAGE_EXTS:
		if str(fname).find(ext) >= 0:
			return True
	return False

def get_valid_image_list(path):
	images = []
	for fn in os.listdir(path):
		if os.path.isfile(path + "/" + fn):
			if is_valid_filename(fn):
				images.append(str(fn))
	images.sort()
	return images

# Upload
def handle_uploaded_file(request, file_handle):
	""" Handle an uploaded zip file of images. """

	if not request.FILES['file'].name.upper().endswith('.ZIP'):
		raise InvalidFileType()

	tmp_path      = settings.TMP_PATH + get_random_prefix()
	tmp_file_path = tmp_path + "/" + get_random_prefix() + ".zip"

	# Make the temp directory
	mkdir(tmp_path)

	# Save zip file to the temp path
	save_file(file_handle, tmp_file_path)

	# Unzip zip file
	unzip(tmp_file_path, tmp_path)

	# Get list of valid image file names (Note: no path)
	valid_images = get_valid_image_list(tmp_path)

	# Save images as moments
	for image in valid_images:
		moment              = Moment()
		moment.published    = False
		moment.photographer = request.user
		moment.create_user  = request.user
		moment.update_user  = request.user
		moment.caption      = ""

		moment.image.save(rand_str() + "_" + image, File(open(tmp_path + "/" + image)))
		moment.save()

	# Remove directory of temp images, zip, etc.
	remove_dir(tmp_path)

# Admin View

def admin_batch_load_view(request, model_admin):
	""" Custom admin view for uploading a zip file of images. """
	opts       = model_admin.model._meta
	admin_site = model_admin.admin_site
	has_perm   = request.user.has_perm(opts.app_label + "." + opts.get_change_permission())

	if request.method == 'POST':
		form = UploadZipFileForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				handle_uploaded_file(request, request.FILES['file'])
				return HttpResponseRedirect('/admin/base/moment/?published__exact=0')
			except InvalidFileType, ex:
				errors = form._errors.setdefault("file", ErrorList())
				errors.append(u'File could not be uploaded. Please make sure the file is a valid .zip archive.')
	else:
		form = UploadZipFileForm()

	context = {
		'admin_site'            : admin_site.name,
		'title'                 : 'Upload Zip',
		'opts'                  : opts,
		'root_path'             : '/admin/',
		'app_label'             : 'base',
		'has_change_permission' : has_perm,
		'form'                  : form
	}			

	return render_to_response('admin/moments/batch_load_view.html', context, context_instance=RequestContext(request))

# Frontend View

def single_page_view(request):
	return render_to_response('single_page.html', {}, context_instance=RequestContext(request))	
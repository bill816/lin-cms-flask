"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask import request
from lin.jwt import login_required
from lin.redprint import Redprint
from flask import current_app
from app.extension.file.local_uploader import LocalUploader
import os



_d,_f=os.path.split(os.path.realpath(__file__))

ROOT_PATH ='../../'+ _d + '/sign_assert/'

# TODO 判断处理路径问题
UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/

#print ('downloads/%s/apk_sign/') % ('n5s')
COPY_APK_SIGN_PATH = ROOT_PATH + 'downloads/%sapk_sign/'
COPY_OTA_SIGN_PATH = ROOT_PATH + 'downloads/%sota_sign/'
COPY_DOWN_UPGRADE_PATH = ROOT_PATH + 'downloads/%s/down_upgrade/'
COPY_SPLASH_PATH = ROOT_PATH + 'downloads/splash/'


##############################function###########################
def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.18.8.152', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def get_current_time():
    return time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))

def is_windows_system():
    return 'Windows' in platform.system()

def delete_file_platform(file_name):
    if is_windows_system():
        os.system('rd /s /q ' + file_name)
        os.system('del /q /s ' + file_name)
    else:
        os.system('rm -rf ' + file_name)

def delete_line(file_path):
    #sed -i '/less_than_int.*/d' updater-script
    os.system( 'sed -i '  + '\'/less_than_int.*/d \' ' + file_path)

def zip_file_platform(zip_fold):
    if is_windows_system():
        os.system('..\zip -ry ..\\' + zip_fold + ".zip" + " .")
    else:
        out_put = os.system('zip -ry ../' + zip_fold + ".zip" + " .")

def unpack(zip_path):
    time_str = get_current_time()
    unzip_fold = 'update_' + time_str 
    output = os.system('unzip ' +  zip_path + ' -d ' + unzip_fold)
    print("unpack successed!")
    return unzip_fold


def pack(zip_fold):
    os.chdir(zip_fold)
    zip_file_platform(zip_fold)
    os.chdir("..")
    print ("sign the update pls wait...")
    zip_file_name = zip_fold + '.zip'
    srv_cp_name =  COPY_DOWN_UPGRADE_PATH + zip_fold + '_signed.zip'
    output = os.system('java -Xmx2048m -jar signapk.jar -w releasekey.x509.pem releasekey.pk8 ' + zip_file_name + ' ' +  srv_cp_name )

    #删除解压文件
    delete_file_platform(zip_fold)
    delete_file_platform(zip_fold + '.zip')
    print ("pack and signed successed!")

    return srv_cp_name

def my_makedirs(dir_path):
   if not os.path.exists(dir_path): 
        os.makedirs(dir_path)


def sign_apk(apk_path,dev_type):
    apk_cp_dir = (COPY_APK_SIGN_PATH) % (dev_type)

    os_type = 7 #android7.1
    if "n5" in dev_type or "n3" in dev_type:
        os_type = 5 #android5.1

    my_makedirs(apk_cp_dir)
    apk_cp_name = apk_cp_dir + apk_path[apk_path.rfind('/'):apk_path.rfind('.')] + '_'+ get_current_time() + "_signed.apk"
    dev_type = ROOT_PATH + dev_type
    print ("start sign apk to platform:" + apk_cp_name )
    cmd = ("java -jar %ssignapk.jar -w %splatform.x509.pem  %splatform.pk8 " + apk_path + " " + apk_cp_name) % (dev_type,dev_type,dev_type)
    #cmd = "java -jar " + dev_type + "signapk.jar " +  dev_type + "platform.x509.pem "  +  dev_type + "platform.pk8 " + apk_path + " " + apk_cp_name
    print(cmd)
    os.system(cmd)
    print ("sign apk finished:" + apk_cp_name)
    return apk_cp_name


def sign_ota(ota_path,dev_type):
    
    ota_cp_dir = (COPY_OTA_SIGN_PATH) % (dev_type)    #"./" + dev_type +  COPY_APK_SIGN_PATH 

    os_type = 7 #android7.1
    if "n5" in dev_type or "n3" in dev_type:
        os_type = 5 #android5.1

    my_makedirs(ota_cp_dir)
    cp_ota_path = ota_cp_dir + ota_path[ota_path.rfind('/'):ota_path.rfind('.')] + '_' + get_current_time() + '_signed.zip'
    dev_type = ROOT_PATH + dev_type


    cmd = ('/usr/lib/jvm/java-8-openjdk-amd64/bin/java  -Xmx2048m -Djava.library.path=%slib64 -jar %ssignapk.jar -w %sreleasekey.x509.pem %sreleasekey.pk8 ' \
            +  ota_path + ' ' + cp_ota_path) % (dev_type,dev_type,dev_type,dev_type)

    if os_type == 5:
        cmd = ('java -Xmx2048m -jar %ssignapk.jar -w  %sreleasekey.x509.pem  %sreleasekey.pk8 ' +  ota_path + ' ' + cp_ota_path) % (dev_type,dev_type,dev_type)

    output = os.system(cmd)
    return cp_ota_path
##############################functions##############################




##############################route functions##############################

def do_ota_sign(file_name,desc):
    file_path =  app.config['UPLOAD_FOLDER'] + desc + file_name
    print ('start do_zip_sign:' + file_path)
    return sign_ota(file_path,desc)

def do_down_update(file_name,desc):
    file_path =  app.config['UPLOAD_FOLDER'] + file_name
    zip_fold = unpack(file_path)

    print (zip_fold)

    #删除时间戳判断
    delete_line(zip_fold + '/META-INF/com/google/android/updater-script')

    ret_str = pack(zip_fold)

    return ret_str


def do_apk_sign(file_name,desc):
    file_path =  app.config['UPLOAD_FOLDER'] + desc + file_name
    print ('start do_apk_sign:' + file_path)
    return sign_apk(file_path,desc)

def do_tms_ota(file_name,desc):
    print ('start do_apk_sign')
    return None
##############################route functions##############################





def do_logo_gen(file_name,desc):

	file_path =  app.config['UPLOAD_FOLDER'] + desc + file_name
	des_path = COPY_SPLASH_PATH + "splash_" + get_current_time() + ".img"
	my_makedirs(COPY_SPLASH_PATH)
	print (file_path)
	MakeLogoImage(file_path, des_path)
	return des_path


operator_map = {'cmd_ota_sign':do_ota_sign,'cmd_down_upgrade':do_down_update,'cmd_apk_sign':do_apk_sign,'cmd_ota_tms':do_tms_ota,'cmd_logo_gen':do_logo_gen} 
def route_function(func_str,file_name,desc):
    #运行处理函数
    return operator_map.get(func_str)(file_name,desc)



sign_file_api = Redprint("sign_file")

@sign_file_api.route("", methods=["POST"])
@login_required
def post_file():
    print('---------------------------')
    files = request.files
    op_type = request.form['op_type']
    option = request.form['option']

    print ('upload_file device type:' + op_type + " operate:" + option)

    print("1. cms/file post file function")
    uploader = LocalUploader(files)
    ret = uploader.upload()
    print("2. cms file end post file function:" + str(ret))
    result_path = route_function(option,ret[0]['path'],op_type)
    return ret

#-*- coding:utf-8 -*-

import os
import time
import sys
import platform
import socket
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'

SRV_PATH = '/srv/public/updload_reulst_n3/'
COPY_APK_SIGN_PATH = SRV_PATH + 'apk_sign/'
COPY_OTA_SIGN_PATH = SRV_PATH + 'ota_sign/'
COPY_OTA_XTMS_PATH = SRV_PATH + 'ota_xtms/'
COPY_DOWN_UPGRADE_PATH = SRV_PATH + 'down_upgrade/'


ALLOwED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip','apk'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

support_version = '0'
after_version = '0'

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
    print "unpack successed!"
    return unzip_fold



def pack(zip_fold):
    os.chdir(zip_fold)
    zip_file_platform(zip_fold)
    os.chdir("..")
    print "sign the update pls wait..."
    zip_file_name = zip_fold + '.zip'
    srv_cp_name =  COPY_DOWN_UPGRADE_PATH + zip_fold + '_signed.zip'
    output = os.system('java -Xmx2048m -jar signapk.jar -w releasekey.x509.pem releasekey.pk8 ' + zip_file_name + ' ' +  srv_cp_name )

    #删除解压文件
    delete_file_platform(zip_fold)
    delete_file_platform(zip_fold + '.zip')
    print "pack and signed successed!"

    return srv_cp_name


def sign_apk(apk_path):
    apk_cp_name = COPY_APK_SIGN_PATH + apk_path[apk_path.rfind('/'):apk_path.rfind('.')] + ".sign.apk"
    print "start sign apk to platform:" + apk_cp_name 
    os.system("java -jar signapk.jar platform.x509.pem platform.pk8 " + apk_path + " " + apk_cp_name)
    print "sign apk finished:" + apk_path[:apk_path.rfind('.')] + ".sign.apk"

    return apk_cp_name


def sign_ota(ota_path):
    cp_ota_path =  COPY_OTA_SIGN_PATH + 'update_new_sign_' + get_current_time() + '.zip'
    output = os.system('java -Xmx2048m -jar signapk.jar -w releasekey.x509.pem releasekey.pk8 ' +  ota_path + ' ' + cp_ota_path)
    return cp_ota_path

def pack_tms(ota_path,desc):
    '''生成的文件名如下示例所示:INC 增量包  FULL 全量包'''
    '''写一半发现意义不太大，废弃吧'''
    #TMS_n3_v1.4.0_20170809_FULL.zip
    #TMS_n3_v1.3.2_N5000001_to_v1.3.2_N5000002_INC.zip
    tms_type = '_INC.zip'
    if support_version == '0':
        tms_type = '_FULL.zip'
        support_version = ''
    else:
        support_version = support_version + '_to_'

    cp_xtms_path = COPY_OTA_XTMS_PATH + 'TMS_n3_' + support_version + after_version + tms_type 

    

def allowed_file(filename):
    """
    checks if a file is abled to be uploaded based on filename extension
    """

    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOwED_EXTENSIONS


def md5sum(filename):             
    import hashlib                    
    fd = open(filename,"r")  
    fcont = fd.r  
    fd.close()           
    fmd5 = hashlib.md5(fcont)  
    return fmd5  


##############################route functions##############################

def do_ota_sign(file_name,desc):
    print 'start do_zip_sign' 
    file_path =  app.config['UPLOAD_FOLDER'] + file_name
    return sign_ota(file_path)

def do_down_update(file_name,desc):
    print 'start do_down_update file:' + file_name 
    print 'start do_down_update desc:' + desc 
    file_path =  app.config['UPLOAD_FOLDER'] + file_name
    zip_fold = unpack(file_path)

    print zip_fold

    #删除时间戳判断
    delete_line(zip_fold + '/META-INF/com/google/android/updater-script')

    ret_str = pack(zip_fold)

    return ret_str


def do_apk_sign(file_name,desc):
    file_path =  app.config['UPLOAD_FOLDER'] + file_name
    return sign_apk(file_path)

def do_tms_ota(file_name,desc):
    print 'start do_apk_sign' 
    return None


operator_map = {'cmd_ota_sign':do_ota_sign,'cmd_down_upgrade':do_down_update,'cmd_apk_sign':do_apk_sign,'cmd_ota_tms':do_tms_ota} 
def route_function(func_str,file_name,desc):
    #运行处理函数
    return operator_map.get(func_str)(file_name,desc)    



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        option = request.form['option']
        #text = request.form['lname']
        text = 'text'
        global support_version
        global after_version
        #support_version = request.form['sname']
        #after_version   = request.form['aname']
        #print 'text:',text
        #print 'ischecked:',option
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = filename + '_' + get_current_time()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            result_path = route_function(option,filename,text)
            return redirect(url_for('uploaded_file',
                                    filename=option[4:] + '\\' + result_path[result_path.rfind('/') + 1:]))

    return '''
	<!doctype html>
	<title>老司机们的工具N3版</title>
	<h1>老司机们的工具N3版</h1>
	<form action="" method=post enctype=multipart/form-data>

    <input type="radio" checked='true' name="option" value="cmd_apk_sign" >APK签名 </input>
    <input type="radio" name="option" value="cmd_down_upgrade" > ota降级 </input>
    <input type="radio" name="option" value="cmd_ota_sign" > ota签名 </input>
    <input type="radio" name="option" value="cmd_ota_tms" > ota生成TMS包 </input>

    <p><input type=file name=file>
    <input type=submit value=Upload>


    <!--
    <br/>
    <br/>
    <br/>
    <h1> ----------XTMS------------ <h1>
    <h3> supportVersion: </h1>
    <textarea rows="1" style="margin: 0px; height: 29px; width: 316px;" name="sname">
     请输入升级前版本,全量升级可填0
    </textarea>

    <h3> afterVersion: </h1>
    <textarea rows="1" style="margin: 0px; height: 29px; width: 316px;" name="aname">
    请输入升级后版本
    </textarea>



    <h3> description: </h1>
    <textarea rows="10" style="height: 150px; margin: 0px; width: 380px;" cols="30" name="lname">
    input description
    </textarea>
    -->

	</form>
	'''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    samba_path = '\\\\' + get_host_ip() +'\public\updload_reulst_n3\\' + filename
    return 'do successed get file:' + samba_path 
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5001)

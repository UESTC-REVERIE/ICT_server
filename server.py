# 基于Flask框架
from multiprocessing import Process
import os,json
import platform
from flask import Flask, render_template, request,send_file,Response,render_template_string
from flask.wrappers import Response
from PIL import Image
PORT = 8888
if os.path.exists('./static/profile.json'):
    print('读取配置文件')
    profile = open('./static/profile.json','r')
    content = profile.read()
    data = json.loads(content)
    PORT = data['server_port']
app = Flask(__name__)

IMAGE_PATH = './images_for_train/'
HISTORY_IMAGE_PATH = './images_for_history/'
VIDEO_PATH = './videos/'
LOADING_VIDEO_PATH = './videos/loading.mp4'
OBJECT_PATH = './models/'
app.template_folder = './'
subProcess = None
imageCounterDirt = {}

# 开启子进程，创建新的训练任务
@app.route("/newTask/<string:name>", methods=['GET'])
def start_new_task(name):
    global subProcess

    if subProcess is not None:
        subProcess.terminate()
        print('killed subProcess')
    # print('creating new task')
    # 在客户端开始上传的时候开启子进程
    # if subProcess is None or not subProcess.is_alive():
    # if name not in imageCounterDirt:
        
    # imageCounterDirt[name] = request.form.get('totalImages')
    print('start subProcess')
    subProcess = Process(target=execute_main,args=(name,))
    subProcess.daemon = True
    subProcess.start()
    return 'create success'
# 接受图片并保存
@app.route("/upload/<string:name>", methods=['POST'])
def recv_images_and_work(name):
    
    # 为每次上传组插入一条新记录
    with open('./history.json', 'rb') as f:
        json_data = json.load(f)
        #创建新内容
        new_data = {
            'alias':request.form.get("alias"),
            'date':request.form.get('date'),
            'totalImages':request.form.get('totalImages')
        }
        #插入新项
        json_data[name] = new_data
        print(f'insert new history: ${name} ${new_data}')
    # 写入文件保存
    with open('./history.json', 'w') as f:
        json.dump(json_data, f) 
        
    # imageCounterDirt[name] -= 1
    # if imageCounterDirt[name] == 0:imageCounterDirt.pop(name)
    print('recv a new image')
    upload_file = request.files['file']
    #创建目录
    image_sub_dir = IMAGE_PATH + name + '/'
    if not os.path.exists(image_sub_dir):
        os.makedirs(image_sub_dir)
    
    images = os.listdir(image_sub_dir)
    index = len(images)
    if upload_file:
        file_paths = image_sub_dir + str(index) + '.jpg'
        print('save in: ' + file_paths)
        upload_file.save(file_paths)
        return '上传成功'


def execute_main(name):
    print('execute: ' + name)
    os.system('python ./main.py ' + name)
@app.route("/history/icon/<string:name>")
def get_history_icon(name):
    # if os.path.exists(HISTORY_IMAGE_PATH + name + '.png'):
    return send_file(HISTORY_IMAGE_PATH + name + '.jpg')
         
@app.route("/history/list")
def get_history_list():
    print('get_history_list')
    json2string = ''
    with open('./history.json','rb') as f:
        jsonData = json.load(f)
        json2string = jsonData
    print(json2string)
    return json2string
# @app.route('/check/model',methods=['GET'])
# def check_model():
#     if os.path.exists(VIDEO_PATH):
#         print(True)
#         return 'True'
#     print(False)
#     return 'False'

# 测试代码
@app.route("/")
def hello_world():
    return "Hello, World!"
# web页面：预览obj模型或加载LoFTR图片预览界面
@app.route("/preview/<string:name>")
def preview(name):
    html_path = 'html/preview_loader.html'
    if name == 'images':
        html_path = 'html/recv_images.html'
    return render_template(html_path,name=name)
    # return render_template('html/preview.html')
# 下载obj模型
@app.route('/download/object/<string:name>',methods=['GET'])
def download_object(name):
    return send_file(OBJECT_PATH+name)

# 加载等待视频
@app.route('/download/loading')
def loading():
    return send_file(LOADING_VIDEO_PATH)

# 下载渲染视频
@app.route('/download/video/<string:name>')
def download_model(name):
    print('Downloading Video')
    return send_file(VIDEO_PATH+name+'.mp4')

# @app.route('/updatePreview',methods=['POST'])
# def update_preview():
#     args = request.json.get('width')+' '+request.json.get('height')
#     args += ' '+request.json.get('posx')+' '+request.json.get('posy')+' '+request.json.get('posz')
#     args += ' '+request.json.get('targetx')+' '+request.json.get('targety')+' '+request.json.get('targetz')
#     command = 'preview '+args
    
#     print(command)
#     result = 'updating'
#     # if imageVerify('./static/img/preview.png'):
#     result = os.system(command)
#     print(result)
#     return str(result)
# def imageVerify(imgPath):
#     if not os.path.exists(imgPath): return False
#     try:
#         img = Image.open(imgPath)
#         img.verify()
#         return True
#     except:
#         return False
# TODO 多用户同时使用测试
if __name__ == "__main__":
    print("--------")
    app.run(host='0.0.0.0', port=8888, debug = Flask)
    #os.system('python server_renderer_mesh.py')



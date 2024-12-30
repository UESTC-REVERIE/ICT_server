# @auther: Reverie，Siner
# @date:2024/3/24        
# @note:
# 服务端主要逻辑的实现，
# 使用多线程确保维护websocket的同时不影响主线程Ai推理逻辑进行，
# 正常情况下该进程应由server进程在接收到第一张图片时开启，
# 进程开始维护websocket，等待图片传输完毕websocket建立连接时开始主线程Ai逻辑
import asyncio
import platform
import time,json,subprocess
import websockets
import sys,os,base64,threading,signal
from PIL import Image
from multiprocessing import Value
def signal_handler(signal, frame):
    # 关闭子线程循环
    global websocket_event_loop
    websocket_event_loop.stop()
    sys.exit(0)
# 注册SIGINT的处理函数
signal.signal(signal.SIGINT, signal_handler)

is_model_completed = False # 模型/Mesh是否训练/生成完成
is_video_completed = False # 渲染视频生成完成
is_upload_completed = False # 图片是否上传结束，也意味着websocket是否建立连接，模型是否可以开始训练
target_name = sys.argv[1] # 通过命令行运行传递参数，任务名称（=图片存放目录名=生成模型的名称=生成视频的名称）
images_dir_path = './images/' + str(target_name) # 存放图片使用的目录
models_dir_path = './models/' # 存放生成的Mesh模型的目录
videos_dir_path = './videos/' # 存放渲染生成的视频的目录
websocket_event_loop = None
global_websocket = None
is_connection = False
IP = 'localhost'
WEBSOCKET_PORT = 4000
if os.path.exists('./static/profile.json'):
    profile = open('./static/profile.json','r')
    content = profile.read()
    data = json.loads(content)
    IP = data['ip']
    WEBSOCKET_PORT = data['websocket_preview_images_port']
    
# 关闭占用端口的进程
system_name = platform.system()
if system_name == "Windows":
    # 查找占用指定端口的进程ID
    cmd_find_pid = f"netstat -aon | findstr :{WEBSOCKET_PORT}"
    process = subprocess.Popen(cmd_find_pid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # 提取进程ID并去重
    pids = set(line.split()[-1] for line in stdout.decode().splitlines() if "LISTENING" in line)

    # 终止这些进程
    for pid in pids:
        cmd_kill = f"taskkill /F /PID {pid}"
        os.system(cmd_kill)
        print(f"Process {pid} has been terminated.")
elif system_name == "Linux":
    # 查找占用指定端口的进程ID
    cmd_find_pid = f"lsof -i :{WEBSOCKET_PORT} | grep LISTEN | awk '{{print $2}}'"
    process = subprocess.Popen(cmd_find_pid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    stdout, stderr = process.communicate()

    # 提取进程ID并去重
    pids = set(stdout.decode().split())

    # 终止这些进程
    for pid in pids:
        cmd_kill = f"kill -9 {pid}"
        os.system(cmd_kill)
        print(f"Process {pid} has been terminated.")

# 确保LoFTR存放图片的文件路径存在
if not os.path.exists(images_dir_path):
        os.makedirs(images_dir_path)

async def send_loftr_images(websocket):
    global image_path,target_name,is_model_completed,images_dir_path
    try:
        # 模型训练完毕之前的图片发送循环
        counter = 0
         
        # print(images)
        while True:
            if is_model_completed:
                # 如果Mesh已经生成，不再传输images，但是由于还要通过该websocket传输videoCompleted指令，维持此循环
                await asyncio.sleep(1)
                continue
            images = os.listdir(images_dir_path)
            total = len(images)
            # LoFTR还未产生图片
            if total == 0:
                await asyncio.sleep(1)
                continue
            counter %= total
            image_path = images_dir_path+'/'+images[counter]
            counter += 1
            print(f'sending image: {image_path}')
            
            with open(image_path,'rb') as file:
                # await websocket.send(file)
                image_base64 = base64.b64encode(file.read())
                await websocket.send(image_base64.decode('utf-8'))
                
            await asyncio.sleep(3) #每3s循环发送一次图片
    except Exception as e:
        print("Error:", e)
    finally:
        print('the websocket sended images disconnected')
        print('is_model_completed: '+ str(is_model_completed))
        print('is_video_completed: '+ str(is_video_completed))
        

# Server：websocket连接时提供的服务，开始尝试发送LoFTR图片，该函数退出时websocket断开连接
# Client：websocket连接建立时也就是说进入了预览界面，创建了websocket并发起连接请求，说明所有图片上传完成
async def serve(websocket, path):
    global global_websocket,is_upload_completed,is_connection
    global_websocket = websocket
    print("Client Connected")
    is_upload_completed = True
    is_connection = True
    # 连接时启动任务
    websocket_event_loop.create_task(send_loftr_images(websocket))
    try:# 检查当前websocket是否继续连接中
        async for message in websocket:
            print('recv message: '+message)
    finally:
        print("Client disconnected")
        websocket_event_loop.stop()
        await websocket.close()
        print('websocket closed')
        is_connection = False
        # sys.exit(0)

def start_websocket_server():
    global websocket_event_loop,start_server
    websocket_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(websocket_event_loop)

    start_server = websockets.serve(serve, IP, WEBSOCKET_PORT)
    websocket_event_loop.run_until_complete(start_server)
    websocket_event_loop.run_forever()

# 在子线程开启事件循环
sub_thread = threading.Thread(target=start_websocket_server)
# 设置子线程在父进程退出时退出
sub_thread.daemon = True
sub_thread.start()

# 阻塞主线程等待图片上传结束
async def wait_for_connection():
    global is_upload_completed
    while not is_upload_completed:
        await asyncio.sleep(0.1)
        
# 主线程在此忙等，但不影响子线程对websocket的处理
asyncio.get_event_loop().run_until_complete(wait_for_connection())

############测试LOFTR中间图片展示用，记得删除#######
# time.sleep(10)
###############################################

if not os.path.exists(models_dir_path+str(target_name)+'.ply'):
    #####################
    # LoFTR将中间图片存入images_dir_path路径下，命名无所谓
    # 生成Mesh存入./models/文件夹下，命名为target_name.ply
    # @auther: Siner
    ####################
    print("model training ...")


    time.sleep(20)






# 通过回调函数通知websocket在send结束后关闭
async def websocket_send_message(websocket,message,callback):
    # 确保存在模型或视频再发送对应信号
    while message == 'modelCompleted' and not os.path.exists(models_dir_path+str(target_name)+'.ply'):
        await asyncio.sleep(1)
    while message == 'videoCompleted' and not os.path.exists(videos_dir_path+str(target_name)+'.mp4'):
        await asyncio.sleep(1)
    if websocket is not None:
        try:
            await websocket.send(message)
            if callback is not None:
                callback()
        except Exception as e:
            print("Error:", e)
            print('reverie: websocket断开连接')
    
def on_model_completed():
    global is_model_completed
    is_model_completed = True
    print("Sent:Model training completed")
# 确保在模型训练结束时调用
# 通知模型训练/Mesh生成结束，交给子线程的异步事件循环，不影响主线程，确保视频渲染快速开始
# websocket_event_loop.create_task(websocket_send_message(global_websocket,'modelCompleted',on_model_completed))

asyncio.run_coroutine_threadsafe(
    websocket_send_message(global_websocket,'modelCompleted',on_model_completed),
    websocket_event_loop
)
if not os.path.exists(videos_dir_path+str(target_name)+'.mp4'):
    #####################
    # 视频渲染，存在./videos/路径下，以target_name.mp4命名
    # 预览图片，存放在./images_for_history/路径下，以target_name.jpg命名
    # @auther: Siner
    ####################
    print('video renderering ...')


    time.sleep(20)





def on_video_completed():
    global is_video_completed
    is_video_completed = True
    print("Sent:Video rendering completed")
    
# 至此Ai模型任务全部结束
# 确保在视频渲染结束时调用
# 通知视频渲染结束，使用主线程阻塞等待，防止在发送结束前退出
asyncio.run_coroutine_threadsafe(
    websocket_send_message(global_websocket,'videoCompleted',on_video_completed),
    websocket_event_loop
)

async def wait_for_completion():
    global is_model_completed, is_video_completed,is_connection
    while not (is_model_completed and is_video_completed):
        if not is_connection:
            break
        await asyncio.sleep(1)  # 非阻塞等待
    # 所有条件满足后关闭服务器
    print("All tasks completed, shutting down the server.")
    global websocket_event_loop
    if websocket_event_loop.is_running():
        websocket_event_loop.stop()
        
asyncio.run(wait_for_completion())
print("websocket: Main thread exiting...")
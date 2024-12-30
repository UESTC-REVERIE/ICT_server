document.addEventListener("DOMContentLoaded", function() {
    const preview = document.getElementById('preview');
    const img = new Image();
    img.onload = function() {
        preview.appendChild(img);
    };
    img.ondragstart = function() { return false; }; // 禁止拖动图片
    preview.style.pointerEvents = 'none'; // 阻止图像捕获鼠标事件
    let ws;
    // 加载配置文件
    fetch('/static/profile.json')
        .then( response =>response.json())
        .then( data =>{
            ws = new WebSocket(`ws://${data.ip}:${data.websocket_preview_images_port}`);
            ws.onopen = function () {
                // console.log('Connected to server');
            };
        
            ws.onmessage = function (event) {
                // console.log('onmessage');
                if(event.data == 'modelCompleted'){
                    console.log('modelCompleted')
                }
                else if(event.data == 'videoCompleted'){
                    console.log('videoCompleted')
                }
                else{
                    const base64Data = event.data;
                    // 创建一个可以被<img>元素使用的data URL
                    const imgUrl = "data:image/jpeg;base64," + base64Data;
                    img.src = imgUrl; // 设置图像源
                }
            };
        
            ws.onclose = function () {
                // console.log('Connection closed');
            };
        })
     // 监听beforeunload事件
     window.addEventListener('beforeunload', function() {
        if (ws) {
            ws.close(); // 关闭WebSocket连接
        }
    });
});

// 防止鼠标左键拖动时选中图像
document.addEventListener('mousedown', function (event) {
    if (event.button === 0) { // 检查是否为左键
        event.preventDefault();
    }
});

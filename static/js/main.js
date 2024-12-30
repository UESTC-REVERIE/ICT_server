import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
const preview = document.getElementById('preview');
//preview.innerHTML = `<img src="/static/img/preview.png" alt="Preview Image">`;
//const ip = '192.168.50.235'
const ip = 'localhost'
const ws = new WebSocket(`ws://${ip}:3000`);

let imageBuffer = null; // 图像缓冲区

ws.onopen = function () {
    console.log('Connected to server');
};

ws.onmessage = function (event) {
    const imageData = event.data;
    // 将接收到的图像数据存储到缓冲区
    renderImage(imageData)
};

// ws.onmessage = function (event) {
//     const imageData = event.data;
//     // 创建新的 Image 对象
//     const img = new Image();
//     // 当图像加载完成后，替换现有的图像
//     img.onload = function () {
//         preview.innerHTML = ''; // 清空原有内容
//         preview.appendChild(img); // 添加新图像
//     };
//     img.src = "data:image/jpeg;base64," + imageData; // 设置图像源
// };
ws.onclose = function () {
    console.log('Connection closed');
};
// const canvas = document.querySelector('#c2d')
// 渲染器
// width和height用来设置Three.js输出的Canvas画布尺寸(像素px)
const width = window.innerWidth; //窗口文档显示区的宽度作为画布宽度
const height = window.innerHeight; //窗口文档显示区的高度作为画布高度

const renderer = new THREE.WebGLRenderer();
renderer.setSize(width, height);

// const canvas = document.getElementById('canvas');
// canvas.width = 100
// canvas.height = 100

document.body.appendChild(renderer.domElement);

const fov = 40 // 视野范围
const aspect = width / height // 相机默认值 画布的宽高比
const near = 0.1 // 近平面
const far = 1000 // 远平面
// 透视投影相机
const camera = new THREE.PerspectiveCamera(fov, aspect, near, far)
// 定义相机坐标系
camera.position.set(0, 0, 10)
camera.lookAt(0, 0, 0)
// 控制相机
const controls = new OrbitControls(camera, renderer.domElement)
// controls.panSpeed = 0.5;
// controls.rotateSpeed = 0.5;
controls.addEventListener('change',()=>{
    console.log(`camera position : ${camera.position.x} ,${camera.position.y} ,${camera.position.z}`);
    console.log(`camera target : ${controls.target.x} ,${controls.target.y} ,${controls.target.z}`);
    const jsonData = {
        "width": `${width}`,
        "height": `${height}`,
        "posx": `${camera.position.x}`,
        "posy": `${camera.position.y}`,
        "posz": `${camera.position.z}`,
        "targetx":`${controls.target.x}`,
        "targety":`${controls.target.y}`,
        "targetz":`${controls.target.z}`
    };
    ws.send(JSON.stringify(jsonData));
    // plane.lookAt(camera.position);
    // var worldPosTarget = plane.getWorldPosition(new THREE.Vector3(controls.target.x,controls.target.y,camera.position.z-10));
    // plane.position.set(worldPosTarget);
})



// controls.autoRotate = true
// controls.autoRotateSpeed = 1.0
controls.update()

// 场景
const scene = new THREE.Scene()
scene.background = new THREE.Color('black')



{
    // 半球光
    const skyColor = 0xb1e1ff // 蓝色
    const groundColor = 0xffffff // 白色
    const intensity = 1
    const light = new THREE.HemisphereLight(skyColor, groundColor, intensity)
    scene.add(light)
}

{
    // 方向光
    const color = 0xffffff
    const intensity = 1
    const light = new THREE.DirectionalLight(color, intensity)
    light.position.set(0, 10, 0)
    light.target.position.set(-5, 0, 0)
    scene.add(light)
    scene.add(light.target)
}
// {
//     var texture = new THREE.TextureLoader().load( '/static/img/preview.png' );

//    // 立即使用纹理进行材质创建
//    	var material = new THREE.MeshBasicMaterial( { map: texture } );
//     var size = 3
//     var geometry = new THREE.PlaneGeometry( size, size * (height / width) );
//     var plane = new THREE.Mesh( geometry, material );
//     scene.add( plane );
// }
// 渲染图像函数
function renderImage(imageData) {
    // 创建 Blob 对象
    const blob = new Blob([imageData], { type: 'image/jpeg' });

    // 清空预览区域
    preview.innerHTML = '';

    // 创建 Image 元素
    const img = new Image();
    img.onload = function () {
        preview.appendChild(img); // 添加图像到预览区域
    };
    img.src = URL.createObjectURL(blob); // 设置图像源
}
// 渲染
function render() {
    renderer.render(scene, camera)
    // if (imageBuffer) {
    //     // // 创建新的 Image 对象
    //     // const img = new Image();
    //     // // 当图像加载完成后，替换现有的图像
    //     // img.onload = function () {
    //     //     preview.innerHTML = ''; // 清空原有内容
    //     //     preview.appendChild(img); // 添加新图像
    //     // };
    //     // img.src = "data:image/jpeg;base64," + imageBuffer; // 设置图像源
    //     // imageBuffer = null; // 清空缓冲区
    //     // 创建 Blob 对象
    //     const blob = new Blob([imageBuffer], { type: 'image/jpeg' });

    //     // 清空预览区域
    //     preview.innerHTML = '';

    //     // 创建 Image 元素
    //     const img = new Image();
    //     img.onload = function () {
    //         preview.appendChild(img); // 添加图像到预览区域
    //     };
    //     img.src = URL.createObjectURL(blob); // 设置图像源

    //     // 清空图像缓冲区
    //     imageBuffer = null;
    // }
    //controls.update()
    requestAnimationFrame(render)
}
requestAnimationFrame(render)
// 防止鼠标左键拖动时选中图像
document.addEventListener('mousedown', function (event) {
    if (event.button === 0) { // 检查是否为左键
        event.preventDefault();
    }
});
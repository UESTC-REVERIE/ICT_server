import * as THREE from 'three';
import {OBJLoader} from 'three/addons/loaders/OBJLoader.js'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js'
import {PLYLoader} from 'three/addons/loaders/PLYLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
// 添加进度条
const preview = document.getElementById('preview');
const progressBar = document.getElementById('progressBar');
// 隐藏页面滚动条
document.body.style.overflow = 'hidden';

// const canvas = document.querySelector('#c2d')
// 渲染器
// width和height用来设置Three.js输出的Canvas画布尺寸(像素px)
const width = window.innerWidth; //窗口文档显示区的宽度作为画布宽度
const height = window.innerHeight; //窗口文档显示区的高度作为画布高度
const renderer = new THREE.WebGLRenderer();
renderer.setSize(width, height);
// const renderer = new SoftwareRenderer();
// renderer.setSize(width, height);

preview.appendChild(renderer.domElement);

const fov = 40 // 视野范围
const aspect = width / height // 相机默认值 画布的宽高比
const near = 0.1 // 近平面
const far = 1000 // 远平面
// 透视投影相机
const camera = new THREE.PerspectiveCamera(fov, aspect, near, far)
camera.position.set(0, 0, 10)
camera.lookAt(0, 0, 0)
// 控制相机
const controls = new OrbitControls(camera, renderer.domElement)
controls.autoRotate = true
// controls.autoRotateSpeed = 1.0
controls.update()

// 场景
const scene = new THREE.Scene()
scene.background = new THREE.Color('white')

window.addEventListener('resize', () => {
    // 更新尺寸
    const width = window.innerWidth;
    const height = window.innerHeight;

    // 更新渲染器和相机的尺寸
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    
    // 可能需要重新渲染场景
    renderer.render(scene, camera);
});


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
// var url = window.location.href
// var previewName = url.split('/').pop()
// const objectUrl = `/static/resources/${previewName}.obj`
// {
//     const objLoader = new OBJLoader()
//     objLoader.load(objectUrl, 
//         // 加载完成
//         (root) => {
//             scene.add(root)
//         },
//         // 加载中
//         (xhr)=>{
//             progressBar.value = xhr.loaded / xhr.total * 100
//         })
//}
// PLY 点云加载
// var url = window.location.href
// var previewName = url.split('/').pop()
// const objectUrl = `/static/resources/ict_demo.ply`
// {
//     const objLoader = new PLYLoader()
//     objLoader.load(objectUrl, (geometry) => {
//         const material = new THREE.PointsMaterial( {size: 0.03} );
//         material.vertexColors = true;
//         const mesh = new THREE.Points( geometry, material );
//         mesh.position.x = 0;
//         mesh.position.y = -1;
//         mesh.position.z = 0;
//         mesh.scale.multiplyScalar(0.2 );
//         mesh.castShadow = true;
//         mesh.receiveShadow = true;
//         scene.add( mesh );
//     })
// }
var url = window.location.href
var previewName = url.split('/').pop()
const objectUrl = `/download/object/${modelName}.ply`
{
    const plyLoader = new PLYLoader()
    plyLoader.load(objectUrl, 
        //加载完成
        (geometry) => {
            geometry.computeVertexNormals();
            const material = new THREE.MeshBasicMaterial({ vertexColors: true });

            const mesh = new THREE.Mesh( geometry, material );
            mesh.position.x = 0;
            mesh.position.y = 0;
            mesh.position.z = 0;
            mesh.scale.multiplyScalar(0.2 );
            scene.add( mesh );

            progressBar.style.visibility = 'hidden'
        },
        // 加载中
        (xhr)=>{
            progressBar.value = xhr.loaded / xhr.total * 100
        })
    
}
{
    // const loader = new GLTFLoader()
    // loader.setPath('../static/resources/');
    // loader.load('ict_demo_0_r.gltf', function (gltf) {
    //     gltf.scene.traverse(function (child) {
    //         if (child.isMesh) {}
    //     });
    //     scene.add(gltf.scene);
    // })
    // const loader = new GLTFLoader()
    // const dracoLoader = new DRACOLoader()
    // dracoLoader.setDecoderPath('/static/draco/')
    // dracoLoader.setDecoderConfig({ type: "js" }); //使用兼容性强的draco_decoder.js解码器
    // dracoLoader.preload();
    
    // loader.setDRACOLoader(dracoLoader)
    // loader.load("/static/resources/ict_demo.glb",  (obj) => {
    //     scene.add(obj.scene);
    // })

}
// 渲染
function render() {
    renderer.render(scene, camera)
    controls.update()
    requestAnimationFrame(render)
}
requestAnimationFrame(render)

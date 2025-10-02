function openModal() {
    document.getElementById("conversationModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("conversationModal").style.display = "none";
}

//fix modal auto show when refresh
closeModal();

window.onclick = function(event) {
    const modal = document.getElementById("conversationModal");
    if (event.target === modal) {
    closeModal();
    }
}

const canvas = document.getElementById('techCanvas');
const ctx = canvas.getContext('2d');

let width = canvas.width = window.innerWidth;
let height = canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
});

const lines = [];
const numLines = 40;

// สร้างเส้น
for(let i=0; i<numLines; i++){
  lines.push({
    x: Math.random()*width,
    y: Math.random()*height,
    length: 50 + Math.random()*50,
    speed: 0.5 + Math.random(),
    angle: Math.random()*Math.PI * 2
  });
}

// วาดและอัปเดตเส้น
function animate(){
  ctx.clearRect(0,0,width,height);
  ctx.strokeStyle = 'rgba(100,100,100,0.2)';
  ctx.lineWidth = 1;

  for(let line of lines){
    ctx.beginPath();
    ctx.moveTo(line.x, line.y);
    ctx.lineTo(line.x + Math.cos(line.angle)*line.length, line.y + Math.sin(line.angle)*line.length);
    ctx.stroke();

    // อัปเดตตำแหน่ง
    line.x += Math.cos(line.angle)*line.speed;
    line.y += Math.sin(line.angle)*line.speed;

    // ถ้าออกจอ ให้ปรับกลับ
    if(line.x > width || line.x < 0) line.angle = Math.PI - line.angle;
    if(line.y > height || line.y < 0) line.angle = -line.angle;
  }

  requestAnimationFrame(animate);
}

animate();
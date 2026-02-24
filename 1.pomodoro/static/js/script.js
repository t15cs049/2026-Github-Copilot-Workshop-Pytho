// グローバル変数
let timer = null;
let timeLeft = 25 * 60; // 秒単位
let totalTime = 25 * 60;
let isRunning = false;
let isWorkSession = true;
let completedSessions = 0;

// DOM要素
const timeDisplay = document.getElementById('timeDisplay');
const statusText = document.getElementById('statusText');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');
const workDurationInput = document.getElementById('workDuration');
const breakDurationInput = document.getElementById('breakDuration');
const completedSessionsDisplay = document.getElementById('completedSessions');
const progressCircle = document.querySelector('.progress-ring-circle');
const particleCanvas = document.getElementById('particleCanvas');
const rippleContainer = document.getElementById('rippleContainer');

// SVG円周の計算
const radius = progressCircle.r.baseVal.value;
const circumference = 2 * Math.PI * radius;
progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
progressCircle.style.strokeDashoffset = 0;

// パーティクルシステム
class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.life = 1.0;
        this.decay = Math.random() * 0.02 + 0.005;
        this.size = Math.random() * 3 + 1;
    }
    
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= this.decay;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
    
    isDead() {
        return this.life <= 0;
    }
}

// パーティクルマネージャー
let particles = [];
const ctx = particleCanvas.getContext('2d');

function resizeCanvas() {
    particleCanvas.width = window.innerWidth;
    particleCanvas.height = window.innerHeight;
}

function addParticles() {
    if (!isRunning) return;
    
    // 中央からランダムな位置にパーティクルを追加
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * 100;
    const x = centerX + Math.cos(angle) * distance;
    const y = centerY + Math.sin(angle) * distance;
    
    particles.push(new Particle(x, y));
    
    // パーティクル数を制限
    if (particles.length > 50) {
        particles = particles.slice(-50);
    }
}

function updateParticles() {
    ctx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);
    
    particles = particles.filter(p => !p.isDead());
    particles.forEach(p => {
        p.update();
        p.draw(ctx);
    });
    
    requestAnimationFrame(updateParticles);
}

// 波紋エフェクト
function createRipple() {
    if (!isRunning) return;
    
    const ripple = document.createElement('div');
    ripple.className = 'ripple';
    
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    
    ripple.style.left = `${centerX}px`;
    ripple.style.top = `${centerY}px`;
    ripple.style.marginLeft = '-150px';
    ripple.style.marginTop = '-150px';
    
    rippleContainer.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 2000);
}

// 時間のフォーマット
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// プログレスバーの更新
function updateProgress() {
    const progress = timeLeft / totalTime;
    const offset = circumference * (1 - progress);
    progressCircle.style.strokeDashoffset = offset;
    
    // 色の変化を適用
    updateColorState(progress);
}

// 色の状態を更新（青→黄→赤）
function updateColorState(progress) {
    const svg = document.querySelector('.progress-ring');
    svg.classList.remove('state-start', 'state-middle', 'state-end');
    
    if (progress > 0.66) {
        svg.classList.add('state-start'); // 青
    } else if (progress > 0.33) {
        svg.classList.add('state-middle'); // 黄
    } else {
        svg.classList.add('state-end'); // 赤
    }
}

// タイマーの更新
function updateTimer() {
    timeDisplay.textContent = formatTime(timeLeft);
    updateProgress();
    
    if (timeLeft <= 0) {
        completeSession();
    }
}

// タイマーのティック
function tick() {
    if (timeLeft > 0) {
        timeLeft--;
        updateTimer();
    }
}

// セッション完了
function completeSession() {
    stopTimer();
    
    if (isWorkSession) {
        completedSessions++;
        completedSessionsDisplay.textContent = completedSessions;
        statusText.textContent = '休憩時間！';
        alert('お疲れ様です！休憩時間です。');
    } else {
        statusText.textContent = '作業開始！';
        alert('休憩終了！次のセッションを始めましょう。');
    }
    
    // セッションを切り替え
    isWorkSession = !isWorkSession;
    resetTimer();
}

// タイマー開始
function startTimer() {
    if (!isRunning) {
        isRunning = true;
        timer = setInterval(tick, 1000);
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        workDurationInput.disabled = true;
        breakDurationInput.disabled = true;
        statusText.textContent = isWorkSession ? '集中中...' : '休憩中...';
        
        // パーティクルと波紋の開始
        setInterval(addParticles, 200);
        setInterval(createRipple, 3000);
    }
}

// タイマー停止
function stopTimer() {
    if (isRunning) {
        isRunning = false;
        clearInterval(timer);
        timer = null;
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        statusText.textContent = '一時停止';
    }
}

// タイマーリセット
function resetTimer() {
    stopTimer();
    
    if (isWorkSession) {
        const workMinutes = parseInt(workDurationInput.value) || 25;
        totalTime = workMinutes * 60;
    } else {
        const breakMinutes = parseInt(breakDurationInput.value) || 5;
        totalTime = breakMinutes * 60;
    }
    
    timeLeft = totalTime;
    updateTimer();
    workDurationInput.disabled = false;
    breakDurationInput.disabled = false;
    statusText.textContent = '準備完了';
}

// イベントリスナー
startBtn.addEventListener('click', startTimer);
pauseBtn.addEventListener('click', stopTimer);
resetBtn.addEventListener('click', resetTimer);

workDurationInput.addEventListener('change', () => {
    if (!isRunning && isWorkSession) {
        resetTimer();
    }
});

breakDurationInput.addEventListener('change', () => {
    if (!isRunning && !isWorkSession) {
        resetTimer();
    }
});

// 初期化
window.addEventListener('resize', resizeCanvas);
resizeCanvas();
updateTimer();
updateParticles();

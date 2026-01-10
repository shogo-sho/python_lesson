
const wordDisplay = document.getElementById('word-display');
const wordInput = document.getElementById('word-input');
const scoreEl = document.getElementById('score');
const timeEl = document.getElementById('time');
const messageEl = document.getElementById('message');
const gameOverScreen = document.getElementById('game-over-screen');
const finalScoreEl = document.getElementById('final-score');
const matrixCanvas = document.getElementById('matrix-bg');
const ctx = matrixCanvas.getContext('2d');

let words = [
    'PYTHON', 'JAVASCRIPT', 'HTML', 'CSS', 'VARIABLE',
    'FUNCTION', 'ARRAY', 'OBJECT', 'LOOP', 'CONDITION',
    'CLASS', 'METHOD', 'IMPORT', 'EXPORT', 'PROMISE',
    'ASYNC', 'AWAIT', 'DEBUG', 'COMPILE', 'RUNTIME',
    'ALGORITHM', 'DATABASE', 'SERVER', 'CLIENT', 'API',
    'FRAMEWORK', 'LIBRARY', 'SYNTAX', 'ERROR', 'EXCEPTION',
    'INTEGER', 'STRING', 'BOOLEAN', 'FLOAT', 'NULL',
    'UNDEFINED', 'RECURSION', 'ITERATION', 'POINTER', 'TERMINAL',
    'SHELL', 'KERNEL', 'NETWORK', 'PROTOCOL', 'ENCRYPTION'
];

let score = 0;
let time = 60;
let isPlaying = false;
let currentWord;
let timerInterval;

// Audio Context Setup for Typing Sound
const AudioContext = window.AudioContext || window.webkitAudioContext;
const audioCtx = new AudioContext();

function playKeySound() {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'square';
    // Randomize pitch slightly for realism
    oscillator.frequency.setValueAtTime(800 + Math.random() * 400, audioCtx.currentTime);

    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.1);
}

// Matrix Rain Effect
matrixCanvas.width = window.innerWidth;
matrixCanvas.height = window.innerHeight;

const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
const fontSize = 16;
const columns = matrixCanvas.width / fontSize;
const drops = [];

for (let x = 0; x < columns; x++) {
    drops[x] = 1;
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);

    ctx.fillStyle = '#0F0';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
        const text = matrixChars.charAt(Math.floor(Math.random() * matrixChars.length));
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > matrixCanvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}

setInterval(drawMatrix, 33);

window.addEventListener('resize', () => {
    matrixCanvas.width = window.innerWidth;
    matrixCanvas.height = window.innerHeight;
});

// Game Logic
function init() {
    messageEl.innerHTML = 'Press Enter to Start';
}

function startGame() {
    if (isPlaying) return;
    isPlaying = true;
    score = 0;
    time = 60;
    scoreEl.innerText = score;
    timeEl.innerText = time;
    messageEl.innerText = '';
    wordInput.value = '';
    wordInput.focus();

    showNewWord();

    timerInterval = setInterval(countDown, 1000);
}

function showNewWord() {
    const randIndex = Math.floor(Math.random() * words.length);
    currentWord = words[randIndex];
    wordDisplay.innerText = currentWord;
}

function countDown() {
    if (time > 0) {
        time--;
        timeEl.innerText = time;
    } else {
        gameOver();
    }
}

function gameOver() {
    isPlaying = false;
    clearInterval(timerInterval);
    gameOverScreen.classList.add('show');
    finalScoreEl.innerText = score;
}

// Event Listeners
wordInput.addEventListener('input', () => {
    playKeySound();

    // Normalize input: Convert full-width to half-width and then uppercase
    const rawInput = wordInput.value;
    const normalizedInput = rawInput.replace(/[Ａ-Ｚａ-ｚ０-９]/g, (s) => {
        return String.fromCharCode(s.charCodeAt(0) - 0xFEE0);
    }).toUpperCase();

    if (isPlaying && normalizedInput === currentWord) {
        score++;
        scoreEl.innerText = score;
        wordInput.value = '';
        showNewWord();
        // Visual feedback for correct word
        wordDisplay.style.color = '#fff';
        setTimeout(() => wordDisplay.style.color = '#0F0', 100);
    }
});

window.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !isPlaying) {
        startGame();
    }
    // Also play sound on other keys even if not inputting text directly (immersion)
    if (e.key !== 'Enter') {
        // handle input event for sound usually, but keydown covers non-char keys too
    }
});

// Focus input mainly
document.addEventListener('click', () => {
    if (isPlaying) wordInput.focus();
});

init();

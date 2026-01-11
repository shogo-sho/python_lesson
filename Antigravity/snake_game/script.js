const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');

const gridSize = 20;
const tileCount = canvas.width / gridSize;

let score = 0;
let snake = [];
let food = { x: 15, y: 15 };
let dx = 0;
let dy = 0;
let changingDirection = false;
let gameSpeed = 100;
let gameInterval;
let isGameRunning = false;

function init() {
    score = 0;
    snake = [{ x: 10, y: 10 }];
    dx = 0;
    dy = 0;
    gameSpeed = 100;
    isGameRunning = true;
    spawnFood();
    scoreElement.textContent = score;

    if (gameInterval) clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, gameSpeed);
}

function gameLoop() {
    if (!isGameRunning) return;

    if (hasGameEnded()) {
        isGameRunning = false;
        clearInterval(gameInterval);
        setTimeout(() => {
            alert(`GAME OVER! Score: ${score}\nOKを押してリスタート`);
            init();
        }, 100);
        return;
    }

    changingDirection = false;
    moveSnake();
    draw();
}

function moveSnake() {
    // まだ動いていないときは更新しない（待機状態）
    if (dx === 0 && dy === 0) return;

    const head = { x: snake[0].x + dx, y: snake[0].y + dy };
    snake.unshift(head);

    // 食べたか判定
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreElement.textContent = score;
        spawnFood();
        // 少しずつ速くする
        if (gameSpeed > 50) {
            clearInterval(gameInterval);
            gameSpeed -= 2;
            gameInterval = setInterval(gameLoop, gameSpeed);
        }
    } else {
        snake.pop();
    }
}

function spawnFood() {
    food = {
        x: Math.floor(Math.random() * tileCount),
        y: Math.floor(Math.random() * tileCount)
    };
    // 蛇の上に重ならないようにする
    snake.forEach(part => {
        if (part.x === food.x && part.y === food.y) spawnFood();
    });
}

function hasGameEnded() {
    const head = snake[0];

    // 壁衝突
    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        return true;
    }

    // 自己衝突（頭以外とぶつかったか）
    for (let i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            return true;
        }
    }
    return false;
}

function draw() {
    // 画面クリア
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 蛇の描画
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#39ff14';
    snake.forEach((part, index) => {
        // 頭は少し明るく、体は標準のネオングリーン
        ctx.fillStyle = index === 0 ? '#ccffcc' : '#39ff14';
        ctx.fillRect(part.x * gridSize, part.y * gridSize, gridSize - 2, gridSize - 2);
    });

    // 餌の描画
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ff003c';
    ctx.fillStyle = '#ff003c';
    ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);

    // シャドウのリセット（UIなど他への影響を防ぐため）
    ctx.shadowBlur = 0;
}

// キー操作
document.addEventListener('keydown', changeDirection);

function changeDirection(event) {
    // 矢印キー以外でスクロールするのを防ぐ
    if ([37, 38, 39, 40].includes(event.keyCode)) {
        event.preventDefault();
    }

    if (changingDirection) return;

    const LEFT_KEY = 37;
    const RIGHT_KEY = 39;
    const UP_KEY = 38;
    const DOWN_KEY = 40;

    const keyPressed = event.keyCode;
    const goingUp = dy === -1;
    const goingDown = dy === 1;
    const goingRight = dx === 1;
    const goingLeft = dx === -1;

    // まだ動いていないときの最初の入力
    if (dx === 0 && dy === 0) {
        if (keyPressed === LEFT_KEY) { dx = -1; dy = 0; }
        if (keyPressed === UP_KEY) { dx = 0; dy = -1; }
        if (keyPressed === RIGHT_KEY) { dx = 1; dy = 0; }
        if (keyPressed === DOWN_KEY) { dx = 0; dy = 1; }
        changingDirection = true;
        return;
    }

    if (keyPressed === LEFT_KEY && !goingRight) {
        dx = -1;
        dy = 0;
        changingDirection = true;
    }
    if (keyPressed === UP_KEY && !goingDown) {
        dx = 0;
        dy = -1;
        changingDirection = true;
    }
    if (keyPressed === RIGHT_KEY && !goingLeft) {
        dx = 1;
        dy = 0;
        changingDirection = true;
    }
    if (keyPressed === DOWN_KEY && !goingUp) {
        dx = 0;
        dy = 1;
        changingDirection = true;
    }
}

// ゲーム開始
init();
draw(); // 最初の1フレームを描画して待機

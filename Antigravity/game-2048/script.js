document.addEventListener('DOMContentLoaded', () => {
    const gridContainer = document.getElementById('tile-container');
    const scoreElement = document.getElementById('score');
    const bestScoreElement = document.getElementById('best-score');
    const newGameButton = document.getElementById('new-game-button');
    const gameMessage = document.querySelector('.game-message');
    const retryButton = document.querySelector('.retry-button');
    const keepPlayingButton = document.querySelector('.keep-playing-button');

    const gridSize = 4;
    let grid = [];
    let score = 0;
    let bestScore = localStorage.getItem('2048-bestScore') || 0;

    // Game state
    let won = false;
    let keepPlaying = false;

    // Initialize
    updateBestScoreDisplay();
    initGame();

    newGameButton.addEventListener('click', () => restart());
    retryButton.addEventListener('click', () => restart());
    keepPlayingButton.addEventListener('click', () => {
        keepPlaying = true;
        gameMessage.style.display = 'none';
    });

    // Touch handling variables
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    document.addEventListener('keydown', handleInput);

    // Touch Events
    const gameContainer = document.querySelector('.game-container');
    gameContainer.addEventListener('touchstart', (e) => {
        if (e.touches.length > 1) return; // Ignore multi-touch
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: false });

    gameContainer.addEventListener('touchmove', (e) => {
        e.preventDefault(); // Prevent scrolling
    }, { passive: false });

    gameContainer.addEventListener('touchend', (e) => {
        if (e.changedTouches.length > 0) {
            touchEndX = e.changedTouches[0].clientX;
            touchEndY = e.changedTouches[0].clientY;
            handleSwipe();
        }
    });

    function initGame() {
        const savedState = localStorage.getItem('2048-gameState');
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                if (state.grid && state.score !== undefined && state.grid.length === gridSize) {
                    grid = state.grid;
                    score = state.score;
                    won = state.won || false;
                    keepPlaying = state.keepPlaying || false;

                    if (state.over) {
                        // If saved game was over, just restart
                        restart();
                        return;
                    }
                    updateView();
                    return;
                }
            } catch (e) {
                console.error("Error loading save", e);
            }
        }

        restart();
    }

    function restart() {
        grid = Array(gridSize).fill().map(() => Array(gridSize).fill(null));
        score = 0;
        won = false;
        keepPlaying = false;
        gameMessage.style.display = 'none';

        addRandomTile();
        addRandomTile();

        updateView();
        saveState();
    }

    function addRandomTile() {
        const emptyCells = [];
        for (let r = 0; r < gridSize; r++) {
            for (let c = 0; c < gridSize; c++) {
                if (!grid[r][c]) {
                    emptyCells.push({ r, c });
                }
            }
        }

        if (emptyCells.length > 0) {
            const { r, c } = emptyCells[Math.floor(Math.random() * emptyCells.length)];
            grid[r][c] = {
                value: Math.random() < 0.9 ? 2 : 4,
                id: Date.now() + Math.random(), // unique ID for transitions
                isNew: true,
                isMerged: false
            };
        }
    }

    function updateView() {
        gridContainer.innerHTML = '';
        scoreElement.textContent = score;

        // Clear component flags for next render

        for (let r = 0; r < gridSize; r++) {
            for (let c = 0; c < gridSize; c++) {
                const tile = grid[r][c];
                if (tile) {
                    const tileDiv = document.createElement('div');
                    const x = c * (100 / gridSize); // Approximate for now, using CSS for precise visual
                    const y = r * (100 / gridSize);

                    // We use CSS transforms for position
                    // The CSS defines --tile-size and --grid-spacing. 
                    // We need to calculate pixel positions or use grid-row/col logic if we weren't doing smooth animations.
                    // For smooth animations, we need absolute positioning coordinates.

                    // Better approach: Use classes like .tile-position-1-1
                    // But standard 2048 uses pixels. Let's use CSS Custom Properties or simple calcs.
                    // Actually, to keep it simple and responsive, let's use the transform approach in style.css
                    // We need standard positions. 

                    // Let's rely on the CSS variable calc logic + JS style injection or classes.
                    // To make it easiest: Let's use `transform: translate(Xpx, Ypx)`

                    // Calculate metrics dynamically from CSS for perfect alignment
                    const containerStyle = getComputedStyle(document.body); // CSS vars are on :root (html) or body usually inherits, checking root is safer but var is defined in :root
                    // In style.css defined in :root. getComputedStyle(document.documentElement) is best.
                    const rootStyle = getComputedStyle(document.documentElement);
                    const gapStr = rootStyle.getPropertyValue('--grid-spacing').trim();
                    const effectiveSpacing = parseFloat(gapStr) || 15;

                    const containerWidth = document.querySelector('.game-container').offsetWidth;
                    // Recalculate tile size based on container width and spacing, mirroring the CSS calc()
                    // --tile-size: (width - (spacing * (rows + 1))) / rows
                    const effectiveTileSize = (containerWidth - (effectiveSpacing * (gridSize + 1))) / gridSize;

                    const pX = effectiveSpacing + c * (effectiveTileSize + effectiveSpacing);
                    const pY = effectiveSpacing + r * (effectiveTileSize + effectiveSpacing);

                    tileDiv.style.transform = `translate(${pX}px, ${pY}px)`;
                    tileDiv.classList.add('tile');
                    tileDiv.classList.add(`tile-${tile.value <= 2048 ? tile.value : 'super'}`);

                    if (tile.isNew) tileDiv.classList.add('tile-new');
                    if (tile.isMerged) tileDiv.classList.add('tile-merged');

                    const inner = document.createElement('div');
                    inner.classList.add('tile-inner');
                    inner.textContent = tile.value;

                    tileDiv.appendChild(inner);
                    gridContainer.appendChild(tileDiv);

                    // Reset flags
                    tile.isNew = false;
                    tile.isMerged = false;
                }
            }
        }
    }

    // Re-render on resize to fix positions
    window.addEventListener('resize', updateView);

    function handleInput(e) {
        if (gameMessage.style.display === 'flex' && !keepPlaying) return;

        let moved = false;
        switch (e.key) {
            case 'ArrowUp': moved = move(0, -1); break;
            case 'ArrowDown': moved = move(0, 1); break;
            case 'ArrowLeft': moved = move(-1, 0); break;
            case 'ArrowRight': moved = move(1, 0); break;
            default: return;
        }

        if (moved) {
            e.preventDefault();
            afterMove();
        }
    }

    function handleSwipe() {
        if (gameMessage.style.display === 'flex' && !keepPlaying) return;

        const dx = touchEndX - touchStartX;
        const dy = touchEndY - touchStartY;
        const absDx = Math.abs(dx);
        const absDy = Math.abs(dy);

        if (Math.max(absDx, absDy) < 10) return; // Tap

        let moved = false;
        if (absDx > absDy) {
            // Horizontal
            if (dx > 0) moved = move(1, 0); // Right
            else moved = move(-1, 0); // Left
        } else {
            // Vertical
            if (dy > 0) moved = move(0, 1); // Down
            else moved = move(0, -1); // Up
        }

        if (moved) afterMove();
    }

    function move(dx, dy) {
        // dx: 1 (right), -1 (left)
        // dy: 1 (down), -1 (up)

        // Define traversal order
        // If Moving Right (dx=1), process cols from right to left (3 to 0)
        // If Moving Down (dy=1), process rows from bottom to top (3 to 0)

        let moved = false;
        const traverseX = dx === 1 ? [3, 2, 1, 0] : [0, 1, 2, 3];
        const traverseY = dy === 1 ? [3, 2, 1, 0] : [0, 1, 2, 3];

        let mergedMap = Array(gridSize).fill().map(() => Array(gridSize).fill(false));

        traverseY.forEach(r => {
            traverseX.forEach(c => {
                if (grid[r][c]) {
                    // Calculate furthest position
                    let cell = { r: r, c: c };
                    let next = { r: r + dy, c: c + dx };

                    while (isWithinBounds(next) && !grid[next.r][next.c]) {
                        cell = next;
                        next = { r: next.r + dy, c: next.c + dx };
                    }

                    // Check merge
                    if (isWithinBounds(next) && grid[next.r][next.c] &&
                        grid[next.r][next.c].value === grid[r][c].value &&
                        !mergedMap[next.r][next.c]) {

                        // Merge
                        const mergedValue = grid[r][c].value * 2;
                        score += mergedValue;
                        grid[next.r][next.c] = {
                            value: mergedValue,
                            id: grid[r][c].id, // keep id logic simple for now
                            isNew: false,
                            isMerged: true
                        };
                        grid[r][c] = null;
                        mergedMap[next.r][next.c] = true;
                        moved = true;

                        // Update best score
                        if (score > bestScore) {
                            bestScore = score;
                            localStorage.setItem('2048-bestScore', bestScore);
                            updateBestScoreDisplay();
                        }

                        if (mergedValue === 2048 && !won) {
                            won = true;
                            showGameWon();
                        }

                    } else if (cell.r !== r || cell.c !== c) {
                        // Move to empty
                        grid[cell.r][cell.c] = grid[r][c];
                        grid[r][c] = null;
                        moved = true;
                    }
                }
            });
        });

        return moved;
    }

    function isWithinBounds(pos) {
        return pos.r >= 0 && pos.r < gridSize && pos.c >= 0 && pos.c < gridSize;
    }

    function afterMove() {
        addRandomTile();
        updateView();
        saveState();

        if (!movesAvailable()) {
            showGameOver();
        }
    }

    function movesAvailable() {
        // Check for empty cells
        for (let r = 0; r < gridSize; r++)
            for (let c = 0; c < gridSize; c++)
                if (!grid[r][c]) return true;

        // Check for merges
        for (let r = 0; r < gridSize; r++) {
            for (let c = 0; c < gridSize; c++) {
                const val = grid[r][c].value;
                const dirs = [[0, 1], [1, 0]]; // Only need check down and right to cover all adjacents
                for (let d = 0; d < dirs.length; d++) {
                    const nr = r + dirs[d][0];
                    const nc = c + dirs[d][1];
                    if (isWithinBounds({ r: nr, c: nc }) && grid[nr][nc].value === val) return true;
                }
            }
        }
        return false;
    }

    function saveState() {
        localStorage.setItem('2048-gameState', JSON.stringify({
            grid: grid,
            score: score,
            won: won,
            keepPlaying: keepPlaying,
            over: !movesAvailable()
        }));
    }

    function updateBestScoreDisplay() {
        bestScoreElement.textContent = bestScore;
    }

    function showGameWon() {
        gameMessage.classList.add('game-won');
        gameMessage.querySelector('p').textContent = "You Win!";
        gameMessage.style.display = 'flex';
    }

    function showGameOver() {
        gameMessage.classList.remove('game-won');
        gameMessage.classList.add('game-over');
        gameMessage.querySelector('p').textContent = "Game Over!";
        gameMessage.style.display = 'flex';
    }
});

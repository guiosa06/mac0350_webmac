document.body.addEventListener("htmx:afterSwap", (htmx_swap) => {

    const aux = document.querySelector("#aux")
    if(aux!=null) {
        let color = aux.className;
        if (color == "red htmx-added") {
            color = "crimson";
        }
        else if (color == "purple htmx-added") {
            color = "blueviolet";
        }
        else if (color == "blue htmx-added") {
            color = "dodgerblue";
        }
        else if (color == "green htmx-added") {
            color = "mediumseagreen";
        }
        else if (color == "orange htmx-added") {
            color = "coral";
        }
        else if (color == "pink htmx-added") {
            color = "hotpink";
        }
        document.querySelector(":root").style.setProperty('--color', color);
    }

    ///////////////////////////////////////////////////////
    // CONSTANTS
    const dirX = [0, 0, 1, -1];
    const dirY = [1, -1, 0, 0];
    const N = 20;
    const board = document.querySelector("#board");
    const scoreElement = document.querySelector("#score");
    const startScreen = document.querySelector("#start-screen");
    const winScreen = document.querySelector("#win-screen");
    const gameOverScreen = document.querySelector("#game-over-screen");

    ///////////////////////////////////////////////////////
    // GAME VARIABLES
    let snake;
    let dirIndex = 0;
    let apple = [1, 1];
    let intervalID = null;
    let gameRunning = 0;
    let menuOn = 0;
    let score = 0;

    ///////////////////////////////////////////////////////
    // MARKED
    let marked = [];
    for (let i = 0; i <= N; i++) {
        let row = [];
        for (let j = 0; j <= N; j++) row.push(0);
        marked.push(row);
    }
    function mark(cell) {
        marked[cell[0]][cell[1]] = 1;
    }
    function unmark(cell) {
        marked[cell[0]][cell[1]] = 0;
    }
    function check(cell) {
        return (cell[0] > 0 && cell[0] <= N && cell[1] > 0 && cell[1] <= N && !marked[cell[0]][cell[1]]);
    }



    ///////////////////////////////////////////////////////
    // DRAW GAME ELEMENTS
    function addToGrid(tag, className, cell) {
        const newElement = document.createElement(tag);
        newElement.className = className;
        // set position in grid display
        newElement.style.gridRow = cell[0];
        newElement.style.gridColumn = cell[1];

        return newElement;
    }
    function spawnApple() {
        // use random function to randomize apple position
        let newApple = [Math.floor(Math.random() * N) + 1, Math.floor(Math.random() * N) + 1];
        while (!check(newApple)) {
            newApple = [Math.floor(Math.random() * N) + 1, Math.floor(Math.random() * N) + 1];
        }
        apple = newApple;
    }
    function drawBoard() {
        // clear board
        board.innerHTML = "";
        // add snake
        snake.forEach((cell) => {
            board.appendChild(addToGrid("div", "snake", cell));
        });
        // add apple
        board.appendChild(addToGrid("div", "apple", apple));
    }



    ///////////////////////////////////////////////////////
    // GAME FUNCTIONALITIES
    function startGame() {
        startScreen.style.visibility = "hidden";
        winScreen.style.visibility = "hidden";
        gameOverScreen.style.visibility = "hidden";
        score = 0;
        scoreElement.innerText = score;

        // initialize 'marked'
        for (let i = 0; i <= N; i++) {
            for (let j = 0; j <= N; j++) marked[i][j] = 0;
        }

        // initialize snake and apple
        snake = [[Math.floor(N / 2), Math.floor(N / 2)], [Math.floor(N / 2), Math.floor(N / 2) + 1]];
        snake.forEach((cell) => {
            mark(cell);
        });
        dirIndex = 0;
        spawnApple();

        // draw
        drawBoard();

        // start interval
        startLoop();
    }
    function startLoop() {
        clearInterval(intervalID);

        intervalID = setInterval(() => {
            walkSnake();
            drawBoard();
        }, 120);
    }
    function walkSnake() {
        let head = snake[(snake.length) - 1];
        let next = [head[0] + dirX[dirIndex], head[1] + dirY[dirIndex]];

        if (!check(next)) {
            gameOver();
        }
        else {
            mark(next);
            snake.push(next);
            if (next[0] === apple[0] && next[1] === apple[1]) {
                spawnApple();
                scoreElement.innerText = ++score;
            }
            else {
                let tail = snake.shift();
                unmark(tail);
            }
        }
    }
    function changeDir(newDir) {
        if ((newDir == 0 && dirIndex != 1)
            || (newDir == 1 && dirIndex != 0)
            || (newDir == 2 && dirIndex != 3)
            || (newDir == 3 && dirIndex != 2)) dirIndex = newDir;
    }



    ///////////////////////////////////////////////////////
    // Game Over with DB function
    async function saveScore() {
        const data = {
            score: score,
            player_id: ""
        };
        const resposta = await fetch('/game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    }
    function gameOver() {
        clearInterval(intervalID);
        gameRunning = 0;
        board.innerHTML = "";
        if (score === 400) winScreen.style.visibility = "visible";
        else gameOverScreen.style.visibility = "visible";

        saveScore();
    }


    ///////////////////////////////////////////////////////
    // KEYDOWN LISTENER
    let waitALittle = 0;
    document.addEventListener("keydown", (e) => {
        if (waitALittle) return;
        if (e.key === "Enter" && !gameRunning) {
            gameRunning = 1;
            startGame();
        }
        else if (e.key === "Enter" && menuOn) {
            gameRunning = 1;
            menuOn = 0;
            document.querySelector("#menu-screen").style.visibility = "hidden";
            startLoop;
        }
        else if ((e.key === "ArrowRight" || e.key === "d")) {
            changeDir(0);
        }
        else if ((e.key === "ArrowLeft" || e.key === "a")) {
            changeDir(1);
        }
        else if ((e.key === "ArrowDown" || e.key === "s")) {
            changeDir(2);
        }
        else if ((e.key === "ArrowUp" || e.key === "w")) {
            changeDir(3);
        }
    });


});


CREATE TABLE player {
    player_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    game_color TEXT NOT NULL,
};

CREATE TABLE game {
    game_id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    score INTEGER NOT NULL,

    FOREIGN KEY (player_id) REFERENCES player(player_id)
};
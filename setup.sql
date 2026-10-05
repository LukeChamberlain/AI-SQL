create table person (
    person_id integer primary key auto_increment,
    first_name varchar(35) not null,
    last_name varchar(35) not null,
    birth_date date not null
);

create table team_location (
    location_id integer primary key auto_increment,
    street varchar(50) not null,
    zip integer not null,
    city varchar(35) not null,
    state varchar(35) not null
);

create table stadium (
    stadium_id integer primary key auto_increment,
    location_id integer not null,
    capacity integer not null,
    build_date date not null,
    style varchar(35) not null,
    foreign key (location_id) references team_location (location_id)
);

create table coach (
    coach_id integer primary key auto_increment,
    person_id integer not null,
    years_coaching integer not null,
    years_on_current_team integer not null,
    position varchar(35) not null,
    start_date date not null,
    foreign key (person_id) references person (person_id)
);

create table team (
    team_id integer primary key auto_increment,
    team_name varchar(50) not null,
    coach_id integer not null,
    location_id integer not null,
    foreign key (coach_id) references coach (coach_id),
    foreign key (location_id) references team_location (location_id)
);

create table player (
    player_id integer primary key auto_increment,
    person_id integer not null,
    height_inches float not null,
    weight float not null,
    position varchar(35) not null,
    years_in_league integer not null,
    number integer not null,
    team_id integer not null,
    foreign key (person_id) references person (person_id),
    foreign key (team_id) references team (team_id)
);

create table game (
    game_id integer primary key auto_increment,
    location_id integer not null,
    home_team_id integer not null,
    away_team_id integer not null,
    home_team_score integer not null,
    away_team_score integer not null,
    date date not null,
    season integer not null,
    week integer not null,
    foreign key (location_id) references stadium (stadium_id),
    foreign key (home_team_id) references team (team_id),
    foreign key (away_team_id) references team (team_id)
);

create table offensive_stats (
    stat_id integer primary key auto_increment,
    player_id integer not null,
    game_id integer not null,
    yards float not null,
    touchdowns integer not null,
    attempts integer not null,
    completions integer not null,
    interceptions integer not null,
    fumbles integer not null,
    rushing_yards float not null,
    receiving_yards float not null,
    rush_attempts integer not null,
    targets integer not null,
    catches integer not null,
    foreign key (player_id) references player (player_id),
    foreign key (game_id) references game (game_id)
);

create table defensive_stats (
    stat_id integer primary key auto_increment,
    player_id integer not null,
    game_id integer not null,
    tackles float not null,
    pass_def float not null,
    sacks float not null,
    forced_fumbles integer not null,
    interceptions integer not null,
    fumble_recoveries integer not null,
    tackles_for_a_loss float not null,
    foreign key (player_id) references player (player_id),
    foreign key (game_id) references game (game_id)
);
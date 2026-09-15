package config

type configDefinition struct {
	Levels  []Level `toml:"level"`
	General general
}

type Level struct {
	Flag           string         `toml:"flag"`
	SolvesRequired int            `toml:"solves_needed"`
	PuzzleWidth    int            `toml:"puzzle_width"`
	PuzzleHeight   int            `toml:"puzzle_height"`
	Images         []*PuzzleImage `toml:"image"`
	TimeLimit      int            `toml:"time_limit_seconds"`
	ShowTimeLimit  bool           `toml:"show_time_limit"`
	BasePoints     int            `toml:"base_points"`
}

type Chunk struct {
	Data  string `json:"data"`
	Index int    `json:"index"`
}

type WinMessage struct {
	Text string `json:"text"`
}

type PuzzleImage struct {
	FilePath    string `toml:"path"`
	Title       string `toml:"title"`
	Artist      string `toml:"artist"`
	URL         string `toml:"url"`
	ImageChunks []*Chunk
	TileWidth   int `json:"tile_width"`
	TileHeight  int `json:"tile_height"`
}

type general struct {
	WinMessages           []WinMessage `toml:"winmessage"`
	ExpiredWinMessages    []WinMessage `toml:"expiredmessage"`
	RateLimitMillis       int          `toml:"ratelimit_ms"`
	MaxUsernameChars      int          `toml:"max_username_length"`
	MinUsernameChars      int          `toml:"min_username_length"`
	UsernameBlacklist     []string     `toml:"username_blacklist"`
	BorderWidth           int          `toml:"border_width"`
	AdminAccountName      string       `toml:"admin_name"`
	VerifyPointsThreshold int          `toml:"verify_points"`
	BindAddress           string       `toml:"bind_address"`
	ApplicationURL        string       `toml:"application_url"`
}

var Config = configDefinition{
	Levels:  []Level{},
	General: general{},
}

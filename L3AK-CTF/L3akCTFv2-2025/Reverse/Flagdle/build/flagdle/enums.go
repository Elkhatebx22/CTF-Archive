package flagdle

type CellStatus int
type GameState int

const (
	CellStatusEmpty CellStatus = iota
	CellStatusGrey
	CellStatusYellow
	CellStatusGreen
)

const (
	GameStateUndefined GameState = iota
	GameStateInProgress
	GameStateOutOfMoves
	GameStateWon
)

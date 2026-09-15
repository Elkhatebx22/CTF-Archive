package utils

import (
	"fmt"
	"time"
)

func DurationHumanReadable(d time.Duration) string {
	seconds := int(d.Seconds())
	minutes := seconds / 60
	hours := minutes / 60
	days := hours / 24
	weeks := days / 7
	months := days / 30
	years := days / 365

	var value int
	var unit string

	switch {
	case years > 0:
		value, unit = years, "year"
	case months > 0:
		value, unit = months, "month"
	case weeks > 0:
		value, unit = weeks, "week"
	case days > 0:
		value, unit = days, "day"
	case hours > 0:
		value, unit = hours, "hour"
	case minutes > 0:
		value, unit = minutes, "minute"
	default:
		value, unit = seconds, "second"
	}

	if value > 1 || value == 0 {
		unit += "s"
	}

	return fmt.Sprintf("%d %s", value, unit)
}

func TimeHumanReadable(t time.Time) string {
	now := time.Now()
	var duration time.Duration
	var suffix string
	var prefix string

	if t.Before(now) {
		duration = now.Sub(t)
		suffix = " ago"
	} else {
		duration = t.Sub(now)
		prefix = "in "
	}

	return fmt.Sprintf("%s%s%s", prefix, DurationHumanReadable(duration), suffix)
}

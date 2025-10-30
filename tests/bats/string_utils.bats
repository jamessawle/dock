#!/usr/bin/env bats

setup() {
	source "$BATS_TEST_DIRNAME/../../lib/string_utils.sh"
}

@test "round_with_trim handles typical cases" {
	result=$(round_with_trim "0" 2)
	[ "$result" = "0" ]

	result=$(round_with_trim "2" 2)
	[ "$result" = "2" ]

	result=$(round_with_trim "0.1" 2)
	[ "$result" = "0.1" ]

	result=$(round_with_trim "0.15" 2)
	[ "$result" = "0.15" ]

	result=$(round_with_trim "0.152" 2)
	[ "$result" = "0.15" ]

	result=$(round_with_trim "0.155" 2)
	[ "$result" = "0.16" ]

	result=$(round_with_trim "0.156" 2)
	[ "$result" = "0.16" ]

	result=$(round_with_trim "1.252" 2)
	[ "$result" = "1.25" ]

	result=$(round_with_trim "0.1000" 2)
	[ "$result" = "0.1" ]
}

@test "round_with_trim respects different precision" {
	result=$(round_with_trim "1.2345" 3)
	[ "$result" = "1.235" ]

	result=$(round_with_trim "1.2341" 3)
	[ "$result" = "1.234" ]

	result=$(round_with_trim "1.2" 0)
	[ "$result" = "1" ]
}

@test "round_with_trim handles leading decimals and negatives" {
	result=$(round_with_trim ".155" 2)
	[ "$result" = "0.16" ]

	result=$(round_with_trim "-0.155" 2)
	[ "$result" = "-0.16" ]

	result=$(round_with_trim "-0.152" 2)
	[ "$result" = "-0.15" ]
}

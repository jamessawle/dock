#!/usr/bin/env bats

setup() {
	export PATH="$BATS_TEST_DIRNAME/../bin:$PATH"
	export HOME="$BATS_TEST_TMPDIR/home"
	mkdir -p "$HOME/.config/dock" "$HOME/Applications" "$HOME/Library/Preferences"
	cp "$BATS_TEST_DIRNAME/../../dock" "$BATS_TEST_TMPDIR/dock"
	chmod +x "$BATS_TEST_TMPDIR/dock"
	cp -R "$BATS_TEST_DIRNAME/../../lib" "$BATS_TEST_TMPDIR/lib"
}

@test "--version prints version" {
	run "$BATS_TEST_TMPDIR/dock" --version
	[ "$status" -eq 0 ]
	[[ "$output" =~ ^dock[[:space:]]+[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

@test "--help prints usage" {
	run "$BATS_TEST_TMPDIR/dock" --help
	[ "$status" -eq 0 ]
	[[ "$output" =~ "Usage:" ]]
	[[ "$output" =~ "Commands:" ]]
}

@test "validate errors when no config found" {
	run "$BATS_TEST_TMPDIR/dock" validate
	[ "$status" -ne 0 ]
	[[ "$output" =~ "No config found for validate" ]]
}

@test "validate with minimal config works" {
	cat >"$BATS_TEST_TMPDIR/conf.yml" <<'YAML'
apps: []
downloads: off
YAML
	run "$BATS_TEST_TMPDIR/dock" --file "$BATS_TEST_TMPDIR/conf.yml" validate
	[ "$status" -eq 0 ]
	[[ "$output" =~ "Config:" ]]
	[[ "$output" =~ "Downloads: off" ]]
}

@test "reset --dry-run emits dockutil commands" {
	mkdir -p "$BATS_TEST_TMPDIR/apps/Chrome.app"
	cat >"$BATS_TEST_TMPDIR/conf.yml" <<YAML
apps:
  - "$BATS_TEST_TMPDIR/apps/Chrome.app"
downloads:
  preset: classic
  path: "$BATS_TEST_TMPDIR/Downloads"
  section: others
YAML
	run "$BATS_TEST_TMPDIR/dock" --dry-run --file "$BATS_TEST_TMPDIR/conf.yml" reset
	[ "$status" -eq 0 ]
	[[ "$output" =~ "\\[DRY-RUN\\] dockutil --remove all --no-restart" ]]
	[[ "$output" =~ "killall Dock" ]]
}

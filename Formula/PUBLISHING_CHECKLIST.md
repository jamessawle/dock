# Homebrew Formula Publishing Checklist

Use this checklist when publishing a new version of the `dock` formula.

The release process is **automated via GitHub Actions**, but this checklist helps ensure everything goes smoothly.

## Pre-Release

- [ ] All tests pass: `make ci`
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG updated (if applicable)
- [ ] Completions regenerated: `make completions`
- [ ] Git working directory is clean
- [ ] All changes committed and pushed to main branch

## Create Release (Automated)

- [ ] Create and push version tag:
  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

- [ ] **GitHub Actions will automatically**:
  - Run CI checks (lint, type-check, tests)
  - Build distribution packages
  - Create GitHub release with artifacts
  - Calculate SHA256 of release tarball
  - Update Formula/dock.rb with new version and SHA256
  - Push updated formula to homebrew-tap repository

- [ ] Monitor the release workflow:
  ```bash
  # Check workflow status on GitHub
  # https://github.com/jamessawle/dock/actions
  ```

- [ ] Verify the workflow completed successfully (all steps green)

## Verify Published Formula

Wait a few minutes for the workflow to complete, then:

- [ ] Check the homebrew-tap repository for the updated formula:
  ```bash
  # Visit: https://github.com/jamessawle/homebrew-tap/commits/main
  # Should see: "dock: update to version 1.0.0"
  ```

- [ ] Install from tap:
  ```bash
  brew install jamessawle/tap/dock
  ```

- [ ] Verify installation:
  ```bash
  dock --version  # Should show v1.0.0
  dock --help
  ```

- [ ] Test basic functionality:
  ```bash
  dock show
  echo "apps:\n  - Safari" > /tmp/test.yml
  dock validate --file /tmp/test.yml
  ```

- [ ] Verify completions installed:
  ```bash
  ls $(brew --prefix)/share/bash-completion/completions/dock
  ls $(brew --prefix)/share/zsh/site-functions/_dock
  ```

- [ ] Clean up:
  ```bash
  brew uninstall dock
  rm /tmp/test.yml
  ```

## Manual Release (If Automation Fails)

If the automated workflow fails, you can update the formula manually:

- [ ] Calculate SHA256:
  ```bash
  ./scripts/update-formula.sh 1.0.0
  ```

- [ ] Test locally:
  ```bash
  ./scripts/test-formula.sh
  ```

- [ ] Copy to tap repository:
  ```bash
  cp Formula/dock.rb /path/to/homebrew-tap/Formula/dock.rb
  cd /path/to/homebrew-tap
  git add Formula/dock.rb
  git commit -m "dock: update to version 1.0.0"
  git push
  ```

## Post-Release

- [ ] Update README if installation instructions changed
- [ ] Announce release (if applicable)
- [ ] Monitor GitHub issues for problems
- [ ] Check Homebrew analytics after a few days

## Troubleshooting

### Workflow Fails at "Checkout homebrew-tap repository"

- Verify `HOMEBREW_TAP_TOKEN` secret is set in repository settings
- Ensure the token has `repo` scope
- Check that the homebrew-tap repository exists

### Workflow Fails at "Calculate SHA256"

- Wait a few minutes and re-run the workflow (tarball may not be ready)
- Verify the release was created successfully
- Check that the tarball URL is accessible

### Formula Update Doesn't Appear in Tap

- Check the workflow logs for errors
- Verify git push succeeded in the workflow
- Check homebrew-tap repository for any conflicts

## Rollback Procedure

If issues are discovered after publishing:

1. **Quick fix**: Revert in the tap repository:
   ```bash
   cd /path/to/homebrew-tap
   git revert HEAD
   git push
   ```

2. **Proper fix**:
   - Fix the issue in the main repository
   - Create a new patch release (e.g., v1.0.1)
   - Push the new tag to trigger automated release
   - Follow this checklist again

## Notes

- The automated workflow requires `HOMEBREW_TAP_TOKEN` secret
- Formula updates happen within minutes of pushing a tag
- Keep the manual scripts for testing and emergency updates
- Test on a clean macOS installation when possible

class Dock < Formula
  desc "macOS Dock Manager (YAML-driven, dry-run friendly)"
  homepage "https://github.com/jamessawle/dock"
  url "https://github.com/jamessawle/dock/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "TO_BE_FILLED_BY_CI"
  license "MIT"

  depends_on "dockutil"
  depends_on :macos
  depends_on "yq"

  def install
    bin.install "dock"
  end

  test do
    assert_match(/\A[dD]ock \d+\.\d+\.\d+/, shell_output("#{bin}/dock --version"))
  end
end

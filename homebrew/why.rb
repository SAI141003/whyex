# Homebrew formula for whyex.
#
# Usage (after publishing the tap):
#   brew tap SAI141003/whyex
#   brew install whyex
#
# IMPORTANT: Replace sha256 before publishing a release:
#   curl -fsSL https://github.com/SAI141003/whyex/archive/refs/tags/v0.1.0.tar.gz -o whyex-0.1.0.tar.gz
#   shasum -a 256 whyex-0.1.0.tar.gz
class Whyex < Formula
  desc "Explain terminal errors offline and show how to fix them"
  homepage "https://github.com/SAI141003/whyex"
  url "https://github.com/SAI141003/whyex/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_RELEASE_SHA256"
  license "MIT"
  depends_on "python@3.12"

  def install
    system "pip3", "install", *std_pip_args, "."
  end

  test do
    assert_match "whyex", shell_output("#{bin}/whyex --version")
  end
end

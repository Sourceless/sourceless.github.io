{
  description = "sourceless.org - Jekyll site";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        ruby = pkgs.ruby_3_3;
        # Used by tools/generate_og_images.py to render per-post OG cards.
        python = pkgs.python3.withPackages (ps: [ ps.numpy ps.pillow ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            ruby
            python
            pkgs.bundler
            pkgs.pkg-config
            pkgs.libffi
            pkgs.libxml2
            pkgs.libxslt
            pkgs.zlib
            pkgs.libyaml
          ];

          shellHook = ''
            export GEM_HOME="$PWD/.gem"
            export PATH="$GEM_HOME/bin:$PATH"
            bundle install --quiet 2>/dev/null
            echo "sourceless.org dev shell"
            echo "Run 'bundle exec jekyll serve' to start the dev server"
          '';
        };
      });
}

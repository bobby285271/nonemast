{
  description = "Tool for reviewing GNOME update Nixpkgs PRs";

  inputs = {
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };

    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      flake-compat,
      nixpkgs,
      utils,
    }:
    utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            self.overlay
          ];
        };
      in
      {
        devShells = {
          default = pkgs.mkShell {
            nativeBuildInputs =
              pkgs.nonemast.nativeBuildInputs
              ++ (with pkgs; [
                python3.pkgs.black
              ]);

            inherit (pkgs.nonemast) buildInputs propagatedBuildInputs checkInputs;
          };
        };

        packages = rec {
          nonemast = pkgs.nonemast;
          default = nonemast;
        };

        apps = {
          default = utils.lib.mkApp {
            drv = self.packages.${system}.nonemast;
          };
        };
      }
    )
    // {
      overlay = final: prev: {
        nonemast = final.stdenv.mkDerivation rec {
          pname = "nonemast";
          version = "0.0.0";

          src = final.nix-gitignore.gitignoreSource [ ] ./.;

          nativeBuildInputs = with final; [
            meson
            ninja
            pkg-config
            gobject-introspection
            desktop-file-utils
            gtk4 # for gtk4-update-icon-cache
            wrapGAppsHook4
            python3.pkgs.wrapPython
          ];

          buildInputs = with final; [
            gtk4
            libgit2-glib
            libadwaita
          ];

          propagatedBuildInputs = with final.python3.pkgs; [
            pygobject3
            linkify-it-py
          ];

          checkInputs = with final.python3.pkgs; [
            final.git
            pytest
          ];

          doCheck = true;

          preCheck = ''
            buildPythonPath "$out $propagatedBuildInputs"
            patchPythonScript ../tests/test_autosquashing.py

            export NONEMAST_NO_GSCHEMA=1
          '';

          preFixup = ''
            gappsWrapperArgs+=(
              --prefix PYTHONPATH : "$program_PYTHONPATH"
              --prefix PATH : "${
                final.lib.makeBinPath [
                  final.gnome-text-editor
                  final.zenity
                ]
              }"
            )
          '';
        };
      };
    };
}

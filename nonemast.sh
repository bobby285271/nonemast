#!/usr/bin/env bash

nix run /home/bobby285271/nonemast --override-input nixpkgs \
  'git+file:///home/bobby285271/nixpkgs?ref=nixos-unstable' . -- "$@"

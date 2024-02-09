## Version 0.9.1 (unstable) - next

Upstream base: https://github.com/jtojnar/nonemast/commit/3aaa6d4e16555fe10df37d72aac10ac8b541e63d

Packaging changes:

- The Nix packaging now ensures gnome-text-editor in PATH.

Other changes:

- The desktop file is removed as I don't use it.
- Sidebar width is now hardcoded. For now responsive is not a focus in this fork.

## Version 0.9.0 (unstable) - 2024-02-09

Upstream base: https://github.com/jtojnar/nonemast/commit/3aaa6d4e16555fe10df37d72aac10ac8b541e63d

Breaking changes:

- Nixpkgs path is not accepted as commandline arg anymore. You can configure this in the Preferences page.
- It is now required to pass Nixpkgs base commit (or reference) as commandline arg.
  For example, by running `nix run /path/to/nonemast staging` you compare the current checkout with the `staging` branch.
- The `Mark as reviewed` button is removed as I prefer `amend!` workflow. You will need to edit the commit message yourself.

Packaging changes:

- This is ported to `AdwNavigationSplitView`, which means you will need libadwaita 1.4.0 or later.

Other changes:

- Support viewing commits on github.com using a browser.
- Prefer direct comparison on github.com.

### Packaging changes

- The Nix packaging ensures `gnome-text-editor` in `PATH`.
- `zenity` is needed for shell scripts integration.
- Ported to `AdwNavigationSplitView`, `AdwAboutDialog` (require libadwaita 1.6.0 or later).

### Breaking changes

- Nixpkgs path is not accepted as commandline arg anymore.
- It is now required to pass Nixpkgs base commit (or reference) as commandline arg.
- The `Mark as reviewed` button is removed as I prefer `amend!` workflow.
- The desktop file is removed as I don't use it.

### Other changes

- Support viewing commits on github.com using a browser.
- Prefer direct comparison on github.com.
- Support update arrow style in commit message subject (GNOME workflow only).
- Support regenerate commits (Cinnamon workflow only).
- Generate Xfce GitLab diff URL if the commit is likely related to Xfce updates.
- Convert Xfce GitLab URL to GitHub mirror URL.
- Sidebar width is now hardcoded. For now responsive is not a focus in this fork.

This fork includes various changes:

- Hardcode various paths, including Nixpkgs dir.
- Prefer direct comparison on github.com.
- Support custom base commit.
- Support viewing commits on github.com.

Some changes are really opinionated and are not for others,
you shouldn't use this fork if you are not bobby285271.

Original README:

------

# Not Nearly Enough Masking Tape

This is a tool for reviewing large Nixpkgs pull requests such as GNOME updates. All review information are tracked in commit messages.

## How to use?

If you use [Nix flakes](https://nixos.wiki/wiki/Flakes), you can just run `nix run github:jtojnar/nonemast` in your local Nixpkgs checkout.

With stable Nix, you will need to use `nix-shell -I 'nonemast=https://github.com/jtojnar/nonemast/archive/main.tar.gz' -p '((import <nonemast>).packages.${builtins.currentSystem}.nonemast)' --run nonemast` instead.

![Main view of GNOME 43 update](data/screenshot.png)

## Why is this needed?

Nixpkgs GNOME maintainers have the following workflow: When an alpha of a new GNOME release is published, they use `update.nix` script to automatically bump all GNOME packages in Nixpkgs on the `gnome` branch. After that, they walk through the commits, reading the release notes and modifying the package expressions as necessary. To have clean Git history where each commit points to a non-broken tree, maintainers push fixup/squash commits. Those are then periodically integrated by [rebasing with auto-squashing](https://git-scm.com/docs/git-rebase#Documentation/git-rebase.txt---autosquash).

To keep track of which updates were already reviewed without modifying commits under other maintainers’ feet, the branch is append only most of the time. The review is acknowledged by creating an empty squash commit with `git commit --squash «commit-id» --allow-empty -m "Changelog-Reviewed-By: $USER"`.

But that would make it easy to miss some review commit far from the original commit in the Git log. The Git’s [notes feature](https://git-scm.com/docs/git-notes) offers a similar annotation feature but it is even more obscure than rebase, harder to use with multiple users due to the need to deal with merges, and rebasing disconnects the notes from commits.

This tool allows maintainers to preview Git log as if it was auto-squashed and additionally highlights the reviewed commits visually.

## How to develop nonemast?

We use [Meson](https://mesonbuild.com/) build system so you can configure, build, test and run it as usual:

```shell
meson setup _build
meson compile -C _build
meson test -C _build
meson devenv -C _build/ nonemast /path/to/nixpkgs
```

The code is formatted with [Black](https://github.com/psf/black), you can run `meson compile -C _build lint-fix` to enforce the formatting.

We include [Nix](https://nixos.org) developement environment so you can just run `nix-shell` in the project directory (or `nix develop` with flakes) to enter a shell with all the dependencies installed.

## License

The code is licensed under [MIT](LICENSE.md).

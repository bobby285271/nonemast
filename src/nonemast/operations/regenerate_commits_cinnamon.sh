#!/usr/bin/env bash

# For Cinnamon workflow only, used in Cinnamon 6.0
# https://github.com/NixOS/nixpkgs/pull/268515

echo_yellow() {
    # $1: text to echo
    echo -e "\033[0;33m${1}\033[0m"
}

nix_eval_wip() {
    # $1: expression
    # ret: result
    ret_nix_eval_wip=$(NIX_PATH=nixpkgs=. \
        nix-instantiate --expr "with import <nixpkgs> { }; ${1}" --eval | \
        sed 's/^"//' | sed 's/"$//')
}

nix_eval_checkout() {
    # $1: expression
    # $2: checkout
    # ret: result
    ret_nix_eval_checkout=$(nix eval \
        "git+file://$(pwd)?ref=${2}#${1}" --raw)
}

is_running_in_nixpkgs() {
    # ret: 0 for yes, else no
    nix_eval_wip "cinnamon.cinnamon-common.meta.homepage"
    echo "${ret_nix_eval_wip}" | grep "https://github.com/linuxmint/cinnamon"
    ret_is_running_in_nixpkgs=${?}
}

is_worktree_clean() {
    # ret: 0 for yes, 1 for no
    if [ -z "$(git status --porcelain)" ]; then 
        echo "Worktree clean"
        ret_is_worktree_clean=0
    else
        git status
        echo "Has uncommitted changes, please confirm"
        read
        ret_is_worktree_clean=1
    fi
}

git_reset() {
    # $1: commit reset to, no --hard
    echo "You are currently on:"
    git rev-parse HEAD
    git reset $1
}

get_cinnamon_pkgs_attr() {
    if [ -z "${CANNOT_VISIT_GUC}" ]; then
        local url="https://raw.githubusercontent.com/bobby285271/what-changed/master/data/003-cinnamon.json"
    else 
        local url="https://raw.fgit.cf/bobby285271/what-changed/master/data/003-cinnamon.json"
    fi
    echo "Fetch cinnamon info: $url"
    # This works f**king well since I maintain this
    ret_get_cinnamon_pkgs_attr=$(curl $url | \
        grep '"attr_path": "' | sed 's/ //g' | sed 's/"attr_path":"//g' | sed 's/"$//g')
}

commit_pkgs_change() {
    # $1: pkgs attr
    # $2: base commit
    echo_yellow "!!!!! Processing $1"


    nix_eval_checkout "${1}.version" "$2"
    local old_version=$ret_nix_eval_checkout

    nix_eval_wip "${1}.version"
    local new_version=$ret_nix_eval_wip

    nix_eval_checkout "${1}.src.rev" "$2"
    local old_rev=$ret_nix_eval_checkout

    nix_eval_wip "${1}.src.rev"
    local new_rev=$ret_nix_eval_wip


    if [ "$new_rev" == "$old_rev" ]; then
        return
    fi

    nix_eval_wip "${1}.src.meta.homepage"
    local diffurl="$ret_nix_eval_wip/compare/${old_rev}...${new_rev}"

    nix_eval_wip "${1}.meta.position"
    local dir_to_add=$(dirname $(echo $ret_nix_eval_wip | cut -d : -f 1))

    echo_yellow "### Dir to add: $dir_to_add"
    git add $dir_to_add
    git commit -m "${1}: ${old_version} -> ${new_version}" -m "${diffurl}"
}

main() {
    zenity --info --title="Still WIP" --text="This does not actually do stuff yet"

    echo "$NONEMAST_NIXPKGS_BASE_COMMIT"

    nonemast_nixpkgs_path=$(gsettings get cz.ogion.Nonemast nixpkgs-path | sed 's/^.\(.*\).$/\1/')
    cd $nonemast_nixpkgs_path

    pwd

    echo_yellow "#################### Check ####################"
    exit 1

    if [ "$#" != 0 ]; then
        echo "Expect no extra arg" && exit 1
    fi

    is_running_in_nixpkgs
    if [ "$ret_is_running_in_nixpkgs" != 0 ]; then
        echo "You must run in nixpkgs root" && exit 1
    fi

    is_worktree_clean

    echo_yellow "#################### Reset ####################"
    git_reset "$NONEMAST_NIXPKGS_BASE_COMMIT"

    echo_yellow "#################### Get cinnamon pkglist ####################"
    get_cinnamon_pkgs_attr

    echo_yellow "#################### Commit ####################"
    for attr in $(echo $ret_get_cinnamon_pkgs_attr); do
        commit_pkgs_change "$attr" "$NONEMAST_NIXPKGS_BASE_COMMIT"
    done
}

main "$@"

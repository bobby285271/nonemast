#!/usr/bin/env bash

check_existing_script() {
    # ret: number of process
    ret_check_existing_script=$(pgrep -fa "operations/update_arrow_style_gnome.sh" | grep -v $$ | wc -l)
}

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
    nix_eval_wip "cinnamon-common.meta.homepage"
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
        echo "Has uncommitted changes"
        # read
        ret_is_worktree_clean=1
    fi
}

main() {
    check_existing_script

    echo $ret_check_existing_script
    if [ "$ret_check_existing_script" != "1" ]; then
        zenity --info --title="Oops" --text="Another arrow style update program is running."
        exit 1
    fi

    zenity --info --title="Still WIP" --text="Please make sure you have save your work."

    echo "Base commit: $NONEMAST_NIXPKGS_BASE_COMMIT"

    nonemast_nixpkgs_path=$(gsettings get cz.ogion.Nonemast nixpkgs-path | sed 's/^.\(.*\).$/\1/')
    cd $nonemast_nixpkgs_path

    echo -n "Nixpkgs path: "; pwd

    echo_yellow "#################### Check ####################"

    if [ "$#" != 0 ]; then
        echo "Expect no extra arg" && exit 1
    fi

    is_running_in_nixpkgs
    if [ "$ret_is_running_in_nixpkgs" != 0 ]; then
        echo "You must run in nixpkgs root" && exit 1
    fi

    is_worktree_clean

    echo_yellow "#################### Rebase ####################"
    export GIT_EDITOR="sed 's/->/→/g' -i"
    export GIT_SEQUENCE_EDITOR="sed 's/^pick /reword /' -i"
    git rebase $NONEMAST_NIXPKGS_BASE_COMMIT -i

    echo_yellow "#################### Done ####################"
    zenity --info --title="Done" --text="You might want to restart nonemast"
}

main "$@"

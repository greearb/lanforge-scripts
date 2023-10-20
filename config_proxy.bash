#!/bin/bash
# please read the below:
# https://unix.stackexchange.com/questions/212894/whats-the-right-format-for-the-http-proxy-environment-variable-caps-or-no-ca
# https://about.gitlab.com/blog/2021/01/27/we-need-to-talk-no-proxy/
# For git proxies:
# https://gist.github.com/evantoli/f8c23a37eb3558ab8765

if [[ -z "${1:-}" ]]; then
  echo "Temporarily configure your proxy environment:"
  echo "  * Establish a shell envronment with a proxy:"
  echo "      $0 proxy.acme.com:3128"
  echo "    Exit the shell to go back to the previous environment."
  echo "  * Display proxy environment variables:"
  echo "      $0 print"
  echo "  * Create a shell environment without proxy variables:"
  echo "      $0 blank"
  exit
fi
qq='"'
q="'"
#set -veu
# never proxy local addresses
eth0_ip=$(ip ro sh | perl -ne '/default .*? dev (\S+)/ && print "$1"' | xargs ip -br a sho | awk '{print $3}')
eth0_ip="${eth0_ip%/*}"
no_proxy="127.0.0.1,127.0.0.1:8080,*.localdomain,.localdomain,localhost,$eth0_ip,$eth0_ip:8080"
#echo "$no_proxy"

case "$1" in
  print)
    echo "Proxies:"
    printenv | grep -i proxy
    echo "Your current git proxies:"
    git config --global --get-regexp http.* ||:
    exit 0
    ;;
  blank)
    echo "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY PROXY_ALL" > $HOME/.blank_rc
    echo "export no_proxy=${q}$no_proxy${q} NO_PROXY=${q}$no_proxy${q}" >> $HOME/.blank_rc
    echo "export PS1=${qq}[no proxies] \u@\$(hostname) \$ ${qq}" >> $HOME/.blank_rc
    bash --rcfile $HOME/.blank_rc -i
    ;;
  *)
    echo "Exporting proxy environment variables set to [$1]"
    echo "export http_proxy=${q}$1${q} https_proxy=${q}$1${q} HTTP_PROXY=${q}$1${q} HTTPS_PROXY=${q}$1${q} ALL_PROXY=${q}$1${q} PROXY_ALL=${q}$1${q}" > $HOME/.proxy_rc
    echo "export no_proxy=${q}$no_proxy${q} NO_PROXY=${q}$no_proxy${q}" >> $HOME/.proxy_rc
    echo "Not proxying [$no_proxy]"
    echo "You might want to configure a git proxy, example:"
    echo "  git config --global http.proxy $1"
    echo "  git config --global http.https://domain.com.proxy $1"
    echo "Your current git proxies:"
    git config --global --get-regexp http.* ||:

    printenv | grep PS
    echo "export PS1=${qq}[+proxy] \u@\$(hostname) \$ ${qq}" >> $HOME/.proxy_rc
    bash --rcfile $HOME/.proxy_rc -i
    ;;
esac

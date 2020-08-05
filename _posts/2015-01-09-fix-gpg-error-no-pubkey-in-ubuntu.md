---
title: How to fix GPG error NO_PUBKEY in Ubuntu
category: linux
---

I have a VPS for testing/developing, when I try Ubuntu 14.04 template for openvz, I got GPG error NO_PUBKEY when I run apt-get update or install whatever package. I guess because the Ubuntu 14.04 openvz template the provider use is missing public key for Ubuntu 14.04 trusty’s repository. I tried y-ppa-manager program to import all missing GPG keys but no luck.
<!--more-->

``` bash
GPG error: http://archive.canonical.com trusty Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 40976EAF437D05B5 NO_PUBKEY 3B4FE6ACC0B21F32
W: GPG error: http://security.ubuntu.com trusty-security Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 40976EAF437D05B5 NO_PUBKEY 3B4FE6ACC0B21F32
W: GPG error: http://archive.ubuntu.com trusty Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 40976EAF437D05B5 NO_PUBKEY 3B4FE6ACC0B21F32
W: GPG error: http://archive.ubuntu.com trusty-updates Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 40976EAF437D05B5 NO_PUBKEY 3B4FE6ACC0B21F32
```

I found a way to solve GPG error NO_PUBKEY error, all we need to do is to download the missing key using the hexadecimal numbers given in the error with apt-key (APT key management utility) command. In my case the hexadecimal number is 40976EAF437D05B5 and 3B4FE6ACC0B21F32. After running apt-key to download the missing PUBKEY, packages from that repositories will be considered trusted and you won’t NO_PUBKEY again.

So let’s do it (your missing PUBKEY may be different so use the hexadecimal number given from your error)

``` bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 40976EAF437D05B5
```

and the output

``` bash
Executing: gpg --ignore-time-conflict --no-options --no-default-keyring --homedir /tmp/tmp.RjvPYT2oIP --no-auto-check-trustdb --trust-model always --keyring /etc/apt/trusted.gpg --primary-keyring /etc/apt/trusted.gpg --keyserver keyserver.ubuntu.com --recv-keys 40976EAF437D05B5
gpg: requesting key 437D05B5 from hkp server keyserver.ubuntu.com
gpg: key 437D05B5: public key "Ubuntu Archive Automatic Signing Key " imported
gpg: Total number processed: 1
gpg:               imported: 1
```

``` bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
```

and the output

``` bash
Executing: gpg --ignore-time-conflict --no-options --no-default-keyring --homedir /tmp/tmp.1LP43k8aGL --no-auto-check-trustdb --trust-model always --keyring /etc/apt/trusted.gpg --primary-keyring /etc/apt/trusted.gpg --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
gpg: requesting key C0B21F32 from hkp server keyserver.ubuntu.com
gpg: key C0B21F32: public key "Ubuntu Archive Automatic Signing Key (2012) " imported
gpg: Total number processed: 1
gpg:               imported: 1  (RSA: 1)
```

Now run apt-get update again or install any package, you should not see any error asking for missing PUBKEY.

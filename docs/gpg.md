# GPG Cheat Sheet

## Create a key
`gpg --expert --full-generate-key`
* RSA (set your own capabilities)
* Set to Certify only.
* 4096
* 2020-01-01

`gpg --expert --edit-key <userid>`
* `addkey` (Create 3, one for sign, encrypt, authenticate)
* `adduid`
* `save`

## Backup key
* `mv ~/.gnupg/secring.gpg ~/.backup/gpg/`
* `mv ~/.gnupg/pubring.gpg ~/.backup/gpg/`
* `gpg -a --export-secret-key <userid> > secret_key.gpg`
* `gpg -a --export-secret-subkeys <userid> > secret_subkeys.gpg`
* `gpg --delete-secret-keys <userid>`
* `gpg --import secret_subkeys.gpg`
* `gpg --list-secret-keys`
* `rm secret_subkeys.gpg`

## Revoke cert
* `gpg -a --output revoke.asc --gen-revoke '<fingerprint>'`

## Import/Export public key
* `gpg --import public.key`
* `gpg --output public.key --armor --export <userid>`

## Import/Export private key
* `gpg --export-secret-keys --armor <userid> > privkey.asc`
* `gpg --import privkey.asc`

## Edit keys
* `gpg --edit-key <userid>`

## List (secret) keys
* `gpg --list-keys`
* `gpg --list-secret-keys`

## Encrypt/Decrypt
* `gpg --recipient user-id --encrypt doc`
* `gpg --output doc --decrypt doc.gpg`

or...

* `gpg -c --s2k-cipher-algo AES256 --s2k-digest-algo SHA512 --s2k-count 65536 doc`
* `gpg --output doc --decrypt doc.gpg`

## Signing
* `gpg --output doc.sig --sign doc`
* `gpg --output doc.sig --clearsign doc`
* `gpg --output doc.sig --detach-sig doc`

## Verify
* `gpg --verify doc.sig`
* `gpg --verify archlinux-version.iso.sig`
* `gpg --verify archlinux-version.iso.sig /path/to/archlinux-version.iso`
* `gpg --with-fingerprint <keyfile>`

## Send keys
* `gpg --send-keys <userid>`
* `gpg --refresh-keys`

## Get keys
* `gpg --recv-key '<fingerprint>'`
* `gpg --fingerprint '<fingerprint>'`

## Sign key
* `gpg --lsign-key '<fingerprint>'`

or...

* `gpg --sign-key '<fingerprint>'`
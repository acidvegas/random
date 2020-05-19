# GPG Cheat Sheet

## Create a key
* `gpg --expert --full-generate-key`
	* RSA (set your own capabilities)
	* Set to Certify only
	* 4096
	* 2020-01-01
* `gpg --expert --edit-key <userid>`
	* `addkey` (Create 3, one for sign, encrypt, authenticate)
	* `addphoto` *(240x288)*
	* `save`
	* `quit`
* `gpg -a --output revoke.asc --gen-revoke '<fingerprint>'`

## Backup key
* `gpg -a --export-secret-key     <userid> > secret_key.gpg`
* `gpg -a --export-secret-subkeys <userid> > secret_subkeys.gpg`
* `gpg --delete-secret-keys <userid>`
* `gpg --import secret_subkeys.gpg`
* `gpg --list-secret-keys`
* `gpg --edit-key <KEYID>` *(type `trust` and press `5`)*

## Import/Export public key
* `gpg --import public.key`
* `gpg --output public.key --armor --export <userid>`
* `gpg --export-secret-keys --armor <userid> > privkey.asc`

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
* `gpg --verify example.sig`
* `gpg --verify example.sig /path/to/example.iso`
* `gpg --with-fingerprint <keyfile>`

## Send keys
* `gpg --keyserver <keyserver> --send-keys <user-id>`
* `gpg --recv-key '<fingerprint> && gpg --fingerprint '<fingerprint>'`
* `gpg --search-keys '<userid>'`

## Sign key
* `gpg --lsign-key '<fingerprint>'`

or...

* `gpg --sign-key '<fingerprint>'`
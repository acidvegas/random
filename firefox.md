## Add-ons
- [uBlock Origin](https://addons.mozilla.org/en-us/firefox/addon/ublock-origin/)
- [NoScript Security Suite](https://addons.mozilla.org/en-us/firefox/addon/noscript/)
- [HTTPS Everywhere](https://www.eff.org/Https-everywhere)

### Disable Animations
| Preference Name | Value |
| --- | --- |
| browser.fullscreen.animate | False |
| browser.tabs.animate | False |
| image.animation_mode | once |

### Disable Autocomplete / Autofill / Formfill
| Preference Name | Value |
| --- | --- |
| browser.formfill.enable | False |
| browser.urlbar.autoFill | False |
| browser.urlbar.autoFill.typed | False |
| browser.urlbar.autocomplete.enabled | False |
| signon.autofillForms | False | 

### Disable Device Tracking
| Preference Name | Value |
| --- | --- |
| camera.control.face_detection.enabled | False |
| camera.control.autofocus_moving_callback.enabled | False |
| device.sensors.enabled | False |

### Disable Disk Cache
| Preference Name | Value |
| --- | --- |
| browser.cache.check_doc_frequency | 1 |
| browser.cache.disk.capacity | 0 |
| browser.cache.disk.enable | False |
| browser.cache.disk_cache_ssl | False |
| browser.cache.offline.capacity | 0 |
| browser.cache.offline.enable | False |

### Disable Encrypted Media Extensions (DRM)
| Preference Name | Value |
| --- | --- |
| media.eme.enabled | False |
| media.gmp-eme-adobe.enabled | False |

### Disable Experiments
| Preference Name | Value |
| --- | --- |
| experiments.enabled | false |
| experiments.manifest.uri | (blank) |
| experiments.supported | False |
| experiments.activeExperiment | False |
| network.allow-experiments | False |

### Disable Geo Location
| Preference Name | Value |
| --- | --- | --- |
| browser.search.geoip.url | (blank) |
| geo.enabled | False |
| geo.wifi.uri | (blank) |

### Disable Ping
| Preference Name | Value |
| --- | --- | --- |
| browser.send_pings | False |
| browser.send_pings.require_same_host | True |

### Disable Popups
| Preference Name | Value |
| --- | --- | --- |
| browser.link.open_newwindow | 3 |
| browser.link.open_newwindow.restriction | 0 |
| dom.disable_open_during_load | True |
| dom.disable_window_* | True |
| dom.popup_maximum | 1 |
| privacy.popups.policy | 2 |

### Disable Prefetch
| Preference Name | Value |
| --- | --- | --- |
| network.dns.disablePrefetch | True |
| network.http.speculative-parallel-limit | 0 |
| network.prefetch-next | False |

### Disable Referer
| Preference Name | Value |
| --- | --- | --- |
| network.http.referer.spoofSource | True |
| network.http.referer.XOriginPolicy | 0 |
| network.http.sendRefererHeader | 0 |
| network.http.sendSecureXSiteReferrer |

### Disable Safe Browsing
| Preference Name | Value |
| --- | --- |
| browser.safebrowsing.downloads.enabled | False |
| browser.safebrowsing.downloads.remote.enabled | False |
| browser.safebrowsing.enabled | False |
| browser.safebrowsing.malware.enabled | False |
| browser.safebrowsing.reportMalwareMistakeURL | (blank) |
| browser.safebrowsing.reportPhishMistakeURL | (blank) |
| browser.search.geoSpecificDefaults.url | (blank) |

### Disable Session Store
| Preference Name | Value |
| --- | --- |
| browser.sessionstore.enabled | False |
| browser.sessionstore.postdata | 0 |
| browser.sessionstore.privacy_level | 2 |
| browser.sessionstore.privacy_level_deferred | 2 |
| browser.sessionstore.resume_from_crash | False | Disable session saving. |

### Disable Slow Startup
| Preference Name | Value |
| --- | --- |
| browser.slowStartup.notificationDisabled | True |
| browser.slowStartup.maxSamples | 0 |
| browser.slowStartup.samples | 0 |
| browser.rights.3.shown | True |
| browser.startup.homepage_override.mstone | ignore |
| startup.homepage_welcome_url | (blank) |
| startup.homepage_override_url | (blank) |
| browser.feeds.showFirstRunUI | False |
| browser.shell.checkDefaultBrowser | False |

### Disable Social Media Integration
| Preference Name | Value |
| --- | --- |
| social.directories | (blank) |
| social.remote-install.enabled | False |
| social.share.activationPanelEnabled | False |
| social.shareDirectory | (blank) |
| social.toast-notifications.enabled | False |
| social.whitelist | (blank) |

### Disable Statistics
| Preference Name | Value |
| --- | --- |
| beacon.enabled | False |
| datareporting.healthreport.documentServerURI | (blank) |
| datareporting.healthreport.service.enabled | False | 
| datareporting.healthreport.uploadEnabled | False |
| datareporting.policy.dataSubmissionEnabled | False |
| toolkit.telemetry.archive.enabled | False |
| toolkit.telemetry.enabled | False |
| toolkit.telemetry.server | (blank) |
| toolkit.telemetry.unified | False |

### Disable Unused Features (This may break a some websites.)
| Preference Name | Value |
| --- | --- |
| browser.pocket.enabled | False |
| dom.storage.enabled | False |
| network.websocket.enabled | False |
| webgl.disabled | True |

### Disable WebRTC Leak
| Preference Name | Value |
| --- | --- |
| media.peerconnection.enabled | False |
| media.peerconnection.identity.timeout | 1 |
| media.peerconnection.turn.disable | True |
| media.peerconnection.use_document_iceservers | False |
| media.video_stats.enabled | False |
| loop.enable | False |

___

### Enable DoNotTrack (DNT) Header
| Preference Name | Value |
| --- | --- |
| privacy.donottrackheader.enabled | True |
| privacy.donottrackheader.value | 1 |
| privacy.trackingprotection.enabled |

### Enable Memory Cache
| Preference Name | Value |
| --- | --- |
| browser.cache.memory.enable | True |
| browser.cache.memory.capacity | -1 |

### Enable DNS Cache (Disable if you use a local DNS caching server.)
| Preference Name | Value |
| --- | --- |
| network.dnsCacheEntries | 100 |
| network.dnsCacheExpiration | 60 |

___

### Cookie Preferences
| Preference Name | Value |
| --- | --- |
| network.cookie.cookieBehavior | 1 |
| network.cookie.lifetimePolicy | 2 |

### Cryptography Hardening (Note: This may break a LOT of websites.)
| Preference Name | Value |
| --- | --- |
| security.OCSP.enabled | 1 | 
| security.OCSP.require | True |
| security.ssl.require_safe_negotiation | True |
| security.ssl.treat_unsafe_negotiation_as_broken | True |
| security.ssl3.ecdhe_ecdsa_rc4_128_sha | False |
| security.ssl3.ecdhe_rsa_rc4_128_sha | False |
| security.ssl3.rsa_aes_256_sha | False |
| security.ssl3.rsa_des_ede3_sha | alse |
| security.ssl3.rsa_rc4_128_md5 | False |
| security.ssl3.rsa_rc4_128_sha | False |
| security.ssl3.rsa_seed_sha | True |
| security.tls.insecure_fallback_hosts.use_static_list | False |
| security.tls.unrestricted_rc4_fallback | False |
| security.tls.version.min | 3 |

### Plugin Preferences
| Preference Name | Value | Description |
| --- | --- | --- |
| pdfjs.disabled | True | Disable pdf reader. |
| plugin.scan.plid.all | False | Disable scanning plugin folders. |
| plugin.state.flash | 1 | Click to load flash objects. |
| plugin.state.java | 0 | Disable java plugin. |
| security.enable_java | False | Disable java plugin. |

___

### Other
| Preference Name | Value | Description |
| --- | --- | --- |
| breakpad.reportURL | (blank) | Disable crash reports. |
| browser.chrome.toolbar_tips | False | Disable browser hover tool tips. |
| browser.sessionhistory.max_entries | 10 | Maximum number of websites to remember when you hit BACK. |
| browser.startup.homepage | about:blank | - |
| browser.startup.page | 0 | - |
| browser.urlbar.maxRichResults | -1 | Disable awesome bar suggestions. |
| browser.zoom.siteSpecific | False | Disable remembering site-specific zoom preferences. |
| dom.allow_scripts_to_close_windows | False | Disable scripts that close windows. |
| dom.battery.enabled | False | Disable battery access. |
| dom.event.clipboardevents.enabled | False | Disable clipboard access. (This may disable you from copying or pasting on some websites.) |
| dom.event.contextmenu.enabled | False | Disable context menu access. |
| network.proxy.socks_remote_dns | True | Enable this if you are using Tor or a proxy. |
| places.frecency.unvisitedBookmarkBonus | 0 | Disable bookmarks in the awesome bar. |
| places.history.enabled | False | Disable history |
| privacy.clearOnShutdown.* | True | - |
| privacy.cpd.* | True | Automatically checked items in clear private data prompt. |
| privacy.sanitize.promptOnSanitize | False | Disable prompt before sanitizing browser data. |
| privacy.sanitize.sanitizeOnShutdown | True | Sanitize browser data on shutdown. |
| signon.rememberSignons | False | Disable remembering passwords. |
| security.ask_for_password | 0 | Disable asking for password. |
| security.dialog_enable_delay | 0 | Disable the delay when installing new extensions. |

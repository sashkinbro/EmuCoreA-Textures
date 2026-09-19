# PSP link-only audit

This ledger records why the current external entries remain direct links. A
public GitHub repository or a downloadable ZIP is not, by itself, permission
to mirror the archive. A pack is promoted to the `texture-catalog` release
only when its author or license grants redistribution and the archive can be
installed as a standalone PPSSPP pack.

| Catalog entry | Source evidence checked | Result |
| --- | --- | --- |
| GTA Liberty City Stories / GTA Vice City Stories | [ItzAntonis2012/modernizepspgames README](https://github.com/ItzAntonis2012/modernizepspgames) gives combined credits for several authors but no redistribution license or mirror permission. | Link-only; preserve the author's release URL. |
| Manhunt 2 | [santiago046/ppsspp-mh2-texture-pack README](https://github.com/santiago046/ppsspp-mh2-texture-pack#license-and-re-upload) explicitly prohibits re-uploading the pack. It permits sharing only files changed or added by a user, with instructions to install them over the original. | Link-only; full ZIP mirror prohibited. |
| WipEout Pure | [reTokyo/WipEout-Pure-HD-Texture-Pack](https://github.com/reTokyo/WipEout-Pure-HD-Texture-Pack) contains copyright and trademark notices but no redistribution license or author permission. | Link-only. |
| Peggle | [sinceohsix/PeggleHD](https://github.com/sinceohsix/PeggleHD) has no pack redistribution license; the game and trademark rights remain with Electronic Arts. | Link-only. |
| Fate/Extra | [Ezehokadrim/fate-extra-texturepack](https://github.com/Ezehokadrim/fate-extra-texturepack) requests author credit and reserves original game rights, but grants no pack redistribution license. | Link-only. |
| Persona 2: Innocent Sin French patch | [chenetulipe/P2-FR-IS-PSP](https://github.com/chenetulipe/P2-FR-IS-PSP) identifies CC BY-NC-SA 4.0 for the patch, but the ZIP is an overlay with no `textures.ini` and requires a separately credited base pack. It is not a standalone pack that the app can safely install. | Keep as external link until a standalone, valid package and complete attribution chain are available. |
| Fate/EXTRA Japanese font add-on | [SIEBEN5106/Fate-EXTRA-Japanese-HD-Font](https://github.com/SIEBEN5106/Fate-EXTRA-Japanese-HD-Font) licenses referenced fonts separately under SIL OFL, but gives no redistribution license for the texture add-on itself and requires another pack. | Link-only. |
| Sword Art Online: Infinity Moment | [Saramagrean/SAO-IM-HD-Remake-Project](https://github.com/Saramagrean/SAO-IM-HD-Remake-Project) contains installation and compatibility information but no redistribution license or mirror permission. | Link-only. |
| Metal Gear Solid: Peace Walker | [AkiraJkr/Metal-Gear-Solid-Peace-Walker-HD-Textures](https://github.com/AkiraJkr/Metal-Gear-Solid-Peace-Walker-HD-Textures) identifies the source author and Konami/Kojima credits but no pack redistribution license. | Link-only. |
| Test Drive Unlimited | [MiyamuraShiro/Test-Drive-Unlimited-Texture-PSP](https://github.com/MiyamuraShiro/Test-Drive-Unlimited-Texture-PSP) identifies the target serial and contributors but provides no redistribution license or mirror permission. | Link-only. |

The catalog still records each entry's exact source URL, author credits,
serials, archive fingerprint, and the reason it is not mirrored in the
`license` and `credits` fields of `textures.json`.

